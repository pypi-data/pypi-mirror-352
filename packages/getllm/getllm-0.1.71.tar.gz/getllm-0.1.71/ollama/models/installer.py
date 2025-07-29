"""Model installation and management for Ollama."""

import os
import logging
import shutil
import platform
import subprocess
from typing import Optional, List, Tuple, Dict, Any
import requests

logger = logging.getLogger('getllm.ollama.models.installer')

class ModelInstaller:
    """Handles installation and management of Ollama models."""
    
    def __init__(self, base_url: str = "http://localhost:11434/api"):
        """Initialize the model installer.
        
        Args:
            base_url: Base URL for the Ollama API
        """
        self.base_url = base_url
        self.pull_url = f"{base_url}/pull"
        self.push_url = f"{base_url}/push"
        
        # Default fallback models
        self.fallback_models = [
            'llama3',
            'llama2',
            'mistral',
            'codellama',
            'phi'
        ]
    
    def install_model(self, model_name: str, stream: bool = True) -> bool:
        """Install a model from the Ollama library.
        
        Args:
            model_name: Name of the model to install (e.g., 'llama3')
            stream: Whether to stream the download progress
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        try:
            logger.info(f"Starting installation of model: {model_name}")
            
            # Check if model is already installed
            if self._is_model_installed(model_name):
                logger.info(f"Model {model_name} is already installed")
                return True
            
            # Start the pull request
            response = requests.post(
                self.pull_url,
                json={'name': model_name, 'stream': stream},
                stream=True,
                timeout=60  # Initial connection timeout
            )
            
            # Process the streamed response
            if stream:
                for line in response.iter_lines():
                    if line:
                        try:
                            progress = line.decode('utf-8')
                            logger.debug(f"Download progress: {progress}")
                            # Here you could emit progress updates
                        except Exception as e:
                            logger.warning(f"Error processing progress update: {str(e)}")
            
            response.raise_for_status()
            logger.info(f"Successfully installed model: {model_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to install model {model_name}: {str(e)}")
            return False
    
    def install_from_huggingface(self, model_path: str, model_name: Optional[str] = None) -> bool:
        """Install a model from Hugging Face.
        
        Args:
            model_path: Path to the model on Hugging Face (e.g., 'username/model-name')
            model_name: Optional name to give the installed model
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        try:
            # Create a Modelfile for the Hugging Face model
            modelfile = f"FROM {model_path}"
            if model_name:
                modelfile += f"\nPARAMETER name \"{model_name}\""
            
            # Save the Modelfile
            with open('Modelfile', 'w', encoding='utf-8') as f:
                f.write(modelfile)
            
            # Build the model
            cmd = ["ollama", "create", "-f", "Modelfile"]
            if model_name:
                cmd.append(model_name)
                
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Clean up
            if os.path.exists('Modelfile'):
                os.remove('Modelfile')
            
            if result.returncode != 0:
                logger.error(f"Failed to build model from Hugging Face: {result.stderr}")
                return False
                
            logger.info(f"Successfully installed model from Hugging Face: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error installing model from Hugging Face: {str(e)}")
            return False
    
    def _is_model_installed(self, model_name: str) -> bool:
        """Check if a model is already installed.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            bool: True if the model is installed, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model.get('name') == model_name for model in models)
            return False
        except requests.exceptions.RequestException:
            return False
    
    def get_fallback_models(self) -> List[str]:
        """Get the list of fallback models.
        
        Returns:
            List of fallback model names
        """
        return self.fallback_models.copy()
    
    def set_fallback_models(self, models: List[str]) -> None:
        """Set the list of fallback models.
        
        Args:
            models: List of model names to use as fallbacks
        """
        self.fallback_models = models.copy()
