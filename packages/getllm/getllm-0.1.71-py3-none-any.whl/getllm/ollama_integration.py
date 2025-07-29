#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama Integration for PyLLM

This module provides integration with Ollama for high-quality code generation.
It handles model management, automatic installation, and fallback mechanisms.
"""

import os
import sys
import time
import json
import shutil
import logging
import platform
import subprocess
from threading import Thread
import threading
import requests
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Create .getllm directory if it doesn't exist
PACKAGE_DIR = os.path.join(os.path.expanduser('~'), '.getllm')
os.makedirs(PACKAGE_DIR, exist_ok=True)

# Configure logger for OllamaIntegration
logger = logging.getLogger('getllm.ollama')
logger.setLevel(logging.INFO)

# Create file handler for Ollama-specific logs
ollama_log_file = os.path.join(PACKAGE_DIR, 'getllm_ollama.log')
file_handler = logging.FileHandler(ollama_log_file)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logger.debug('OllamaIntegration initialized')


class ProgressSpinner:
    """A simple progress spinner for console output."""
    def __init__(self, message="Processing", delay=0.1):
        self.message = message
        self.delay = delay
        self.running = False
        self.spinner_thread = None
        self.spinner_chars = ['-', '\\', '|', '/']
        self.counter = 0
        self.start_time = 0
        
    def spin(self):
        while self.running:
            elapsed = time.time() - self.start_time
            sys.stderr.write(f"\r{self.message} {self.spinner_chars[self.counter % len(self.spinner_chars)]} ({elapsed:.1f}s) ")
            sys.stderr.flush()
            time.sleep(self.delay)
            self.counter += 1
        # Clear the line when done
        sys.stderr.write("\r" + " " * (len(self.message) + 20) + "\r")
        sys.stderr.flush()
            
    def start(self):
        self.running = True
        self.start_time = time.time()
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
        
    def stop(self):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join(timeout=1.0)


class OllamaIntegration:
    """Class for integrating with Ollama and managing LLM models."""

    def __init__(self, ollama_path: str = None, model: str = None):
        self.ollama_path = ollama_path or os.getenv('OLLAMA_PATH', 'ollama')
        # Set default model with fallbacks to ensure we use an available model
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3')
        self.fallback_models = os.getenv('OLLAMA_FALLBACK_MODELS', 'llama3,llama-2-7b-chat').split(',')
        self.ollama_process = None
        # Ollama API endpoints
        self.base_api_url = "http://localhost:11434/api"
        self.generate_api_url = f"{self.base_api_url}/generate"
        self.chat_api_url = f"{self.base_api_url}/chat"
        self.version_api_url = f"{self.base_api_url}/version"
        self.list_api_url = f"{self.base_api_url}/tags"
        # Track the last error that occurred
        self.last_error = None
        self.original_model_specified = model is not None
        # Check if Ollama is installed
        self.is_ollama_installed = self._check_ollama_installed()
        
    def _check_ollama_installed(self) -> bool:
        """Check if Ollama is installed on the system."""
        try:
            # Common installation paths for Ollama
            common_paths = [
                self.ollama_path,  # First try the path provided or default 'ollama'
                '/usr/local/bin/ollama',
                '/usr/bin/ollama',
                '/opt/homebrew/bin/ollama',  # Common on macOS
                os.path.expanduser('~/go/bin/ollama'),  # Common when installed from source
            ]
            
            # On Windows, add common Windows paths
            if os.name == 'nt':
                common_paths.extend([
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'ollama', 'ollama.exe'),
                    os.path.join(os.environ.get('PROGRAMFILES', ''), 'ollama', 'ollama.exe'),
                ])
            
            # Check each path directly
            for path in common_paths:
                if os.path.isfile(path) and os.access(path, os.X_OK):
                    logger.info(f"Ollama found at: {path}")
                    self.ollama_path = path
                    return True
            
            # If not found in common paths, try using which/where command
            if os.name == 'nt':  # Windows
                which_cmd = 'where'
            else:  # Unix/Linux/MacOS
                which_cmd = 'which'
                
            result = subprocess.run(
                [which_cmd, 'ollama'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]  # Take first result if multiple
                logger.info(f"Ollama found at: {path}")
                self.ollama_path = path
                return True
            else:
                logger.warning(f"Ollama not found in PATH. Command '{which_cmd} {self.ollama_path}' failed.")
                return False
        except Exception as e:
            logger.error(f"Error checking if Ollama is installed: {e}")
            return False

    def _install_ollama(self) -> bool:
        """Attempt to install Ollama based on user confirmation.
        
        Returns:
            bool: True if installation was successful, False otherwise.
        """
        try:
            print("\nOllama is not installed but required for this operation.")
            
            # Use questionary if available for better UX, otherwise fallback to input
            try:
                import questionary
                has_questionary = True
            except ImportError:
                has_questionary = False
            
            # Define installation options
            options = [
                {"name": "Install Ollama directly (recommended)", "value": "direct"},
                {"name": "Install Ollama using Docker", "value": "docker"},
                {"name": "Use bexy sandbox for testing", "value": "bexy"},
                {"name": "Manual installation (I'll install it myself)", "value": "manual"},
                {"name": "Continue in mock mode (no Ollama required)", "value": "mock"},
                {"name": "Cancel", "value": "cancel"}
            ]
            
            # Present installation options to the user
            if has_questionary:
                install_choice = questionary.select(
                    "How would you like to install Ollama?",
                    choices=[option["name"] for option in options],
                    use_shortcuts=True
                ).ask()
                
                # Map the selected name back to the value
                for option in options:
                    if option["name"] == install_choice:
                        install_choice = option["value"]
                        break
            else:
                print("Installation options:")
                for i, option in enumerate(options):
                    print(f"  {i+1}. {option['name']}")
                
                choice_input = input("Select an option (1-5): ").strip()
                try:
                    choice_idx = int(choice_input) - 1
                    if 0 <= choice_idx < len(options):
                        install_choice = options[choice_idx]["value"]
                    else:
                        install_choice = "cancel"
                except ValueError:
                    install_choice = "cancel"
            
            # Handle the user's choice
            if install_choice == "cancel":
                print("Installation cancelled.")
                print("If you want to continue without Ollama, use the --mock flag.")
                return False
            
            elif install_choice == "manual":
                print("\nPlease install Ollama manually from https://ollama.com")
                print("After installation, restart getllm to use Ollama.")
                print("If you want to continue without Ollama, use the --mock flag.")
                return False
            
            elif install_choice == "mock":
                print("\nContinuing in mock mode. No Ollama installation required.")
                # Set environment variable to indicate mock mode
                os.environ['GETLLM_MOCK_MODE'] = 'true'
                return False
            
            elif install_choice == "docker":
                return self._install_ollama_docker()
            
            elif install_choice == "bexy":
                return self._install_ollama_bexy()
            
            else:  # direct installation
                return self._install_ollama_direct()
                
        except Exception as e:
            logger.error(f"Error in Ollama installation menu: {e}")
            print(f"\n❌ Error during Ollama installation: {e}")
            print("Please install Ollama manually from https://ollama.com")
            print("If you want to continue without Ollama, use the --mock flag.")
            return False
    
    def _install_ollama_direct(self) -> bool:
        """Install Ollama directly using the official installation script.
        
        Returns:
            bool: True if installation was successful, False otherwise.
        """
        try:
            print("\nInstalling Ollama directly...")
            
            # Determine the installation command based on the OS
            if platform.system() == "Darwin":  # macOS
                install_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
            elif platform.system() == "Linux":
                install_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
            elif platform.system() == "Windows":
                print("Automatic installation on Windows is not supported.")
                print("Please download and install Ollama from https://ollama.com")
                return False
            else:
                print(f"Unsupported operating system: {platform.system()}")
                return False
                
            # Execute the installation command
            print(f"Running: {install_cmd}")
            result = subprocess.run(
                install_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                print("\n✅ Ollama installed successfully!")
                # Update the path and installation status
                self.is_ollama_installed = self._check_ollama_installed()
                return self.is_ollama_installed
            else:
                print(f"\n❌ Failed to install Ollama: {result.stderr}")
                print("Please install Ollama manually from https://ollama.com")
                print("If you want to continue without Ollama, use the --mock flag.")
                return False
                
        except Exception as e:
            logger.error(f"Error installing Ollama directly: {e}")
            print(f"\n❌ Error installing Ollama: {e}")
            print("Please install Ollama manually from https://ollama.com")
            print("If you want to continue without Ollama, use the --mock flag.")
            return False
    
    def _install_ollama_docker(self) -> bool:
        """Install and run Ollama using Docker.
        
        Returns:
            bool: True if installation was successful, False otherwise.
        """
        try:
            print("\nChecking if Docker is installed...")
            
            # Check if Docker is installed
            docker_check = subprocess.run(
                ["docker", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if docker_check.returncode != 0:
                print("❌ Docker is not installed or not in PATH.")
                print("Please install Docker first: https://docs.docker.com/get-docker/")
                print("If you want to continue without Ollama, use the --mock flag.")
                return False
            
            print(f"✅ Docker found: {docker_check.stdout.strip()}")
            
            # Pull and run the Ollama Docker container
            print("\nPulling the Ollama Docker image...")
            pull_cmd = subprocess.run(
                ["docker", "pull", "ollama/ollama:latest"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if pull_cmd.returncode != 0:
                print(f"❌ Failed to pull Ollama Docker image: {pull_cmd.stderr}")
                print("If you want to continue without Ollama, use the --mock flag.")
                return False
            
            print("✅ Ollama Docker image pulled successfully.")
            
            # Check if the container is already running
            check_running = subprocess.run(
                ["docker", "ps", "-q", "-f", "name=ollama"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if check_running.stdout.strip():
                print("✅ Ollama Docker container is already running.")
            else:
                # Check if the container exists but is stopped
                check_exists = subprocess.run(
                    ["docker", "ps", "-a", "-q", "-f", "name=ollama"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if check_exists.stdout.strip():
                    print("Starting existing Ollama Docker container...")
                    start_cmd = subprocess.run(
                        ["docker", "start", "ollama"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    if start_cmd.returncode != 0:
                        print(f"❌ Failed to start Ollama Docker container: {start_cmd.stderr}")
                        print("If you want to continue without Ollama, use the --mock flag.")
                        return False
                else:
                    print("Creating and starting Ollama Docker container...")
                    run_cmd = subprocess.run(
                        ["docker", "run", "-d", "--name", "ollama", "-p", "11434:11434", "ollama/ollama:latest"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    if run_cmd.returncode != 0:
                        print(f"❌ Failed to run Ollama Docker container: {run_cmd.stderr}")
                        print("If you want to continue without Ollama, use the --mock flag.")
                        return False
            
            print("\n✅ Ollama is now running in Docker!")
            print("The Ollama API is available at http://localhost:11434")
            
            # Wait a moment for the server to fully start
            print("Waiting for Ollama server to initialize...")
            time.sleep(2)
            
            # Update the status
            return self.check_server_running()
                
        except Exception as e:
            logger.error(f"Error installing Ollama with Docker: {e}")
            print(f"\n❌ Error setting up Ollama with Docker: {e}")
            print("Please install Ollama manually from https://ollama.com")
            print("If you want to continue without Ollama, use the --mock flag.")
            return False
    
    def _install_ollama_bexy(self) -> bool:
        """Set up and run Ollama in a bexy sandbox environment for testing.
        
        Returns:
            bool: True if bexy sandbox was set up successfully, False otherwise.
        """
        try:
            print("\nSetting up bexy sandbox for Ollama testing...")
            
            # Check if bexy is available in the project
            bexy_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "bexy")
            
            if not os.path.isdir(bexy_path):
                print("❌ bexy package not found at expected location.")
                print("Please make sure the bexy package is available at: {}".format(bexy_path))
                print("If you want to continue without Ollama, use the --mock flag.")
                return False
            
            print("✅ Found bexy package at: {}".format(bexy_path))
            
            # Create a virtual environment for bexy if it doesn't exist
            bexy_venv_path = os.path.join(bexy_path, "venv")
            if not os.path.isdir(bexy_venv_path):
                print("Creating virtual environment for bexy...")
                venv_cmd = subprocess.run(
                    [sys.executable, "-m", "venv", bexy_venv_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if venv_cmd.returncode != 0:
                    print(f"❌ Failed to create virtual environment: {venv_cmd.stderr}")
                    print("If you want to continue without Ollama, use the --mock flag.")
                    return False
                
                print("✅ Created virtual environment for bexy")
            else:
                print("✅ Using existing bexy virtual environment")
            
            # Determine the pip executable path based on the OS
            if os.name == "nt":  # Windows
                pip_path = os.path.join(bexy_venv_path, "Scripts", "pip")
            else:  # Unix/Linux/MacOS
                pip_path = os.path.join(bexy_venv_path, "bin", "pip")
            
            # Install bexy package in development mode
            print("Installing bexy package...")
            install_cmd = subprocess.run(
                [pip_path, "install", "-e", bexy_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=bexy_path
            )
            
            if install_cmd.returncode != 0:
                print(f"❌ Failed to install bexy package: {install_cmd.stderr}")
                print("If you want to continue without Ollama, use the --mock flag.")
                return False
            
            print("✅ Installed bexy package")
            
            # Install Ollama in the bexy sandbox
            print("Setting up Ollama in bexy sandbox...")
            
            # Determine the Python executable path based on the OS
            if os.name == "nt":  # Windows
                python_path = os.path.join(bexy_venv_path, "Scripts", "python")
            else:  # Unix/Linux/MacOS
                python_path = os.path.join(bexy_venv_path, "bin", "python")
            
            # Create a simple script to run Ollama in the bexy sandbox
            sandbox_script = os.path.join(bexy_path, "run_ollama_sandbox.py")
            
            with open(sandbox_script, 'w') as f:
                f.write("""
