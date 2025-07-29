"""
Ollama server management.
"""
import os
import sys
import time
import logging
import subprocess
import threading
from typing import Optional, Dict, Any, List
import requests

from .exceptions import ServerError, InstallationError
from .models import OllamaModelManager
from . import utils

logger = logging.getLogger('getllm.ollama.server')

class OllamaServer:
    """Manages the Ollama server process and API interactions."""
    
    def __init__(self, ollama_path: str = None, model: str = None):
        """Initialize the Ollama server manager.
        
        Args:
            ollama_path: Path to the Ollama executable
            model: Default model to use
        """
        self.ollama_path = ollama_path or os.getenv('OLLAMA_PATH', 'ollama')
        self.model = model or os.getenv('OLLAMA_MODEL', 'codellama:7b')
        self.fallback_models = os.getenv(
            'OLLAMA_FALLBACK_MODELS', 
            'codellama:7b,phi3:latest,tinyllama:latest'
        ).split(',')
        
        # API endpoints
        self.base_api_url = "http://localhost:11434/api"
        self.generate_api_url = f"{self.base_api_url}/generate"
        self.chat_api_url = f"{self.base_api_url}/chat"
        self.version_api_url = f"{self.base_api_url}/version"
        
        # Process management
        self.ollama_process = None
        self.original_model_specified = model is not None
        
        # Model manager
        self.model_manager = OllamaModelManager(ollama_path, self.base_api_url)
        
        # Check if Ollama is installed
        self.is_ollama_installed = self._check_ollama_installed()
    
    def _check_ollama_installed(self) -> bool:
        """Check if Ollama is installed on the system."""
        try:
            result = subprocess.run(
                [self.ollama_path, '--version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
            
    def list_models(self) -> List[Dict]:
        """List all available Ollama models.
        
        Returns:
            List of dictionaries containing model information
        """
        try:
            # Use the model manager to list models
            return self.model_manager.list_installed_models()
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            raise
    
    def install_ollama(self, method: str = 'auto') -> bool:
        """Install Ollama using the specified method.
        
        Args:
            method: Installation method ('auto', 'direct', 'docker', 'bexy')
            
        Returns:
            bool: True if installation was successful
            
        Raises:
            InstallationError: If installation fails
        """
        if method == 'auto':
            if utils.is_linux():
                return self._install_ollama_direct()
            elif utils.is_macos() or utils.is_windows():
                return self._install_ollama_direct()
            else:
                return self._install_ollama_docker()
        elif method == 'direct':
            return self._install_ollama_direct()
        elif method == 'docker':
            return self._install_ollama_docker()
        elif method == 'bexy':
            return self._install_ollama_bexy()
        else:
            raise ValueError(f"Unknown installation method: {method}")
    
    def _install_ollama_direct(self) -> bool:
        """Install Ollama directly using the official installation script."""
        logger.info("Installing Ollama using the official installation script...")
        
        if utils.is_linux():
            install_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
        elif utils.is_macos():
            install_cmd = "brew install ollama"
        elif utils.is_windows():
            install_cmd = "winget install ollama.ollama"
        else:
            raise InstallationError("Unsupported operating system for direct installation")
        
        success, output = utils.run_command(install_cmd)
        if not success:
            raise InstallationError(f"Failed to install Ollama: {output}")
        
        self.is_ollama_installed = True
        return True
    
    def _install_ollama_docker(self) -> bool:
        """Install and run Ollama using Docker."""
        logger.info("Installing Ollama using Docker...")
        
        # Check if Docker is installed
        docker_check = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True
        )
        
        if docker_check.returncode != 0:
            raise InstallationError(
                "Docker is not installed. Please install Docker first."
            )
        
        # Pull the Ollama Docker image
        pull_cmd = "docker pull ollama/ollama"
        success, output = utils.run_command(pull_cmd)
        if not success:
            raise InstallationError(f"Failed to pull Ollama Docker image: {output}")
        
        # Create a Docker volume for persistent storage
        volume_cmd = "docker volume create ollama_data"
        success, output = utils.run_command(volume_cmd)
        if not success and "already exists" not in output:
            logger.warning(f"Failed to create Docker volume (may already exist): {output}")
        
        # Run the Ollama container
        run_cmd = (
            "docker run -d "
            "--name ollama "
            "-p 11434:11434 "
            "-v ollama_data:/root/.ollama "
            "--restart unless-stopped "
            "ollama/ollama"
        )
        
        success, output = utils.run_command(run_cmd)
        if not success:
            raise InstallationError(f"Failed to start Ollama container: {output}")
        
        logger.info("Ollama is running in a Docker container")
        self.is_ollama_installed = True
        return True
    
    def _install_ollama_bexy(self) -> bool:
        """Set up Ollama in a bexy sandbox environment."""
        logger.warning("Bexy sandbox installation is not fully implemented")
        return False
    
    def is_running(self) -> bool:
        """Check if the Ollama server is running."""
        try:
            response = requests.get(self.version_api_url, timeout=5)
            return response.status_code == 200
        except (requests.RequestException, ConnectionError):
            return False
    
    def start(self) -> bool:
        """Start the Ollama server if it's not already running."""
        if self.is_running():
            logger.info("Ollama server is already running")
            return True
        
        if not self.is_ollama_installed:
            logger.info("Ollama is not installed. Attempting to install...")
            try:
                self.install_ollama()
            except InstallationError as e:
                logger.error(f"Failed to install Ollama: {e}")
                return False
        
        # Start the Ollama server in a separate process
        try:
            self.ollama_process = subprocess.Popen(
                [self.ollama_path, 'serve'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for the server to start
            max_attempts = 30
            for _ in range(max_attempts):
                if self.is_running():
                    logger.info("Ollama server started successfully")
                    return True
                time.sleep(1)
            
            # If we get here, the server didn't start
            error = self.ollama_process.stderr.read() if self.ollama_process.stderr else "Unknown error"
            logger.error(f"Failed to start Ollama server: {error}")
            return False
            
        except Exception as e:
            logger.error(f"Error starting Ollama server: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the Ollama server if it was started by this instance."""
        if self.ollama_process:
            try:
                self.ollama_process.terminate()
                self.ollama_process.wait(timeout=10)
                logger.info("Stopped Ollama server")
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                self.ollama_process.kill()
                logger.warning("Forcefully killed Ollama server")
            finally:
                self.ollama_process = None
    
    def ensure_model_available(self, model_name: str = None) -> bool:
        """Ensure the specified model is available, installing it if necessary."""
        model = model_name or self.model
        
        try:
            if self.model_manager.is_model_installed(model):
                return True
                
            logger.info(f"Model {model} not found. Attempting to install...")
            return self.model_manager.install_model(model)
            
        except Exception as e:
            logger.error(f"Error ensuring model {model} is available: {e}")
            return False
    
    def query(
        self, 
        prompt: str, 
        model: str = None, 
        template_type: str = None,
        **template_args
    ) -> str:
        """
        Generate a response using the specified model.
        
        Args:
            prompt: The prompt to send to the model
            model: The model to use (defaults to self.model)
            template_type: Type of template to use
            **template_args: Additional template arguments
            
        Returns:
            The generated text
            
        Raises:
            ServerError: If there's an error communicating with the Ollama server
        """
        model_to_use = model or self.model
        
        if not self.is_running() and not self.start():
            raise ServerError("Failed to start Ollama server")
        
        if not self.ensure_model_available(model_to_use):
            raise ServerError(f"Failed to ensure model {model_to_use} is available")
        
        # Prepare the request payload
        payload = {
            "model": model_to_use,
            "prompt": prompt,
            "stream": False,
            **template_args
        }
        
        try:
            response = requests.post(
                self.generate_api_url,
                json=payload,
                timeout=300  # 5 minute timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.RequestException as e:
            error_msg = f"Error querying Ollama API: {e}"
            logger.error(error_msg)
            raise ServerError(error_msg) from e
    
    def query_ollama(self, *args, **kwargs):
        """Alias for query method for backward compatibility.
        
        This method is kept for backward compatibility with code that expects
        the query_ollama method. It simply calls the query method with the
        provided arguments.
        
        Returns:
            The generated text from the query method
        """
        return self.query(*args, **kwargs)
        
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        **kwargs
    ) -> str:
        """
        Have a chat conversation with the model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: The model to use (defaults to self.model)
            **kwargs: Additional parameters for the API call
            
        Returns:
            The model's response
            
        Raises:
            ServerError: If there's an error communicating with the Ollama server
        """
        model_to_use = model or self.model
        
        if not self.is_running() and not self.start():
            raise ServerError("Failed to start Ollama server")
        
        if not self.ensure_model_available(model_to_use):
            raise ServerError(f"Failed to ensure model {model_to_use} is available")
        
        # Prepare the request payload
        payload = {
            "model": model_to_use,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        try:
            response = requests.post(
                self.chat_api_url,
                json=payload,
                timeout=300  # 5 minute timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('message', {}).get('content', '').strip()
            
        except requests.RequestException as e:
            error_msg = f"Error in chat with Ollama API: {e}"
            logger.error(error_msg)
            raise ServerError(error_msg) from e
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.stop()
