"""
# Connects to all gateways in the JSON file over SSH.
# Runs the specified command inside the gateway container for each combination of gateway and model in the config.
# MODEL_ID argument is replaced with the actual model ID from the config file.
#
# Examples:
# $ pipx run --spec . --no-cache lumeo-model-management config.json engine-cache list --model-id MODEL_ID
# $ pipx run --spec . --no-cache lumeo-model-management config.json engine-cache create --model-id MODEL_ID
# $ pipx run --spec . --no-cache lumeo-model-management config.json engine-cache create --model-id MODEL_ID --force
#
# JSON format:
# {
#   "gateways": [
#     {
#       "ssh": "root@gateway_host",
#       "container_name": "lumeo-gateway-container"
#     }
#   ],
#   "models": [
#     {
#       "id": "00000000-0000-0000-0000-000000000000"
#     }
#   ]
# }
#
# DESIGN: Status Table Printing
#
# The status table will be printed to the console using the 'tabulate' library, but no more frequently than every 5 seconds.
# - Does not clear the console; each table print is appended, allowing scrollback to grow, but it is more reliable than live-updating UIs.
#
# Thread separation:
# - Worker threads process tasks and report status updates to the main thread.
# - The main thread maintains the authoritative list of all task statuses.
# - The main thread is responsible for printing the status table to the console, with rate limiting (e.g., no more than once every 5 seconds).
# - On shutdown, the main thread always prints the final table.
#
# Output responsibilities:
# - The main thread is the only component that prints directly to the console.
# - Each worker writes only to its own log file and does not print to the console.
"""

import argparse
import getpass
import json
import requests
import subprocess
import concurrent.futures
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from queue import Queue, Empty
from tabulate import tabulate
import time

STATUS_WAITING = "Waiting..."
STATUS_IN_PROGRESS = "In progress..."
STATUS_SUCCESS = "OK"
STATUS_ERROR = "Error"

# Global flag to control execution
is_running = True


@dataclass
class TaskStatus:
    gateway_ssh: str
    model_id: str
    log_file: str
    status: str = STATUS_WAITING
    result: Optional[str] = None
    error: Optional[str] = None

    def update_status(
        self, status: str, result: Optional[str] = None, error: Optional[str] = None
    ):
        self.status = status
        self.result = result
        self.error = error


