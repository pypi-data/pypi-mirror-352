#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publish script for PyLLM package.

This script helps with publishing the PyLLM package to PyPI or TestPyPI.
It handles authentication and package uploading.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def setup_pypirc(token, test=False):
    """Set up the .pypirc file with the provided token."""
    pypirc_path = os.path.expanduser("~/.pypirc")
    repository = "testpypi" if test else "pypi"
    repository_url = "https://test.pypi.org/legacy/" if test else "https://upload.pypi.org/legacy/"
    
    content = f"""[distutils]
index-servers =
    {repository}

[{repository}]
username = __token__
password = {token}
repository = {repository_url}
"""
    
    with open(pypirc_path, "w") as f:
        f.write(content)
    
    # Set appropriate permissions
    os.chmod(pypirc_path, 0o600)
    print(f"Created .pypirc file at {pypirc_path}")


def build_package():
    """Build the package using setuptools."""
    print("Building package...")
    subprocess.run([sys.executable, "setup.py", "sdist", "bdist_wheel"], check=True)
    print("Package built successfully.")


def check_package():
    """Check the package using twine."""
    print("Checking package...")
    result = subprocess.run(["twine", "check", "dist/*"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Package check failed:")
        print(result.stderr)
        return False
    print("Package check passed.")
    return True


def upload_package(test=False):
    """Upload the package to PyPI or TestPyPI."""
    repository = "--repository=testpypi" if test else ""
    print(f"Uploading package to {'TestPyPI' if test else 'PyPI'}...")
    cmd = ["twine", "upload"]
    if repository:
        cmd.append(repository)
    cmd.append("dist/*")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Upload failed:")
        print(result.stderr)
        return False
    print("Upload successful.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Publish PyLLM package to PyPI or TestPyPI")
    parser.add_argument("--token", help="PyPI or TestPyPI API token")
    parser.add_argument("--test", action="store_true", help="Publish to TestPyPI instead of PyPI")
    parser.add_argument("--skip-build", action="store_true", help="Skip building the package")
    
    args = parser.parse_args()
    
    # Change to the project directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    
    # Set up .pypirc if token is provided
    if args.token:
        setup_pypirc(args.token, args.test)
    
    # Build the package
    if not args.skip_build:
        build_package()
    
    # Check the package
    if not check_package():
        sys.exit(1)
    
    # Upload the package
    if not upload_package(args.test):
        sys.exit(1)
    
    print(f"PyLLM package published to {'TestPyPI' if args.test else 'PyPI'} successfully.")


if __name__ == "__main__":
    main()
