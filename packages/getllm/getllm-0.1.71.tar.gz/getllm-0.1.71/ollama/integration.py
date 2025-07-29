"""Main integration class for Ollama."""

import os
import logging
from typing import Optional, List, Dict, Any, Union, Iterator

from .services.server import OllamaServer
from .models.manager import OllamaModelManager
from .models.installer import ModelInstaller
from .api.client import OllamaClient
from .exceptions import (
    OllamaError,
    OllamaInstallationError,
    ModelNotFoundError,
    ModelInstallationError,
    APIError
)

logger = logging.getLogger('getllm.ollama.integration')

class OllamaIntegration:
    """Main class for Ollama integration."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        ollama_path: Optional[str] = None,
        base_url: str = "http://localhost:11434/api"
    ):
        """Initialize the Ollama integration.
        
        Args:
            model: The default model to use
            ollama_path: Path to the Ollama executable
            base_url: Base URL for the Ollama API
        """
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3')
        self.base_url = base_url
        
        # Initialize components
        self.server = OllamaServer(ollama_path)
        self.model_manager = OllamaModelManager(base_url)
        self.model_installer = ModelInstaller(base_url)
        self.client = OllamaClient(base_url)
        
        # Start the server if it's not already running
        self.ensure_server_running()
    
    def ensure_server_running(self) -> bool:
        """Ensure the Ollama server is running.
        
        Returns:
            bool: True if the server is running, False otherwise
        """
        if not self.server.is_running():
            logger.info("Ollama server is not running. Starting it now...")
            return self.server.start()
        return True
    
    def check_model_availability(self, model: Optional[str] = None) -> bool:
        """Check if a model is available.
        
        Args:
            model: The model to check. If None, uses the default model.
            
        Returns:
            bool: True if the model is available, False otherwise
        """
        model_name = model or self.model
        return self.model_manager.model_exists(model_name)
    
    def install_model(
        self,
        model_name: str,
        from_hf: bool = False,
        hf_model_path: Optional[str] = None,
        stream: bool = True
    ) -> bool:
        """Install a model.
        
        Args:
            model_name: Name of the model to install
            from_hf: Whether to install from Hugging Face
            hf_model_path: Path to the Hugging Face model (if from_hf is True)
            stream: Whether to stream the installation progress
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        try:
            if from_hf:
                hf_path = hf_model_path or model_name
                return self.model_installer.install_from_huggingface(hf_path, model_name)
            else:
                return self.model_installer.install_model(model_name, stream)
        except Exception as e:
            logger.error(f"Failed to install model {model_name}: {str(e)}")
            return False
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Generate a response from the model.
        
        Args:
            prompt: The prompt to generate a response for
            model: The model to use (defaults to self.model)
            **kwargs: Additional arguments to pass to the client
            
        Returns:
            The generated response or a generator of response chunks
        """
        model_name = model or self.model
        
        # Check if the model is available
        if not self.check_model_availability(model_name):
            logger.warning(f"Model {model_name} is not installed. Attempting to install...")
            if not self.install_model(model_name):
                raise ModelInstallationError(f"Failed to install model: {model_name}")
        
        return self.client.generate(prompt=prompt, model=model_name, **kwargs)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Generate a chat response.
        
        Args:
            messages: List of message objects with 'role' and 'content' keys
            model: The model to use (defaults to self.model)
            **kwargs: Additional arguments to pass to the client
            
        Returns:
            The chat response or a generator of response chunks
        """
        model_name = model or self.model
        
        # Check if the model is available
        if not self.check_model_availability(model_name):
            logger.warning(f"Model {model_name} is not installed. Attempting to install...")
            if not self.install_model(model_name):
                raise ModelInstallationError(f"Failed to install model: {model_name}")
        
        return self.client.chat(messages=messages, model=model_name, **kwargs)
    
    def embeddings(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate embeddings for a prompt.
        
        Args:
            prompt: The prompt to generate embeddings for
            model: The model to use (defaults to self.model)
            **kwargs: Additional arguments to pass to the client
            
        Returns:
            Dictionary containing the embeddings and metadata
        """
        model_name = model or self.model
        
        # Check if the model is available
        if not self.check_model_availability(model_name):
            logger.warning(f"Model {model_name} is not installed. Attempting to install...")
            if not self.install_model(model_name):
                raise ModelInstallationError(f"Failed to install model: {model_name}")
        
        return self.client.embeddings(prompt=prompt, model=model_name, **kwargs)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models.
        
        Returns:
            List of model dictionaries with their details
        """
        return self.model_manager.list_models()
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model.
        
        Args:
            model_name: Name of the model to get info for
            
        Returns:
            Dictionary with model information or None if not found
        """
        return self.model_manager.get_model_info(model_name)
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a model.
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        return self.model_manager.delete_model(model_name)
    
    def copy_model(self, source_name: str, target_name: str) -> bool:
        """Create a copy of a model with a new name.
        
        Args:
            source_name: Name of the source model
            target_name: Name for the new model
            
        Returns:
            bool: True if the copy was successful, False otherwise
        """
        return self.model_manager.copy_model(source_name, target_name)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.server.stop()