def get_log_file_path(gateway_ssh: str, model_id: str) -> str:
    """Generate a log file path for a specific gateway and model combination."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gateway_name = (
        "local"
        if gateway_ssh == "local"
        else gateway_ssh.split("@")[1].replace(".", "_")
    )
    log_dir = "model_management_logs"
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, f"{gateway_name}_{model_id}_{timestamp}.log")


def log_to_file(log_file: str, message: str) -> None:
    """Write a message to the log file."""
    with open(log_file, "a") as f:
        f.write(f"{message}\n")


def print_status_table(tasks):
    headers = ["Status", "Gateway", "Model ID", "Log File"]
    rows = [
        [t.status, t.gateway_ssh, t.model_id, f"less -R {t.log_file}"]
        for t in tasks
    ]
    print(f"\nStatus Table ({time.strftime('%Y-%m-%d %H:%M:%S')})")
    print(tabulate(rows, headers=headers, tablefmt="fancy_outline"))


def concatenate_error_logs(tasks):
    error_logs = [t.log_file for t in tasks if t.status == STATUS_ERROR]

    if not error_logs:
        return

    with open("model_management_logs/error_logs.txt", "w") as f:
        for log in error_logs:
            f.write(f"\n\n===== {log} =====\n")
            with open(log, "r") as f2:
                f.write(f2.read())

    print(f"\nSee error logs: less -R model_management_logs/error_logs.txt")


def main():
    global is_running
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="JSON file with gateways and models")
    parser.add_argument("command", help="Command to execute (e.g., engine-cache)")
    parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Additional arguments for the command"
    )
    args = parser.parse_args()

    try:
        with open(args.config) as f:
            config = json.load(f)

        environment, api_token = login()
        if not environment or not api_token:
            return

        # Create task status objects and log files dictionary in one pass
        tasks = []
        model_log_files = {}
        for gateway in config["gateways"]:
            for model in config["models"]:
                log_file = get_log_file_path(gateway["ssh"], model["id"])
                tasks.append(TaskStatus(gateway["ssh"], model["id"], log_file))
                model_log_files[(gateway["ssh"], model["id"])] = log_file

        update_queue = Queue()

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        process_gateway,
                        gateway,
                        config["models"],
                        environment,
                        api_token,
                        [args.command] + args.args,
                        update_queue,
                        model_log_files,
                    )
                    for gateway in config["gateways"]
                ]

                print_status_table(tasks)
                last_print_time = time.time()

                while futures and is_running:
                    try:
                        gateway_ssh, model_id, status = update_queue.get(timeout=0.5)
                        task = next(
                            t
                            for t in tasks
                            if t.gateway_ssh == gateway_ssh and t.model_id == model_id
                        )
                        task.update_status(status)

                        now = time.time()
                        if now - last_print_time >= 5:
                            print_status_table(tasks)
                            last_print_time = now
                    except Empty:
                        futures = [f for f in futures if not f.done()]

        except KeyboardInterrupt:
            print("\nInterrupted by user. Shutting down ...")
            is_running = False
            for future in futures:
                future.cancel()
            concurrent.futures.wait(futures)
            for task in tasks:
                if task.status == STATUS_IN_PROGRESS:
                    task.update_status(
                        STATUS_ERROR, error="Operation interrupted by user"
                    )
                    log_to_file(task.log_file, "Operation interrupted by user")
        finally:
            print_status_table(tasks)
            concatenate_error_logs(tasks)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


def process_gateway(
    gateway: Dict[str, str],
    models: List[Dict[str, str]],
    environment: str,
    api_token: str,
    command: List[str],
    update_queue: Queue,
    model_log_files: Dict[Tuple[str, str], str],
) -> None:
    """Process a single gateway with all its models."""
    docker_base = [
        "docker",
        "exec",
        "--env",
        f"LUMEO_ENVIRONMENT={environment}",
        "--env",
        f"LUMEO_API_KEY={api_token}",
        "--env",
        "RUST_LOG=info",
        gateway["container_name"],
        "lumeod",
    ]

    if gateway["ssh"] != "local":
        docker_base = ["ssh", gateway["ssh"]] + docker_base

    for model in models:
        if not is_running:
            return

        log_file = model_log_files[(gateway["ssh"], model["id"])]
        log_to_file(
            log_file,
            f"###\n### Running command on {gateway['ssh']}. Model ID: {model['id']}\n###",
        )

        try:
            # Print lumeod version
            update_queue.put((gateway["ssh"], model["id"], STATUS_IN_PROGRESS))
            version_cmd = docker_base + ["--version"]
            result = subprocess.run(
                version_cmd, check=True, capture_output=True, text=True
            )
            log_to_file(log_file, result.stdout)

            if not is_running:
                return

            # Run the model command
            model_cmd = (
                docker_base
                + ["model"]
                + [model["id"] if arg == "MODEL_ID" else arg for arg in command]
            )
            result = subprocess.run(
                model_cmd, check=True, capture_output=True, text=True
            )
            log_to_file(log_file, result.stdout)
            update_queue.put((gateway["ssh"], model["id"], STATUS_SUCCESS))

        except subprocess.CalledProcessError as e:
            log_to_file(log_file, f"Error: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}")
            update_queue.put((gateway["ssh"], model["id"], STATUS_ERROR))
        except Exception as e:
            log_to_file(log_file, f"Unexpected error: {e}")
            update_queue.put((gateway["ssh"], model["id"], STATUS_ERROR))


def login() -> Tuple[Optional[str], Optional[str]]:
    try:
        environment = input("Lumeo environment (d/s/p): ").lower().strip()

        environments = {
            "d": "development",
            "s": "staging",
            "p": "production",
        }

        if environment not in environments:
            print(f"Invalid environment: '{environment}'")
            return None, None

        environment = environments[environment]
        base_url = {
            "development": "https://api-dev.lumeo.com",
            "staging": "https://api-staging.lumeo.com",
            "production": "https://api.lumeo.com",
        }[environment]

        email = input("Email: ").strip()
        password = getpass.getpass("Password: ")

        response = requests.post(
            f"{base_url}/v1/internal/auth/login",
            json={"email": email, "password": password},
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code} {response.reason}")
            return None, None

        return environment, response.json()["token"]

    except KeyboardInterrupt:
        print("\nLogin interrupted by user.")
        return None, None
    except Exception as e:
        print(f"\nLogin error: {e}")
        return None, None


if __name__ == "__main__":
    exit(main())
