import requests
import subprocess
import sys
import os

from packaging import version

from lumeo import __version__, dist_name

def check_for_update():
    """
    Check if a new version of the package is available on PyPI.
    
    Returns:
        tuple: (bool, str) A tuple containing a boolean indicating if an update is available,
                and a string with the latest version number.
    """
    try:
        # Get the latest version from PyPI
        response = requests.get(f"https://pypi.org/pypi/{dist_name}/json")
        latest_version = version.parse(response.json()["info"]["version"])
        
        # Compare with the current version
        current_version = version.parse(__version__)
        
        if latest_version > current_version:
            return True, str(latest_version), f"{current_version} (Newer version available: {latest_version})"
        else:
            return False, str(current_version), f"{current_version} (Latest version)"
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return False, __version__, f"Error checking for updates: {e}"


def self_update():
    """
    Update the package to the latest version using the same installation method.
    """

    def run_command(cmd):
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            sys.exit(1)

    update_available, latest_version, _ = check_for_update()
    
    if not update_available:
        print(f"You are already using the latest version ({__version__}).")
        return

    print(f"Updating {dist_name} to version {latest_version}...")

    # Check if running in a virtual environment
    in_venv = sys.prefix != sys.base_prefix

    # Check if installed via pipx
    is_pipx = "PIPX_HOME" in os.environ or "PIPX_LOCAL_VENVS" in os.environ

    if is_pipx:
        run_command(f"pipx upgrade {dist_name}")
    elif in_venv:
        run_command(f"pip install --upgrade {dist_name}")
    else:
        # If not in a venv and not installed via pipx, use pip with the --user flag
        run_command(f"pip install --user --upgrade {dist_name}")

    print(f"Successfully updated {dist_name} to version {latest_version}.")