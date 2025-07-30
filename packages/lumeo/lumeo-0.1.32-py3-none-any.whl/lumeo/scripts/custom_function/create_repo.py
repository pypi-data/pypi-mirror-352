import os
import argparse
import sys

def create_package_structure(package_name, author, email, description):
    
    # Convert package name to Python package name format
    package_name = package_name.lower().replace('-', '_').replace(' ', '_')
    
    # Validate package name
    if not package_name.isidentifier():
        raise ValueError("Invalid package name. Please use only letters, numbers, and underscores, and start with a letter or underscore.")
    
    # Create main directory to hold the package and git repository
    os.makedirs(package_name)

    # Create setup.py
    setup_py = f"""
from setuptools import setup, find_packages

setup(
    name='{package_name}',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # List your runtime dependencies here
    ],
    extras_require={{
        'tests': [
            'pytest',
        ],
    }},
    author='{author}',
    author_email='{email}',
    description='{description}',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
"""
    with open(os.path.join(package_name, 'setup.py'), 'w') as f:
        f.write(setup_py)

    # Create package directory
    os.makedirs(os.path.join(package_name, package_name))

    # Create __init__.py
    with open(os.path.join(package_name, package_name, '__init__.py'), 'w') as f:
        f.write("# Package initialization\n")

    # Create dummy module (similar to display.py)
    dummy_module = """
from lumeopipeline import VideoFrame
import cv2

frame_count = 0

def process_frame(frame: VideoFrame, **kwargs) -> bool:
    global frame_count
    frame_count += 1

    with frame.data() as mat:
        cv2.putText(mat, f"Frame {frame_count}", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 255), 1)

    return True
"""
    with open(os.path.join(package_name, package_name, 'sample_module.py'), 'w') as f:
        f.write(dummy_module)

    # Create tests directory
    os.makedirs(os.path.join(package_name, 'tests'))

    # Create __init__.py in tests directory
    with open(os.path.join(package_name, 'tests', '__init__.py'), 'w') as f:
        f.write("import pytest\n")


    readme_md = f"""
# Overview

This repository contains Lumeo Custom Functions, to be used in Lumeo's [custom function node](https://docs.lumeo.com/docs/custom-function-node).

# How to use

1. Add or replace my_module.py with your custom code. You can add other modules to the package if you want.

2. Create a new git repository inside the top level {package_name} folder. Publish the package to a git repository. 
Replace the 'url' in setup.py with the URL to your git repository.

3. Using the `Utils.install_import` method in a Lumeo custom function node.

You can install this package in a Lumeo custom function node, and call it's functions using the following code snippet. If it's a public git repo, skip the token, otherwise use a read-only [personal access token](https://github.com/settings/tokens) with the `repo` scope.

> Important: The version number must match the version number in the `setup.py` file. When you make changes to the package, 
> you must also update the package version and specify it in the `Utils.install_import` method, even if you specify a git 
> branch or tag in the `git_url` parameter.
> This is required since Lumeo will not re-download the package if the specified version already exists in the container.

```python
from lumeopipeline import VideoFrame, Utils

Utils.install_import('{package_name}', 
                     version='0.1.0',
                     git_url='https://<token>@github.com/<username>/<repo>.git')
from {package_name} import sample_module

def process_frame(frame: VideoFrame, **kwargs):
    return sample_module.process_frame(frame, **kwargs)
```

4. Alternatively to #3, you can also use the `Custom Function Repo` node in Lumeo, and configure it with the git URL to your repository.
"""

    with open(os.path.join(package_name, 'README.md'), 'w') as f:
        f.write(readme_md)

    print(f"Package '{package_name}' structure created successfully. Check the README.md file for instructions on how to use it.")


def main():
    parser = argparse.ArgumentParser(description="Create a basic Python package structure to host Lumeo Custom Functions.")
    parser.add_argument("package_name", nargs='?', help="Name of the package")
    parser.add_argument("--author", default="Your Name", help="Author's name")
    parser.add_argument("--email", default="your.email@example.com", help="Author's email")
    parser.add_argument("--description", default="A Python package that contains Lumeo Custom Functions", 
                       help="Short description of the package")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    create_package_structure(args.package_name, args.author, args.email, args.description)


if __name__ == "__main__":
    main()

