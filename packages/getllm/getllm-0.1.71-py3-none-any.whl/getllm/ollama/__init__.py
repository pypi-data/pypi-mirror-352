"""
Ollama Server for PyLLM

This package provides a server interface for Ollama for high-quality code generation.
It handles model management, automatic installation, and fallback mechanisms.
"""

import warnings
from typing import Optional, List, Dict, Any

from .models import OllamaModelManager
from .server import OllamaServer
from .api import get_ollama_server as _get_ollama_server, query_ollama, list_ollama_models, install_ollama_model
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

def get_ollama_server(model: Optional[str] = None) -> OllamaServer:
    """
    Get an OllamaServer instance with the specified model.
    
    Args:
        model: Optional model name to use
        
    Returns:
        An OllamaServer instance
    """
    return _get_ollama_server(model=model)

def get_ollama_integration(model: Optional[str] = None) -> OllamaServer:
    """
    Deprecated. Use get_ollama_server() instead.
    
    Args:
        model: Optional model name to use
        
    Returns:
        An OllamaServer instance
    """
    warnings.warn(
        "get_ollama_integration() is deprecated and will be removed in a future version. "
        "Use get_ollama_server() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return get_ollama_server(model=model)

def start_ollama_server() -> OllamaServer:
    """
    Start the Ollama server and return an OllamaServer instance.
    
    Note: This function is kept for backward compatibility.
    Consider using OllamaServer directly instead.
    
    Returns:
        An OllamaServer instance with the server started
    """
    server = OllamaServer()
    server.start()
    return server

# For backward compatibility (deprecated, will be removed in a future version)
OllamaIntegration = OllamaServer  # Alias for backward compatibility (deprecated)

__all__ = [
    'OllamaServer',
    'OllamaModelManager',
    'get_ollama_server',
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
    'query_ollama',
    'list_ollama_models',
    'install_ollama_model',
    'start_ollama_server',
    # Deprecated, included for backward compatibility
    'OllamaIntegration',
    'get_ollama_integration',
]
