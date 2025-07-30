import os
import sys
import importlib
import subprocess
import site

from distutils.version import LooseVersion

from .log_events import error_log, debug_log_if

def run_command(command, cwd=None, context='', node_id="", show_debug_log=False):
    """
    Run a shell command inside the Gateway container and log the output or error.
    Only available in Lumeo Custom Function node (https://docs.lumeo.com/docs/custom-function-node).

    Args:
        command (str): The command to run.
        cwd (str, optional): The working directory to run the command in. Default is None.
        context (str, optional): The context or description of the command being run. Default is an empty string.
        node_id (str, optional): The ID of the node. Default is an empty string.
        show_debug_log (bool, optional): Whether to show debug logs. Default is False.

    Returns:
        None
    """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    output, error = process.communicate()

    if process.returncode != 0:
        error_log(f"Error occurred while {context}: {command} : {error.decode('utf-8')}")
    else:
        debug_log_if(f"Output: {output.decode('utf-8')}", node_id, show_debug_log)


def __get_python_package_installed_version__(package_name):
    try:
        # Run the pip show command to get package information
        cmd = f"pip3 show {package_name}"
        cmd_result = os.popen(cmd).read()

        # Check if the command was successful
        if cmd_result:
            # Iterate through the lines of the command output
            for line in cmd_result.splitlines():
                # Search for the 'Version:' line
                if line.startswith('Version:'):
                    # Extract the version number
                    version_parts = line.split('Version:')
                    if len(version_parts) > 1:
                        return version_parts[1].strip()

        # If the command was not successful or the package metadata does not include Version, print an error message and return None
        print(
            f"install_import info: package '{package_name}' wasn't previously installed or the version is not present in 'pip3 show' metadata.")
        return None
    except Exception as error:
        print(
            f"install_import error: Exception while trying to verify the version of '{package_name}' using 'pip3 show': {error}")
        return None


def __install_with_pip__(package_name=None, version=None, git_url=None, pypi_url=None, extras=""):
    # Extract the parent module if dot notation was used
    parent_module = package_name.split('.')[0]

    if pypi_url:
        return f"pip3 install --user --index-url {pypi_url} {parent_module}{extras}=={version}" if version else f"pip3 install --user --index-url {pypi_url} {parent_module}{extras}"
    elif git_url:
        return f"pip3 install --user git+{git_url}#egg={parent_module}{extras}=={version}" if version else f"pip3 install --user git+{git_url}#egg={parent_module}{extras}"
    else:
        return f"pip3 install --user {parent_module}{extras}=={version}" if version else f"pip3 install --user {parent_module}{extras}"


def __install_and_import_package__(package_name, version, git_url, pypi_url, target, extras=""):
    cmd = __install_with_pip__(package_name, version, git_url, pypi_url, extras)
    os.system(cmd)

    # If you are dynamically importing a module that was created since the interpreter began execution
    # you may need to call invalidate_caches() in order for the new module to be noticed by the import system.
    importlib.invalidate_caches()

    return importlib.import_module(target)


def install_import(package_name=None, attribute_name=None, module_name=None, version=None, git_url=None,
                    pypi_url=None):
    """
    Allow users to install and import additional python modules on devices.

    Usage:
        - import module with dot notation:
          pytz_ref = install_import('pytz.reference')

        - import attribute from module:
          sleep = install_import('time', 'sleep')

        - import a module which has a different name from the package it belongs
          box = install_import('python-box', module_name='box')

        - install a specific version
          jwt = install_import('PyJWT', module_name='jwt', version='1.5.3')

        - install from a private PyPI repository
          custom_module = install_import('custom_module', pypi_url='http://your_private_pypi.com')

        - install from a GitHub repository
          github_module = install_import('github_module', git_url='https://github.com/username/repo.git')

        - install package with extra requires:
          tritonclient = install_import("tritonclient[http,cuda]", version="2.33.0")

    Args:
        package_name (str, optional): The name of the package to install and import.
        attribute_name (str, optional): The attribute to import from the module.
        module_name (str, optional): The name of the module to import.
        version (str, optional): The version of the package to install.
        git_url (str, optional): The GitHub URL to install the package from.
        pypi_url (str, optional): The PyPI URL to install the package from.

    Returns:
        module or attribute: The imported module or attribute.
    """
    if package_name:
        # Parse package name and [extras_require]
        if '[' in package_name and ']' in package_name:
            package_name, extras = package_name.split('[', 1)
            extras = f"[{extras.rstrip(']').replace(' ', '')}]"
        else:
            extras = ""

        target = module_name or package_name

        if site.USER_SITE not in sys.path:
            sys.path.insert(0, site.USER_SITE)

        try:
            if version:
                # Check the installed version if a specific version is provided
                installed_version = __get_python_package_installed_version__(package_name)

                # TODO:  In Python 3.6, the packaging module is available, but it's not included in the standard library.
                #        Starting from Python 3.8, the packaging module is included in the standard library.
                #        Once we deprecate Python 3.6 replace "from distutils.version import LooseVersion" by
                #        "from packaging.version import Version as LooseVersion"
                if installed_version and LooseVersion(installed_version) != LooseVersion(version):
                    # The correct version is not installed, so we will try to install it
                    loaded_module = __install_and_import_package__(package_name, version, git_url, pypi_url,
                                                                          target, extras)
                    return getattr(loaded_module, attribute_name) if attribute_name else loaded_module

            loaded_module = importlib.import_module(target)

        except ImportError:
            # Initial import failed, proceed with installation
            loaded_module = __install_and_import_package__(package_name, version, git_url, pypi_url, target, extras)

        return getattr(loaded_module, attribute_name) if attribute_name else loaded_module