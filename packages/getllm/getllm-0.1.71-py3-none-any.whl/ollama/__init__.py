"""
Ollama Server for PyLLM

This package provides a server interface for Ollama for high-quality code generation.
It handles model management, automatic installation, and fallback mechanisms.
"""

import os
from typing import Optional, List, Dict, Any, Union, Iterator

from .models import OllamaModelManager
from .services.server import OllamaServer
from .integration import OllamaIntegration
from .exceptions import (
    OllamaError,
    OllamaInstallationError,
    OllamaStartupError,
    ModelNotFoundError,
    ModelInstallationError,
    ModelGenerationError,
    APIError,
    AuthenticationError,
    RateLimitExceededError,
    InsufficientDiskSpaceError,
    ModelValidationError
)

# Create a global instance for the default integration
_global_integration = None

def get_ollama_integration(
    model: Optional[str] = None,
    ollama_path: Optional[str] = None,
    base_url: str = "http://localhost:11434/api"
) -> OllamaIntegration:
    """Get or create the global Ollama integration instance.
    
    Args:
        model: The default model to use
        ollama_path: Path to the Ollama executable
        base_url: Base URL for the Ollama API
        
    Returns:
        OllamaIntegration: The global Ollama integration instance
    """
    global _global_integration
    if _global_integration is None:
        _global_integration = OllamaIntegration(
            model=model,
            ollama_path=ollama_path,
            base_url=base_url
        )
    return _global_integration

def start_ollama_server(ollama_path: Optional[str] = None) -> bool:
    """Start the Ollama server.
    
    Args:
        ollama_path: Path to the Ollama executable
        
    Returns:
        bool: True if the server was started successfully, False otherwise
    """
    server = OllamaServer(ollama_path)
    return server.start()

def install_ollama_model(model_name: str, **kwargs) -> bool:
    """Install an Ollama model.
    
    Args:
        model_name: Name of the model to install
        **kwargs: Additional arguments to pass to the model installer
        
    Returns:
        bool: True if the model was installed successfully, False otherwise
    """
    integration = get_ollama_integration()
    return integration.install_model(model_name, **kwargs)

def list_ollama_models() -> List[Dict[str, Any]]:
    """List all available Ollama models.
    
    Returns:
        List[Dict[str, Any]]: List of model information dictionaries
    """
    integration = get_ollama_integration()
    return integration.list_models()

def query_ollama(
    prompt: str,
    model: Optional[str] = None,
    **kwargs
) -> Union[str, Iterator[str]]:
    """Query the Ollama API with a prompt.
    
    Args:
        prompt: The prompt to send to the model
        model: The model to use (defaults to the integration's default model)
        **kwargs: Additional arguments to pass to the API
        
    Returns:
        Union[str, Iterator[str]]: The model's response, either as a string or a stream of strings
    """
    integration = get_ollama_integration()
    return integration.query(prompt, model=model, **kwargs)

# For backward compatibility (deprecated, will be removed in a future version)
OllamaServer = OllamaIntegration  # Alias for backward compatibility (deprecated)

__all__ = [
    'OllamaServer',
    'OllamaModelManager',
    'OllamaIntegration',
    'OllamaError',
    'OllamaInstallationError',
    'OllamaStartupError',
    'ModelNotFoundError',
    'ModelInstallationError',
    'ModelGenerationError',
    'APIError',
    'AuthenticationError',
    'RateLimitExceededError',
    'InsufficientDiskSpaceError',
    'ModelValidationError',
    'get_ollama_integration',
    'start_ollama_server',
    'install_ollama_model',
    'list_ollama_models',
    'query_ollama'
]
