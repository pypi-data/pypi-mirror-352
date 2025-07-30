import argparse
import asyncio
import json
import logging
from typing import List, Dict
import re
from datetime import datetime
import signal

from lumeo.api import LumeoApiClient
from lumeo.scripts.bulk_deploy.bulk_deploy import BulkDeployer


async def stop_running_deployments(api_client: LumeoApiClient, gateway_id: str):
    running_deployments = await api_client.get_deployments(gateway_id, state="running")
    for deployment in running_deployments:
        await api_client.set_deployment_state(deployment['id'], "stop")
    logging.info(
        f"Stopped {len(running_deployments)} running deployments on gateway {gateway_id}")


async def create_deployment(bulk_deployer: BulkDeployer, gateway_id: str, pipeline_id: str, stream_id: str, deployment_config: Dict, deployment_prefix: str):
    args = argparse.Namespace(
        gateway_id=gateway_id,
        pipeline_id=pipeline_id,
        stream_id=stream_id,
        deployment_config=deployment_config,
        app_id=bulk_deployer._args.app_id,
        token=bulk_deployer._args.token,
        deployment_prefix=deployment_prefix
    )
    tasks = await bulk_deployer._process_existing_live_stream(args, bulk_deployer._api_client, bulk_deployer._queuing_lock)
    results = await bulk_deployer._process_tasks(tasks)
    if results and results[0][0]:
        logging.info(f"Successfully created deployment for stream {stream_id}. Waiting for it to start...")
        return True, results[0][1]
    else:
        logging.error(f"Failed to create deployment for stream {stream_id}")
        return False, None


async def wait_for_deployment_running(api_client: LumeoApiClient, deployment_id: str):
    while True:
        deployment = await api_client.get_deployment(deployment_id)
        if deployment['state'] == 'running':
            logging.info(f"Deployment {deployment_id} is now running")
            return
        logging.info(f"Deployment {deployment_id} is {deployment['state']}. Waiting till it is running...")
        await asyncio.sleep(5)

async def run_command(host: str, command: str, context_str: str):
    if host == 'localhost':
        command = command
    else:
        command = f"ssh {host} '{command}'"
    
    if not context_str:
        context_str = command

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        logging.error(f"Error executing {context_str} command: {stderr.decode()}")
        return None
    
    return stdout.decode().strip()


async def check_utilization_dgpu(gateway_host: str):
    command = "top -bn1 | grep \"Cpu(s)\" && nvidia-smi --query-gpu=utilization.gpu,memory.total,memory.used --format=csv,noheader,nounits && free -m | grep Mem"

    try:
        output = await run_command(gateway_host, command, "check_utilization_dgpu")
        if not output:
            return None        
        output = output.split('\n')

        # Parse CPU usage
        cpu_usage = 100 - float(output[0].split(',')[3].split()[0])

        # Parse GPU usage and memory
        gpu_data = output[1:-1]  # Exclude the last line which is CPU memory
        gpu_usage_sum = 0
        gpu_memory_percentage_sum = 0
        gpu_count = len(gpu_data)

        for gpu in gpu_data:
            gpu_info = gpu.split(', ')
            gpu_usage_sum += float(gpu_info[0])
            gpu_total_memory = float(gpu_info[1])
            gpu_used_memory = float(gpu_info[2])
            gpu_memory_percentage_sum += (gpu_used_memory / gpu_total_memory) * 100

        avg_gpu_usage = gpu_usage_sum / gpu_count if gpu_count > 0 else 0
        avg_gpu_memory_percentage = gpu_memory_percentage_sum / gpu_count if gpu_count > 0 else 0

        # Parse CPU memory
        mem_data = output[-1].split()
        total_mem = float(mem_data[1])
        used_mem = float(mem_data[2])
        cpu_memory = (used_mem / total_mem) * 100

        return {
            'cpu_usage': cpu_usage,
            'gpu_usage': avg_gpu_usage,
            'cpu_memory': cpu_memory,
            'gpu_memory': avg_gpu_memory_percentage
        }
    except Exception as e:
        logging.error(f"Error checking utilization dgpu: {str(e)}")
        return None


