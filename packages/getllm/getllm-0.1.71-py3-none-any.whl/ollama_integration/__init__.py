"""
Ollama Integration for PyLLM

This package provides integration with Ollama for high-quality code generation.
It handles model management, automatic installation, and fallback mechanisms.
"""

from .client import OllamaClient
from .models import OllamaModelManager
from .server import OllamaServer
from .api import (
    generate_completion,
    generate_chat_completion,
    list_available_models,
    check_model_availability
)
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

# For backward compatibility
OllamaIntegration = OllamaClient

__all__ = [
    # Main classes
    'OllamaClient',
    'OllamaModelManager',
    'OllamaServer',
    'OllamaIntegration',  # For backward compatibility
    
    # API functions
    'generate_completion',
    'generate_chat_completion',
    'list_available_models',
    'check_model_availability',
    
    # Exceptions
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
    'ModelValidationError'
]
