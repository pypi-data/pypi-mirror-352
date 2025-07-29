"""
Model management for Ollama integration.
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import requests

from .exceptions import ModelNotFoundError, ModelInstallationError, DiskSpaceError
from . import utils

logger = logging.getLogger('getllm.ollama.models')

class OllamaModelManager:
    """Manages Ollama models including installation and listing."""
    
    def __init__(self, ollama_path: str = None, base_api_url: str = "http://localhost:11434/api"):
        """Initialize the model manager.
        
        Args:
            ollama_path: Path to the Ollama executable
            base_api_url: Base URL for the Ollama API
        """
        self.ollama_path = ollama_path or os.getenv('OLLAMA_PATH', 'ollama')
        self.base_api_url = base_api_url
        self.models_api_url = f"{base_api_url}/tags"
        self.pull_api_url = f"{base_api_url}/pull"
        
        # Set up models directory
        self.models_dir = os.path.join(os.path.expanduser('~'), '.ollama', 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
    def list_installed_models(self) -> List[Dict[str, Any]]:
        """List all installed Ollama models.
        
        Returns:
            List of dictionaries containing model information
            
        Raises:
            requests.RequestException: If there's an error communicating with the Ollama API
        """
        try:
            response = requests.get(self.models_api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except requests.RequestException as e:
            logger.error(f"Error listing Ollama models: {e}")
            raise
    
    def is_model_installed(self, model_name: str) -> bool:
        """Check if a specific model is installed.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            bool: True if the model is installed, False otherwise
        """
        try:
            models = self.list_installed_models()
            return any(model['name'] == model_name for model in models)
        except requests.RequestException:
            return False
    
    def install_model(self, model_name: str) -> bool:
        """Install a model using Ollama's pull command.
        
        Args:
            model_name: Name of the model to install
            
        Returns:
            bool: True if installation was successful, False otherwise
            
        Raises:
            ModelInstallationError: If there's an error during installation
            DiskSpaceError: If there's not enough disk space
        """
        logger.info(f"Installing model: {model_name}")
        
        # Check disk space before proceeding
        has_space, available_gb, required_gb = utils.check_disk_space(model_name=model_name)
        if not has_space:
            raise DiskSpaceError(
                f"Not enough disk space to install model {model_name}",
                available_gb=available_gb,
                required_gb=required_gb
            )
        
        # Special handling for SpeakLeash models
        if 'speakleash' in model_name.lower():
            return self._install_speakleash_model(model_name)
        
        # Normal Ollama model installation
        cmd = f"{self.ollama_path} pull {model_name}"
        success, output = utils.run_command(cmd)
        
        if not success:
            error_msg = f"Failed to install model {model_name}: {output}"
            logger.error(error_msg)
            raise ModelInstallationError(error_msg)
        
        logger.info(f"Successfully installed model: {model_name}")
        return True
    
    def _install_speakleash_model(self, model_name: str) -> bool:
        """Special installation process for SpeakLeash Bielik models.
        
        Args:
            model_name: Name of the SpeakLeash model to install
            
        Returns:
            bool: True if installation was successful
            
        Raises:
            ModelInstallationError: If installation fails
        """
        logger.info(f"Installing SpeakLeash model: {model_name}")
        
        # Extract model name without the 'speakleash/' prefix if present
        model_short_name = model_name.split('/')[-1] if '/' in model_name else model_name
        
        # Create a temporary directory for the model files
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the model files
            model_url = f"https://huggingface.co/speakleash/{model_short_name}/resolve/main/"
            
            # List of files we need to download
            files = [
                "config.json",
                "generation_config.json",
                "pytorch_model-00001-of-00002.bin",
                "pytorch_model-00002-of-00002.bin",
                "pytorch_model.bin.index.json",
                "special_tokens_map.json",
                "tokenizer.json",
                "tokenizer_config.json"
            ]
            
            # Download each file
            for file in files:
                file_url = f"{model_url}{file}"
                file_path = os.path.join(temp_dir, file)
                
                logger.info(f"Downloading {file}...")
                try:
                    response = requests.get(file_url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                except Exception as e:
                    error_msg = f"Failed to download {file}: {e}"
                    logger.error(error_msg)
                    raise ModelInstallationError(error_msg)
            
            # Create a Modelfile for Ollama
            modelfile_path = os.path.join(temp_dir, "Modelfile")
            with open(modelfile_path, 'w') as f:
                f.write(f"FROM {temp_dir}\n")
                f.write('TEMPLATE """{{ if .System }}...{{ end }}{{ if .Prompt }}{{ .Prompt }}{{ end }}"""\n')
            
            # Build the model using Ollama
            cmd = f"{self.ollama_path} create {model_name} -f {modelfile_path}"
            success, output = utils.run_command(cmd, cwd=temp_dir)
            
            if not success:
                error_msg = f"Failed to build SpeakLeash model {model_name}: {output}"
                logger.error(error_msg)
                raise ModelInstallationError(error_msg)
        
        logger.info(f"Successfully installed SpeakLeash model: {model_name}")
        return True
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model.
        
        Args:
            model_name: Name of the model to get info for
            
        Returns:
            Dict containing model information
            
        Raises:
            ModelNotFoundError: If the model is not found
        """
        try:
            models = self.list_installed_models()
            for model in models:
                if model['name'] == model_name:
                    return model
            
            raise ModelNotFoundError(f"Model not found: {model_name}")
        except requests.RequestException as e:
            error_msg = f"Error getting model info for {model_name}: {e}"
            logger.error(error_msg)
            raise ModelInstallationError(error_msg) from e