async def check_utilization_jetson(gateway_host: str):
    try:
        command = "top -bn1 | grep \"Cpu(s)\" && free -m | grep Mem"
        output = await run_command(gateway_host, command, "check_utilization_jetson_cpu")
        if not output:
            return None
        
        output = output.split('\n')
        cpu_usage = 100 - float(output[0].split(',')[3].split()[0]) 
        
        mem_data = output[1].split()
        total_mem = float(mem_data[1])
        used_mem = float(mem_data[2])
        cpu_memory = (used_mem / total_mem) * 100
                
        command = "tegrastats --interval 1 | head -n 1"
        output = await run_command(gateway_host, command, "check_utilization_jetson_gpu")
        if not output:
            return None
        
        gpu_percent_used = float(re.search(r'GR3D_FREQ\s+(\d+)%', output).group(1))
        
        return {
            'cpu_usage': cpu_usage,
            'gpu_usage': gpu_percent_used,
            'cpu_memory': cpu_memory,
            'gpu_memory': cpu_memory
        }
    except Exception as e:
        logging.error(f"Error checking utilization jetson: {str(e)}")
        return None

async def get_gateway_specs(gateway_host: str):

    gateway_type_command = "cat /proc/device-tree/model 2>/dev/null || echo 'dgpu'"
    output = await run_command(gateway_host, gateway_type_command, "get_gateway_type")
    if not output or output.strip() == 'dgpu':
        gateway_type = "dgpu"
    else:
        gateway_type = output.strip().rstrip('\x00')

    if gateway_type == "dgpu":
        command = """
            echo "CPU:" && lscpu | grep "Model name\\|CPU(s):" && 
            echo "Memory:" && free -h | grep Mem && 
            echo "GPU:" && nvidia-smi --query-gpu=gpu_name,memory.total,count --format=csv,noheader
        """
    else:
        command = """
            echo "CPU:" && lscpu | grep "Model name\\|CPU(s):" && 
            echo "Memory:" && free -h | grep Mem &&
            nvpmodel -q | grep "NV Power Mode"
        """

    try:
        output = await run_command(gateway_host, command, "get_gateway_specs")
        if not output:
            return None    
        
        # Parse the output and convert to structured JSON
        specs = {
            'gateway_type': gateway_type,
            'cpu': {},
            'memory': {},
            'gpu': []
        }
        current_section = None
        for line in output.split('\n'):
            if line.startswith('CPU:'):
                current_section = 'cpu'
                specs['cpu'] = {}
            elif line.startswith('Memory:'):
                current_section = 'memory'
                specs['memory'] = {}
            elif line.startswith('GPU:'):
                current_section = 'gpu'
                specs['gpu'] = []
            elif line.startswith('NV Power Mode:'):
                key, value = line.split(':', 1)
                specs['cpu'][key.strip()] = value.strip()
            elif current_section == 'cpu':
                key, value = line.split(':', 1)
                specs['cpu'][key.strip()] = value.strip()
            elif current_section == 'memory':
                parts = line.split()
                specs['memory'] = {
                    'total': parts[1],
                    'used': parts[2],
                    'free': parts[3],
                    'shared': parts[4],
                    'buff/cache': parts[5],
                    'available': parts[6]
                }
            elif current_section == 'gpu':
                gpu_info = line.split(', ')
                specs['gpu'].append({
                    'name': gpu_info[0],
                    'memory': gpu_info[1],
                    'count': int(gpu_info[2])
                })
        
        if gateway_type != "dgpu":
            specs['gpu'] = [
                {
                    'name': gateway_type,
                    'memory': specs['memory']['total'],
                    'count': 1
                }
            ]
        
        return specs
    except Exception as e:
        logging.error(f"Error getting gateway specs: {str(e)}")
        return None