# Script to run Ollama in a bexy sandbox
from bexy import DockerSandbox

# Create a Docker sandbox for Ollama
sandbox = DockerSandbox(
    image="ollama/ollama:latest",
    ports={"11434": "11434"},
    detach=True,
    name="ollama-bexy-sandbox"
)

# Run the sandbox
print("Starting Ollama in bexy sandbox...")
result = sandbox.run("ollama serve")
print("Ollama is now running in bexy sandbox!")
print("The Ollama API is available at http://localhost:11434")
print("
To stop the sandbox later, run:
python -c "from bexy import DockerSandbox; DockerSandbox().stop('ollama-bexy-sandbox')"
""")
            
            # Create a custom model in Ollama
            print(f"Creating Ollama model: {model_id}")
            result = subprocess.run(
                [self.ollama_path, "create", model_id, "--from", model_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Failed to create model: {model_id}")
                print(result.stderr)
                
                # Check if the error is due to disk space
                if "no space left on device" in result.stderr.lower():
                    print("\nError: Not enough disk space to install the model.")
                    try:
                        import questionary
                        use_mock = questionary.confirm(
                            "Would you like to continue in mock mode instead?",
                            default=True
                        ).ask()
                        
                        if use_mock:
                            print("\nContinuing in mock mode (no model download required)...")
                            # Set environment variable for mock mode
                            os.environ['GETLLM_MOCK_MODE'] = 'True'
                            return True
                    except ImportError:
                        # If questionary is not available, ask with input
                        use_mock = input("Would you like to continue in mock mode instead? (Y/n): ").lower()
                        if not use_mock.startswith('n'):
                            print("\nContinuing in mock mode (no model download required)...")
                            # Set environment variable for mock mode
                            os.environ['GETLLM_MOCK_MODE'] = 'True'
                            return True
                return False
            
            print("\n✅ Ollama is now running in bexy sandbox!")
            print("The Ollama API is available at http://localhost:11434")
            
            # Run the sandbox script
            print("Starting Ollama in bexy sandbox...")
            run_cmd = subprocess.run(
                [python_path, sandbox_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=bexy_path
            )
            
            if run_cmd.returncode != 0:
                print(f"❌ Failed to start Ollama in bexy sandbox: {run_cmd.stderr}")
                print("If you want to continue without Ollama, use the --mock flag.")
                return False
            
            print("\n✅ Ollama is now running in bexy sandbox!")
            print("The Ollama API is available at http://localhost:11434")
            
            # Wait a moment for the server to fully start
            print("Waiting for Ollama server to initialize...")
            time.sleep(2)
            
            # Update the status
            return self.check_server_running()
                
        except Exception as e:
            logger.error(f"Error setting up bexy sandbox for Ollama: {e}")
            print(f"\n❌ Error setting up bexy sandbox: {e}")
            print("Please install Ollama manually from https://ollama.com")
            print("If you want to continue without Ollama, use the --mock flag.")
            return False
    
    def check_server_running(self) -> bool:
        """Check if the Ollama server is running.
        
        Returns:
            bool: True if Ollama server is running, False otherwise.
        """
        try:
            # Check if Ollama is already running by querying the version
            response = requests.get(self.version_api_url, timeout=5)
            if response.status_code == 200:
                logger.info(f"Ollama is running (version: {response.json().get('version', 'unknown')})")
                return True
            else:
                logger.warning(f"Ollama server returned status code {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama server is not running (connection error)")
            return False
        except Exception as e:
            logger.error(f"Error checking Ollama server: {e}")
            return False
    
    def start_ollama(self) -> bool:
        """Start the Ollama server if it's not already running.
        
        Returns:
            bool: True if Ollama is running or was started successfully, False otherwise.
        """
        # First check if Ollama is installed
        if not self.is_ollama_installed:
            logger.error("Ollama is not installed. Please install Ollama first.")
            
            # Ask user if they want to install Ollama
            if self._install_ollama():
                logger.info("Ollama was installed successfully")
            else:
                print("\nOllama is required but not installed. Please install Ollama from https://ollama.com")
                print("If you want to continue without Ollama, use the --mock flag.")
                return False
            
        try:
            # Check if Ollama is already running by querying the version
            response = requests.get(self.version_api_url)
            logger.info(f"Ollama is running (version: {response.json().get('version', 'unknown')})")
            return True

        except requests.exceptions.ConnectionError:
            logger.info("Starting Ollama server...")
            try:
                # Run Ollama in the background
                self.ollama_process = subprocess.Popen(
                    [self.ollama_path, "serve"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                # Wait for the server to start
                time.sleep(5)

                # Check if the server actually started
                try:
                    response = requests.get(self.version_api_url)
                    logger.info(f"Ollama server started (version: {response.json().get('version', 'unknown')})")
                    return True
                except requests.exceptions.ConnectionError:
                    logger.error("ERROR: Failed to start Ollama server.")
                    if self.ollama_process:
                        logger.error("Error details:")
                        stderr = self.ollama_process.stderr.read().decode('utf-8')
                        logger.error(stderr)
                    return False
            except Exception as e:
                logger.error(f"Error starting Ollama: {e}")
                return False

    def stop_ollama(self) -> None:
        """Stop the Ollama server if it was started by this script."""
        if self.ollama_process:
            logger.info("Stopping Ollama server...")
            self.ollama_process.terminate()
            self.ollama_process.wait()
            logger.info("Ollama server stopped")

    def check_model_availability(self):
        """
        Check if the selected model is available in Ollama.
        Returns True if the model is available, False otherwise.
        If the model is not available but auto-install is enabled, attempts to install it.
        """
        try:
            # First check if Ollama is running
            if not self.check_server_running():
                logger.warning("Ollama server is not running")
                if not self.start_ollama():
                    return False
            
            # Check if the model is available
            response = requests.get(self.list_api_url)
            if response.status_code != 200:
                logger.error(f"Failed to list models: {response.text}")
                return False
            
            models = response.json().get('models', [])
            available_models = [m.get('name', '') for m in models]
            
            logger.debug(f"Available models: {available_models}")
            
            # Check if the current model is available
            if self.model in available_models:
                return True
            
            # Special handling for Bielik models - check if already installed with a different name
            if self.model.lower().startswith('speakleash/bielik'):
                for model in available_models:
                    if model.startswith('bielik-custom-'):
                        logger.info(f"Found existing Bielik model installation: {model}")
                        print(f"\nFound existing Bielik model installation: {model}")
                        print("Using existing model instead of downloading again.")
                        self.model = model
                        
                        # Increase timeout for Bielik models as they tend to be larger
                        current_timeout = int(os.getenv('OLLAMA_TIMEOUT', '30'))
                        if current_timeout < 120:
                            os.environ['OLLAMA_TIMEOUT'] = '120'
                            print("Increased API timeout to 120 seconds for Bielik model.")
                        return True
            
            # Try to install the requested model first
            print(f"\nModel '{self.model}' is not installed. Attempting to install it now...")
            if self.install_model(self.model):
                print(f"Successfully installed model '{self.model}'")
                return True
            
            # If installation failed and we're not in strict mode, try to find a suitable alternative
            if os.getenv('OLLAMA_STRICT_MODE', 'false').lower() != 'true':
                # Try to find a similar model from available ones
                for model in available_models:
                    if any(x in model.lower() for x in ['code', 'llama', 'phi', 'mistral']):
                        logger.info(f"Automatically selecting available model: {model} instead of {self.model}")
                        self.model = model
                        return True
                
                # If no suitable model found, use the first available one
                if available_models:
                    logger.info(f"Automatically selecting first available model: {available_models[0]} instead of {self.model}")
                    self.model = available_models[0]
                    return True
            
            # Try fallback models if available
            if hasattr(self, 'fallback_models'):
                print(f"Failed to install model '{self.model}'. Trying fallback models...")
                for fallback in self.fallback_models:
                    if fallback != self.model and fallback not in available_models:
                        print(f"Trying fallback model: {fallback}")
                        if self.install_model(fallback):
                            self.model = fallback
                            print(f"Using fallback model: {fallback}")
                            return True
            
            # If no fallbacks worked, try to use any available model
            if available_models:
                logger.info(f"Using available model: {available_models[0]}")
                self.model = available_models[0]
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking model availability: {str(e)}")
            return False

    def _check_disk_space(self, required_space_gb=None, model_name=None):
        """
        Check if there is enough disk space available for model installation.
        
        Args:
            required_space_gb: Required space in GB, if known
            model_name: Name of the model to check space for
            
        Returns:
            Tuple of (bool, float, float): (has_enough_space, available_gb, required_gb)
        """
        try:
            # Default model size estimates based on model name patterns
            model_size_estimates = {
                'bielik': {
                    '1.5b': 2.0,  # 1.5B model needs ~2GB
                    '3b': 3.5,    # 3B model needs ~3.5GB
                    '7b': 7.0,    # 7B model needs ~7GB
                    '11b': 12.0,  # 11B model needs ~12GB
                },
                'llama': {
                    '7b': 7.0,    # 7B model needs ~7GB
                    '13b': 14.0,  # 13B model needs ~14GB
                },
                'mistral': {
                    '7b': 7.0,    # 7B model needs ~7GB
                },
                'phi': {
                    '2': 2.5,     # Phi-2 needs ~2.5GB
                    '3': 3.5,     # Phi-3 needs ~3.5GB
                },
                'tinyllama': {
                    '1.1b': 1.5,  # TinyLlama needs ~1.5GB
                }
            }
            
            # If required space is not provided, estimate based on model name
            if required_space_gb is None and model_name is not None:
                model_name_lower = model_name.lower()
                required_space_gb = 5.0  # Default estimate if we can't determine
                
                # Try to estimate based on model name patterns
                for model_family, sizes in model_size_estimates.items():
                    if model_family in model_name_lower:
                        for size_key, size_gb in sizes.items():
                            if size_key in model_name_lower:
                                required_space_gb = size_gb
                                # Add extra buffer for temporary files during installation
                                required_space_gb *= 1.5  # Add 50% buffer
                                break
            
            # If still no required space specified, use a conservative default
            if required_space_gb is None:
                required_space_gb = 10.0  # Conservative default: 10GB
            
            # Get available disk space in the Ollama models directory
            ollama_dir = os.path.expanduser('~/.ollama')
            if not os.path.exists(ollama_dir):
                # If Ollama directory doesn't exist yet, check the home directory
                ollama_dir = os.path.expanduser('~')
                
            # Get disk usage statistics
            disk_usage = shutil.disk_usage(ollama_dir)
            available_gb = disk_usage.free / (1024 ** 3)  # Convert bytes to GB
            
            # Check if there's enough space
            has_enough_space = available_gb >= required_space_gb
            
            return has_enough_space, available_gb, required_space_gb
            
        except Exception as e:
            logger.warning(f"Could not check disk space: {e}")
            # If we can't check, assume there's enough space to avoid blocking installation
            return True, 0, 0
    
    def install_model(self, model_name: str) -> bool:
        """
        Install a model using Ollama\'s pull command.
        For SpeakLeash models, performs a special installation process.
        
        Args:
            model_name: The name of the model to install
            
        Returns:
            True if installation was successful, False otherwise
        """
        # First check if Ollama is installed
        if not self.is_ollama_installed:
            logger.error("Cannot install model: Ollama is not installed")
            print("\nError: Ollama is not installed. Please install Ollama from https://ollama.com")
            print("Installation instructions:")
            print("  - Linux/macOS: curl -fsSL https://ollama.com/install.sh | sh")
            print("  - Windows: Visit https://ollama.com/download")
            print("\nIf you want to continue without Ollama, use the --mock flag:")
            print("  getllm --mock")
            return False
            
        # Check disk space before attempting to download large models
        has_enough_space, available_gb, required_gb = self._check_disk_space(model_name=model_name)
        if not has_enough_space:
            logger.warning(f"Not enough disk space to install {model_name}. "
                         f"Available: {available_gb:.2f} GB, Required: {required_gb:.2f} GB")
            print(f"\n⚠️ WARNING: Not enough disk space to install {model_name}"
                  f"\nAvailable: {available_gb:.2f} GB, Required: {required_gb:.2f} GB")
            
            # Ask user if they want to continue anyway or use mock mode
            try:
                import questionary
                continue_anyway = questionary.confirm(
                    "Do you want to attempt installation anyway? (Not recommended)",
                    default=False
                ).ask()
                
                if not continue_anyway:
                    use_mock = questionary.confirm(
                        "Would you like to continue in mock mode instead?",
                        default=True
                    ).ask()
                    
                    if use_mock:
                        print("\nContinuing in mock mode (no model download required)...")
                        # Set environment variable for mock mode
                        os.environ['GETLLM_MOCK_MODE'] = 'True'
                        return True
                    return False
            except ImportError:
                # If questionary is not available, ask with input
                continue_anyway = input("Do you want to attempt installation anyway? (y/N): ").lower().startswith('y')
                if not continue_anyway:
                    use_mock = input("Would you like to continue in mock mode instead? (Y/n): ").lower()
                    if not use_mock.startswith('n'):
                        print("\nContinuing in mock mode (no model download required)...")
                        # Set environment variable for mock mode
                        os.environ['GETLLM_MOCK_MODE'] = 'True'
                        return True
                    return False
        
        # Check if this is a SpeakLeash model that needs special handling
        if model_name.lower().startswith('speakleash/bielik'):
            print(f"\nDetected SpeakLeash Bielik model: {model_name}")
            print("Starting special installation process...")
            return self._install_speakleash_model(model_name)
            
        # For regular models, use ollama pull
        try:
            # Check if Ollama server is running
            if not self.check_server_running():
                if not self.start_ollama():
                    logger.error("Failed to start Ollama server")
                    return False
                    
            print(f"\nInstalling model: {model_name}")
            spinner = ProgressSpinner(message=f"Pulling model {model_name}")
            spinner.start()
            
            # Run ollama pull command
            result = subprocess.run(
                [self.ollama_path, "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            spinner.stop()
            
            if result.returncode == 0:
                print(f"Successfully installed model: {model_name}")
                # Update the current model
                self.model = model_name
                return True
            else:
                print(f"Failed to install model: {model_name}")
                print(f"Error: {result.stderr}")
                
                # Check if the error is due to disk space
                if "no space left on device" in result.stderr.lower():
                    print("\nError: Not enough disk space to install the model.")
                    try:
                        import questionary
                        use_mock = questionary.confirm(
                            "Would you like to continue in mock mode instead?",
                            default=True
                        ).ask()
                        
                        if use_mock:
                            print("\nContinuing in mock mode (no model download required)...")
                            # Set environment variable for mock mode
                            os.environ['GETLLM_MOCK_MODE'] = 'True'
                            return True
                    except ImportError:
                        # If questionary is not available, ask with input
                        use_mock = input("Would you like to continue in mock mode instead? (Y/n): ").lower()
                        if not use_mock.startswith('n'):
                            print("\nContinuing in mock mode (no model download required)...")
                            # Set environment variable for mock mode
                            os.environ['GETLLM_MOCK_MODE'] = 'True'
                            return True
                return False
                
        except Exception as e:
            if 'spinner' in locals():
                spinner.stop()
            print(f"Error installing model: {e}")
            return False
    
    def _install_speakleash_model(self, model_name: str) -> bool:
        """
        Special installation process for SpeakLeash Bielik models.
        
        Args:
            model_name: The name of the SpeakLeash model to install
            
        Returns:
            True if installation was successful, False otherwise
        """
        # Check if a Bielik model is already installed
        try:
            response = requests.get(self.list_api_url, timeout=10)
            response.raise_for_status()
            available_models = [tag['name'] for tag in response.json().get('models', [])]
            
            for model in available_models:
                if model.startswith('bielik-custom-'):
                    logger.info(f"Using existing Bielik model installation: {model}")
                    print(f"\nFound existing Bielik model installation: {model}")
                    print(f"Using existing model instead of downloading again.")
                    
                    # Update the current model
                    self.model = model
                    
                    # Update environment variables for future use
                    os.environ["OLLAMA_MODEL"] = model
                    
                    # Increase timeout for Bielik models as they tend to be larger
                    os.environ["OLLAMA_TIMEOUT"] = "120"
                    print(f"Increased API timeout to 120 seconds for Bielik model.")
                    
                    # Save these settings to .env file if it exists
                    self._update_env_file(model)
                    
                    return True
        except Exception as e:
            logger.warning(f"Could not check for existing Bielik models: {e}")
            # Continue with installation if we can't check for existing models
        
        # Extract the model version from the name
        model_parts = model_name.split('/')
        
        # Check if we have enough disk space for the download and installation
        # We need to be more careful with SpeakLeash models as they can be very large
        has_enough_space, available_gb, required_gb = self._check_disk_space(model_name=model_name)
        if not has_enough_space:
            logger.warning(f"Not enough disk space to install {model_name}. "
                         f"Available: {available_gb:.2f} GB, Required: {required_gb:.2f} GB")
            print(f"\n⚠️ WARNING: Not enough disk space to install {model_name}"
                  f"\nAvailable: {available_gb:.2f} GB, Required: {required_gb:.2f} GB")
            
            # Ask user if they want to continue anyway or use mock mode
            try:
                import questionary
                continue_anyway = questionary.confirm(
                    "Do you want to attempt installation anyway? (Not recommended)",
                    default=False
                ).ask()
                
                if not continue_anyway:
                    use_mock = questionary.confirm(
                        "Would you like to continue in mock mode instead?",
                        default=True
                    ).ask()
                    
                    if use_mock:
                        print("\nContinuing in mock mode (no model download required)...")
                        # Set environment variable for mock mode
                        os.environ['GETLLM_MOCK_MODE'] = 'True'
                        return True
                    return False
            except ImportError:
                # If questionary is not available, ask with input
                continue_anyway = input("Do you want to attempt installation anyway? (y/N): ").lower().startswith('y')
                if not continue_anyway:
                    use_mock = input("Would you like to continue in mock mode instead? (Y/n): ").lower()
                    if not use_mock.startswith('n'):
                        print("\nContinuing in mock mode (no model download required)...")
                        # Set environment variable for mock mode
                        os.environ['GETLLM_MOCK_MODE'] = 'True'
                        return True
                    return False
        if len(model_parts) != 2:
            print(f"Invalid model name format: {model_name}")
            return False
        
        model_version = model_parts[1].lower()
        
        # Set up custom model name for Ollama
        custom_model_name = f"bielik-custom-{int(time.time())}"  # Add timestamp to avoid conflicts
        
        # Determine the correct Hugging Face model path and file
        if "1.5b-v3.0" in model_version:
            hf_repo = "speakleash/Bielik-1.5B-v3.0-Instruct-GGUF"
            model_file = "Bielik-1.5B-v3.0-Instruct.Q8_0.gguf"
        elif "4.5b-v3.0" in model_version:
            hf_repo = "speakleash/Bielik-4.5B-v3.0-Instruct-GGUF"
            model_file = "Bielik-4.5B-v3.0-Instruct.Q8_0.gguf"
        elif "11b-v2.3" in model_version:
            hf_repo = "speakleash/Bielik-11B-v2.3-Instruct-GGUF"
            model_file = "Bielik-11B-v2.3-Instruct.Q8_0.gguf"
        else:
            print(f"Unsupported Bielik model version: {model_version}")
            print("Supported versions: 1.5b-v3.0, 4.5b-v3.0, 11b-v2.3")
            return False
        
        # Create a temporary directory for the model
        temp_dir = os.path.join(PACKAGE_DIR, "models", custom_model_name)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download the model using Hugging Face CLI if available, otherwise use wget
        print(f"\nDownloading {model_name} from Hugging Face...")
        print(f"This may take a while depending on your internet connection.")
        
        model_path = os.path.join(temp_dir, model_file)
        download_url = f"https://huggingface.co/{hf_repo}/resolve/main/{model_file}"
        
        try:
            # First try using huggingface_hub if installed
            try:
                from huggingface_hub import hf_hub_download
                print("Using Hugging Face Hub for download (shows progress)")
                
                hf_hub_download(
                    repo_id=hf_repo,
                    filename=model_file,
                    local_dir=temp_dir,
                    local_dir_use_symlinks=False
                )
                
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"Downloaded file not found at {model_path}")
                    
            except ImportError:
                # Fall back to wget if huggingface_hub is not installed
                print("Hugging Face Hub not available, using wget for download")
                spinner = ProgressSpinner(message=f"Downloading {model_file}")
                spinner.start()
                
                result = subprocess.run(
                    ["wget", "-O", model_path, download_url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                spinner.stop()
                
                if result.returncode != 0 or not os.path.exists(model_path):
                    print(f"Download failed: {result.stderr}")
                    return False
            
            # Create a Modelfile
            modelfile_path = os.path.join(temp_dir, "Modelfile")
            with open(modelfile_path, "w") as f:
                f.write(f"FROM {model_file}\n")
                f.write("PARAMETER num_ctx 4096\n")
                f.write('SYSTEM """\nPoland-optimized NLU model with constitutional AI constraints\n"""\n')
            
            # Create the model in Ollama
            print(f"\nCreating Ollama model: {custom_model_name}")
            spinner = ProgressSpinner(message=f"Creating model in Ollama")
            spinner.start()
            
            result = subprocess.run(
                [self.ollama_path, "create", custom_model_name, "-f", modelfile_path],
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            spinner.stop()
            
            if result.returncode == 0:
                print(f"\nSuccessfully created model: {custom_model_name}")
                print(f"Original model name: {model_name}")
                print(f"\nYou can now use this model with: --model {custom_model_name}")
                
                # Update environment variables for future use
                os.environ["OLLAMA_MODEL"] = custom_model_name
                
                # Update fallback models to include this model
                fallback_models = os.environ.get("OLLAMA_FALLBACK_MODELS", "")
                if fallback_models:
                    os.environ["OLLAMA_FALLBACK_MODELS"] = f"{custom_model_name},{fallback_models}"
                else:
                    os.environ["OLLAMA_FALLBACK_MODELS"] = custom_model_name
                
                # Enable auto-select model
                os.environ["OLLAMA_AUTO_SELECT_MODEL"] = "true"
                
                # Update the current model
                self.model = custom_model_name
                
                # Save these settings to .env file if it exists
                self._update_env_file(custom_model_name)
                
                return True
            else:
                print(f"Failed to create model: {custom_model_name}")
                print(result.stderr)
                
                # Check if the error is due to disk space
                if "no space left on device" in result.stderr.lower():
                    print("\nError: Not enough disk space to install the model.")
                    try:
                        import questionary
                        use_mock = questionary.confirm(
                            "Would you like to continue in mock mode instead?",
                            default=True
                        ).ask()
                        
                        if use_mock:
                            print("\nContinuing in mock mode (no model download required)...")
                            # Set environment variable for mock mode
                            os.environ['GETLLM_MOCK_MODE'] = 'True'
                            return True
                    except ImportError:
                        # If questionary is not available, ask with input
                        use_mock = input("Would you like to continue in mock mode instead? (Y/n): ").lower()
                        if not use_mock.startswith('n'):
                            print("\nContinuing in mock mode (no model download required)...")
                            # Set environment variable for mock mode
                            os.environ['GETLLM_MOCK_MODE'] = 'True'
                            return True
                return False
                
        except Exception as e:
            print(f"Error during model installation: {e}")
            return False
    
    def _update_env_file(self, model_name: str) -> None:
        """
        Update the .env file with the new model settings.
        
        Args:
            model_name: The name of the model to set as default
        """
        from pathlib import Path
        
        # Try to find the central .env file
        current_dir = Path(__file__).parent.absolute()
        env_file = None
        
        # Check if we're in a subdirectory of py-lama
        parts = current_dir.parts
        for i in range(len(parts) - 1, 0, -1):
            if parts[i] == "py-lama":
                env_file = Path(*parts[:i+1]) / ".env"
                break
        
        # If not found, look for the directory structure
        if not env_file or not env_file.exists():
            # Try the local .env file
            env_file = current_dir / ".env"
        
        # Check if .env file exists
        if not env_file.exists():
            try:
                # Create a new .env file
                with open(env_file, "w") as f:
                    f.write(f"OLLAMA_MODEL={model_name}\n")
                    f.write(f"OLLAMA_FALLBACK_MODELS={model_name},codellama:7b,phi:latest\n")
                    f.write("OLLAMA_AUTO_SELECT_MODEL=true\n")
                    # Set higher timeout for Bielik models
                    f.write("OLLAMA_TIMEOUT=120\n")
                print(f"Created .env file with model settings: {env_file}")
            except Exception as e:
                print(f"Error creating .env file: {e}")
            return
        
        try:
            # Read existing .env file
            with open(env_file, "r") as f:
                lines = f.readlines()
            
            # Update or add model settings
            model_line_found = False
            fallback_line_found = False
            auto_select_line_found = False
            timeout_line_found = False
            
            for i, line in enumerate(lines):
                if line.startswith("OLLAMA_MODEL="):
                    lines[i] = f"OLLAMA_MODEL={model_name}\n"
                    model_line_found = True
                elif line.startswith("OLLAMA_FALLBACK_MODELS="):
                    # Add the new model to fallback models if not already there
                    fallback_models = line.split("=")[1].strip()
                    if model_name not in fallback_models:
                        lines[i] = f"OLLAMA_FALLBACK_MODELS={model_name},{fallback_models}\n"
                    fallback_line_found = True
                elif line.startswith("OLLAMA_AUTO_SELECT_MODEL="):
                    lines[i] = "OLLAMA_AUTO_SELECT_MODEL=true\n"
                    auto_select_line_found = True
                elif line.startswith("OLLAMA_TIMEOUT="):
                    # Set higher timeout for Bielik models
                    lines[i] = "OLLAMA_TIMEOUT=120\n"
                    timeout_line_found = True
            
            # Add missing settings
            if not model_line_found:
                lines.append(f"OLLAMA_MODEL={model_name}\n")
            if not fallback_line_found:
                lines.append(f"OLLAMA_FALLBACK_MODELS={model_name},codellama:7b,phi:latest\n")
            if not auto_select_line_found:
                lines.append("OLLAMA_AUTO_SELECT_MODEL=true\n")
            if not timeout_line_found:
                lines.append("OLLAMA_TIMEOUT=120\n")
            
            # Write updated .env file
            with open(env_file, "w") as f:
                f.writelines(lines)
                
            print(f"Updated .env file with model settings: {env_file}")
            
        except Exception as e:
            print(f"Error updating .env file: {e}")

    def list_installed_models(self) -> List[Dict[str, Any]]:
        """
        List models that are currently installed in Ollama.
        
        Returns:
            A list of dictionaries containing model information
        """
        try:
            response = requests.get(self.list_api_url, timeout=10)
            response.raise_for_status()
            return response.json().get('models', [])
        except Exception as e:
            logger.warning(f"Could not list installed models: {e}")
            return []
            
    def query_ollama(self, prompt, template_type=None, **template_args):
        """
        Generate code using Ollama API.
        
        Args:
            prompt: The prompt to send to the model
            template_type: The type of template to use
            **template_args: Additional arguments for the template
            
        Returns:
            The generated code
        """
        # Ensure Ollama is running
        self.start_ollama()
        
        # Check if the model is available
        if not self.check_model_availability():
            raise RuntimeError(f"Model {self.model} is not available")
        
        # Prepare the prompt with template if provided
        if template_type:
            from getllm.cli import get_template
            full_prompt = get_template(prompt, template_type, **template_args)
        else:
            full_prompt = prompt
        
        # Set up the request
        request_data = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        # Add optional parameters if provided
        if 'temperature' in template_args:
            request_data['temperature'] = float(template_args['temperature'])
        
        # Show progress spinner
        spinner = ProgressSpinner(message=f"Generating code with {self.model}")
        spinner.start()
        
        try:
            # Set timeout from environment variable or default to 120 seconds for code generation
            timeout = int(os.getenv('OLLAMA_TIMEOUT', '120'))
            
            print(f"Sending request to Ollama API with timeout {timeout}s...")
            
            # Make the API request
            response = requests.post(
                self.generate_api_url,
                json=request_data,
                timeout=timeout
            )
            response.raise_for_status()
            
            # Get the response text
            result = response.json().get('response', '')
            return result
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise RuntimeError(f"Failed to generate code: {e}")
        finally:
            spinner.stop()
            
    def extract_python_code(self, text):
        """
        Extract Python code from the response.
        
        Args:
            text: The text to extract code from
            
        Returns:
            The extracted Python code
        """
        # Use regex to find Python code blocks
        code_blocks = re.findall(r'```(?:python)?\s*([\s\S]*?)```', text)
        
        if code_blocks:
            # Return the first code block found
            return code_blocks[0].strip()
        else:
            # If no code blocks found, return the original text
            return text


# Convenience functions for external use
def get_ollama_integration(model: str = None) -> OllamaIntegration:
    """
    Get an OllamaIntegration instance with the specified model.
    
    Args:
        model: Optional model name to use
        
    Returns:
        An OllamaIntegration instance
    """
    return OllamaIntegration(model=model)


def start_ollama_server() -> OllamaIntegration:
    """
    Start the Ollama server and return an OllamaIntegration instance.
    
    Returns:
        An OllamaIntegration instance with the server started
    """
    ollama = OllamaIntegration()
    ollama.start_ollama()
    return ollama


def install_ollama_model(model_name: str) -> bool:
    """
    Install a model using Ollama.
    
    Args:
        model_name: The name of the model to install
        
    Returns:
        True if installation was successful, False otherwise
    """
    # Initialize OllamaIntegration
    ollama = OllamaIntegration()
    
    # Check if Ollama is installed
    if not ollama.is_ollama_installed:
        logger.error("Cannot install model: Ollama is not installed")
        print("\nError: Ollama is not installed. Please install Ollama from https://ollama.com")
        print("Installation instructions:")
        print("  - Linux/macOS: curl -fsSL https://ollama.com/install.sh | sh")
        print("  - Windows: Visit https://ollama.com/download")
        print("\nIf you want to continue without Ollama, use the --mock flag:")
        print("  getllm --mock")
        return False
    
    # Start Ollama server
    if not ollama.start_ollama():
        return False
        
    # Install the model
    return ollama.install_model(model_name)


def list_ollama_models() -> List[Dict[str, Any]]:
    """
    List models that are currently installed in Ollama.
    
    Returns:
        A list of dictionaries containing model information
    """
    ollama = OllamaIntegration()
    try:
        ollama.start_ollama()
        return ollama.list_installed_models()
    except Exception:
        return []
