"""
Model management for Ollama integration.
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import requests

from .exceptions import (
    ModelError,
    ModelNotFoundError,
    ModelInstallationError,
    InsufficientDiskSpaceError,
    ModelValidationError
)

logger = logging.getLogger('getllm.ollama.models')

class OllamaModelManager:
    """Manages Ollama models including installation and listing."""
    
    def __init__(self, ollama_path: Optional[str] = None, base_api_url: str = "http://localhost:11434/api"):
        """Initialize the model manager.
        
        Args:
            ollama_path: Path to the Ollama executable
            base_api_url: Base URL for the Ollama API
        """
        self.ollama_path = ollama_path or os.getenv('OLLAMA_PATH', 'ollama')
        self.base_api_url = base_api_url
        self.models_api_url = f"{base_api_url}/tags"
        self.pull_api_url = f"{base_api_url}/pull"
        
    def list_installed_models(self) -> List[Dict[str, Any]]:
        """List all installed Ollama models.
        
        Returns:
            List of dictionaries containing model information
            
        Raises:
            ModelError: If there's an error listing models
        """
        try:
            response = requests.get(self.models_api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except requests.RequestException as e:
            logger.error(f"Error listing Ollama models: {e}")
            raise ModelError(f"Failed to list models: {e}")
    
    def is_model_installed(self, model_name: str) -> bool:
        """Check if a specific model is installed.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            bool: True if the model is installed, False otherwise
        """
        try:
            models = self.list_installed_models()
            return any(model.get('name') == model_name for model in models)
        except ModelError:
            return False
    
    def install_model(self, model_name: str) -> bool:
        """Install a model.
        
        Args:
            model_name: Name of the model to install
            
        Returns:
            bool: True if installation was successful, False otherwise
            
        Raises:
            ModelInstallationError: If there's an error installing the model
            InsufficientDiskSpaceError: If there's not enough disk space
        """
        try:
            # Check disk space first
            if not self._check_disk_space(model_name):
                raise InsufficientDiskSpaceError("Not enough disk space to install the model")
            
            logger.info(f"Pulling model: {model_name}")
            response = requests.post(
                self.pull_api_url,
                json={"name": model_name},
                stream=True
            )
            
            if response.status_code != 200:
                error_msg = f"Failed to pull model {model_name}: {response.text}"
                logger.error(error_msg)
                raise ModelInstallationError(error_msg)
            
            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if 'status' in data:
                            logger.info(f"Status: {data['status']}")
                        if 'error' in data:
                            error_msg = f"Error pulling model {model_name}: {data['error']}"
                            logger.error(error_msg)
                            raise ModelInstallationError(error_msg)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse response line: {line}")
            
            logger.info(f"Successfully installed model: {model_name}")
            return True
            
        except requests.RequestException as e:
            error_msg = f"Failed to install model {model_name}: {e}"
            logger.error(error_msg)
            raise ModelInstallationError(error_msg) from e
    
    def _check_disk_space(self, model_name: str, required_space_gb: float = 10.0) -> bool:
        """Check if there's enough disk space for the model.
        
        Args:
            model_name: Name of the model being installed
            required_space_gb: Required space in GB (default: 10GB)
            
        Returns:
            bool: True if there's enough space, False otherwise
        """
        try:
            # Get disk usage statistics for the partition containing the home directory
            total, used, free = shutil.disk_usage(os.path.expanduser("~"))
            free_gb = free / (1024 ** 3)  # Convert bytes to GB
            
            logger.debug(f"Disk space - Free: {free_gb:.2f}GB, Required: {required_space_gb}GB")
            
            if free_gb < required_space_gb:
                logger.warning(
                    f"Insufficient disk space for model {model_name}. "
                    f"Required: {required_space_gb}GB, Available: {free_gb:.2f}GB"
                )
                return False
                
            return True
            
        except Exception as e:
            logger.warning(f"Error checking disk space: {e}")
            # If we can't check disk space, assume it's fine and let the installation proceed
            return True
    
    def validate_model(self, model_name: str) -> bool:
        """Validate that a model is properly installed and accessible.
        
        Args:
            model_name: Name of the model to validate
            
        Returns:
            bool: True if the model is valid, False otherwise
            
        Raises:
            ModelValidationError: If the model fails validation
        """
        if not self.is_model_installed(model_name):
            raise ModelValidationError(f"Model not installed: {model_name}")
        
        # TODO: Add more comprehensive validation if needed
        return True