async def load_test(app_id: str, token: str, gateway_id: str, gateway_host: str, pipeline_ids: List[str], stream_ids: List[str],
                    deployment_config: Dict, deployment_prefix: str, threshold: float, deployment_buffer: int, cleanup: bool):
    api_client = LumeoApiClient(app_id, token)
    bulk_deployer = BulkDeployer(api_client=api_client, args=argparse.Namespace(app_id=app_id,
                                                                                token=token,
                                                                                batch_size=1))

    # Fetch and log stream names and gateway name
    stream_names = []
    for stream_id in stream_ids:
        stream = await api_client.get_stream_with_id(stream_id)
        stream_names.append(stream.get('name', 'Unknown Stream'))

    gateway = await api_client.get_gateway(gateway_id)
    gateway_name = gateway.get('name', 'Unknown Gateway')

    logging.info(f"Starting load test with:")
    logging.info(f"Streams: {', '.join(stream_names)} (IDs: {', '.join(stream_ids)})")
    logging.info(f"Gateway: {gateway_name} (ID: {gateway_id})")

    gateway_specs = await get_gateway_specs(gateway_host)

    results = {
        'timestamp': datetime.now().isoformat(),
        'configuration': {
            'gateway': {'name': gateway_name, 'id': gateway_id},
            'streams': [{'name': name, 'id': id} for name, id in zip(stream_names, stream_ids)],
            'pipelines': []
        },
        'threshold': threshold,
        'gateway_specs': gateway_specs,
        'deployments': [],
        'summary': []
    }
    
    await stop_running_deployments(api_client, gateway_id)

    # Create an event to signal task termination
    terminate_event = asyncio.Event()

    # Create a task to handle the cleanup
    cleanup_task = None

    def signal_handler(sig, frame):
        logging.info("Interrupt received, waiting for running tasks to complete...")
        terminate_event.set()
        nonlocal cleanup_task
        if cleanup_task is None:
            cleanup_task = asyncio.create_task(cleanup_and_save(api_client, gateway_id, deployments, results, deployment_prefix, gateway_name, cleanup))
        
    signal.signal(signal.SIGINT, signal_handler)

    deployments = []
    try:
        for pipeline_id in pipeline_ids:
            pipeline = await api_client.get_pipeline(pipeline_id)
            pipeline_name = pipeline.get('name', 'Unknown Pipeline')
            
            logging.info(f"Starting load test for pipeline: {pipeline_name} (ID: {pipeline_id})")
            
            results['configuration']['pipelines'].append({'name': pipeline_name, 'id': pipeline_id})
            
            deployments.clear()
            stream_index = 0
            threshold_exceeded = False
            deployment_idx = 0

            while not threshold_exceeded:
                if terminate_event.is_set():
                    logging.info("Termination signal received. Stopping load test.")
                    break

                stream_id = stream_ids[stream_index]
                current_prefix = f"{deployment_prefix}-{pipeline_name}-{deployment_idx}-"
                success, deployment_id = await create_deployment(bulk_deployer, gateway_id, pipeline_id, stream_id, deployment_config, current_prefix)
                if not success:
                    stream_index = (stream_index + 1) % len(stream_ids)
                    continue

                await wait_for_deployment_running(api_client, deployment_id)
                deployments.append(deployment_id)

                logging.info(f"Waiting for 5 seconds before checking utilization...")
                await asyncio.sleep(5)

                logging.info(f"Checking utilization for gateway {gateway_host}")
                utilization_samples = []
                for _ in range(deployment_buffer):
                    if terminate_event.is_set():
                        break
                    if gateway_specs['gateway_type'] == "dgpu":
                        utilization = await check_utilization_dgpu(gateway_host)
                    else:
                        utilization = await check_utilization_jetson(gateway_host)
                    if utilization:
                        utilization_samples.append(utilization) 
                        logging.info(f"Current utilization: {utilization}")
                    await asyncio.sleep(1)

                if utilization_samples:
                    avg_utilization = {
                        key: sum(sample[key] for sample in utilization_samples) / len(utilization_samples)
                        for key in utilization_samples[0]
                    }
                    logging.info(f"Average utilization: {avg_utilization}")

                    results['deployments'].append({
                        'deployment_id': deployment_id,
                        'pipeline_name': pipeline_name,
                        'avg_utilization': avg_utilization
                    })

                    if any(value >= threshold for value in avg_utilization.values()):
                        logging.info(f"Threshold {threshold} reached or exceeded. Stopping load test for this pipeline.")
                        threshold_exceeded = True
                    else:
                        stream_index = (stream_index + 1) % len(stream_ids)
                        deployment_idx += 1
                else:
                    logging.warning("Failed to collect any utilization samples.")
                    stream_index = (stream_index + 1) % len(stream_ids)
                    deployment_idx += 1

            logging.info(f"Load test completed for pipeline {pipeline_name}. Total deployments: {len(deployments)}")
            logging.info(f"Deployment IDs: {deployments}")

            results['summary'].append({
                'pipeline_name': pipeline_name,
                'pipeline_id': pipeline_id,
                'max_deployments': len(deployments),
                'utilization_at_max': results['deployments'][-1]['avg_utilization'] if results['deployments'] else None
            })

            if cleanup:
                await stop_running_deployments(api_client, gateway_id)
                for deployment_id in deployments:
                    await api_client.delete_deployment(deployment_id)
                    logging.info(f"Deleted deployment {deployment_id}")
                logging.info(f"Cleanup completed for pipeline {pipeline_name}. Stopped & deleted {len(deployments)} deployments on gateway {gateway_id}")

        if cleanup_task is None:
            await cleanup_and_save(api_client, gateway_id, deployments, results, deployment_prefix, gateway_name, cleanup)
        else:
            await cleanup_task

    except Exception as e:
        logging.error(f"An error occurred during the load test: {str(e)}")
        if cleanup_task is None:
            await cleanup_and_save(api_client, gateway_id, deployments, results, deployment_prefix, gateway_name, cleanup)
        else:
            await cleanup_task

    return


