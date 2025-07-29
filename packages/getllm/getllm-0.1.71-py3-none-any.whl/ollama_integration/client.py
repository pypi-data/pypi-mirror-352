"""
Ollama client for interacting with the Ollama API.
"""

import os
import logging
from typing import Optional, Dict, Any, List, Union

from .models import OllamaModelManager
from .server import OllamaServer
from .exceptions import (
    OllamaError,
    ModelNotFoundError,
    ModelInstallationError,
    ModelGenerationError
)

logger = logging.getLogger('getllm.ollama.client')

class OllamaClient:
    """Client for interacting with the Ollama API and managing models."""
    
    def __init__(self, model: Optional[str] = None, auto_start: bool = True):
        """Initialize the Ollama client.
        
        Args:
            model: The default model to use for generation
            auto_start: Whether to automatically start the Ollama server if not running
        """
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3')
        self.auto_start = auto_start
        self.server = OllamaServer()
        self.model_manager = OllamaModelManager()
        
        if auto_start:
            self.ensure_server_running()
    
    def ensure_server_running(self) -> bool:
        """Ensure the Ollama server is running.
        
        Returns:
            bool: True if the server is running, False otherwise
        """
        if not self.server.is_running():
            logger.info("Starting Ollama server...")
            return self.server.start()
        return True
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        **generation_params
    ) -> str:
        """Generate text using the specified model.
        
        Args:
            prompt: The prompt to generate text from
            model: The model to use (defaults to the client's default model)
            **generation_params: Additional parameters for text generation
            
        Returns:
            The generated text
            
        Raises:
            ModelGenerationError: If there's an error generating text
            ModelNotFoundError: If the specified model is not found
        """
        model = model or self.model
        
        try:
            if not self.model_manager.is_model_installed(model):
                logger.info(f"Model {model} not found, attempting to install...")
                if not self.install_model(model):
                    raise ModelNotFoundError(f"Failed to install model: {model}")
            
            return self.server.generate(prompt, model=model, **generation_params)
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            if isinstance(e, (ModelNotFoundError, ModelInstallationError, ModelGenerationError)):
                raise
            raise ModelGenerationError(f"Failed to generate text: {e}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **generation_params
    ) -> str:
        """Generate a chat response using the specified model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: The model to use (defaults to the client's default model)
            **generation_params: Additional parameters for text generation
            
        Returns:
            The generated chat response
            
        Raises:
            ModelGenerationError: If there's an error generating the response
        """
        model = model or self.model
        
        try:
            if not self.model_manager.is_model_installed(model):
                logger.info(f"Model {model} not found, attempting to install...")
                if not self.install_model(model):
                    raise ModelNotFoundError(f"Failed to install model: {model}")
            
            return self.server.chat(messages, model=model, **generation_params)
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            if isinstance(e, (ModelNotFoundError, ModelInstallationError, ModelGenerationError)):
                raise
            raise ModelGenerationError(f"Failed to generate chat response: {e}")
    
    def install_model(self, model_name: str) -> bool:
        """Install a model.
        
        Args:
            model_name: The name of the model to install
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        return self.model_manager.install_model(model_name)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all installed models.
        
        Returns:
            List of dictionaries containing model information
        """
        return self.model_manager.list_installed_models()
    
    def is_model_installed(self, model_name: str) -> bool:
        """Check if a model is installed.
        
        Args:
            model_name: The name of the model to check
            
        Returns:
            bool: True if the model is installed, False otherwise
        """
        return self.model_manager.is_model_installed(model_name)
    
    def start_server(self) -> bool:
        """Start the Ollama server.
        
        Returns:
            bool: True if the server was started successfully, False otherwise
        """
        return self.server.start()
    
    def stop_server(self) -> bool:
        """Stop the Ollama server.
        
        Returns:
            bool: True if the server was stopped successfully, False otherwise
        """
        return self.server.stop()
    
    def is_server_running(self) -> bool:
        """Check if the Ollama server is running.
        
        Returns:
            bool: True if the server is running, False otherwise
        """
        return self.server.is_running()