async def cleanup_and_save(api_client, gateway_id, deployments, results, deployment_prefix, gateway_name, cleanup):
    if cleanup:
        await stop_running_deployments(api_client, gateway_id)
        for deployment_id in deployments:
            await api_client.delete_deployment(deployment_id)
            logging.info(f"Deleted deployment {deployment_id}")
        logging.info(f"Final cleanup completed. Stopped & deleted any remaining deployments on gateway {gateway_id}")

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{deployment_prefix}-{gateway_name}-{timestamp}.json".replace(" ", "_")
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    logging.info(f"Results saved to {filename}")


def run_main():
    parser = argparse.ArgumentParser(description="Load test for Lumeo deployments", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--app_id", required=True, help="Lumeo Workspace/Application ID")
    parser.add_argument("--token", required=True, help="Lumeo Workspace/Application token")
    parser.add_argument("--gateway_id", required=True, help="Gateway ID")
    parser.add_argument("--gateway_host", required=True, help="Gateway host for SSH connection, to measure utilization. Should be in the format user@host, and allow passwordless login or 'localhost' for local execution")
    parser.add_argument("--pipeline_ids", required=True, help="List of Pipeline IDs to deploy, separated by commas")
    parser.add_argument("--stream_ids", required=True, help="List of stream IDs to deploy pipeline with, separated by commas")
    parser.add_argument("--deployment_config", type=json.loads, default={}, help="Deployment configuration as JSON")
    parser.add_argument("--deployment_prefix", type=str, default="load-test", help="Prefix for the deployment name")
    parser.add_argument("--threshold", type=float, default=90.0, help="Utilization threshold (0-100)")
    parser.add_argument("--deployment_buffer", type=int, default=10, help="Gap between deployments in seconds")
    parser.add_argument("--no-cleanup", action="store_true", help="Skip cleanup of deployments after load test")

    args = parser.parse_args()
    stream_ids = args.stream_ids.split(',')
    pipeline_ids = args.pipeline_ids.split(',')
    asyncio.run(load_test(args.app_id, args.token, args.gateway_id, args.gateway_host, pipeline_ids,
                          stream_ids, args.deployment_config, args.deployment_prefix,
                          args.threshold, args.deployment_buffer, not args.no_cleanup))
