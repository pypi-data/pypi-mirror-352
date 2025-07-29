"""
Exceptions for the Ollama integration.
"""

class OllamaError(Exception):
    """Base exception for all Ollama integration errors."""
    pass

class OllamaInstallationError(OllamaError):
    """Raised when there's an error installing Ollama."""
    pass

class OllamaStartupError(OllamaError):
    """Raised when there's an error starting the Ollama server."""
    pass

class ModelError(OllamaError):
    """Base exception for model-related errors."""
    pass

class ModelNotFoundError(ModelError):
    """Raised when a specified model is not found."""
    pass

class ModelInstallationError(ModelError):
    """Raised when there's an error installing a model."""
    pass

class ModelGenerationError(ModelError):
    """Raised when there's an error generating content with a model."""
    pass

class APIError(OllamaError):
    """Raised when there's an error with the Ollama API."""
    pass

class AuthenticationError(APIError):
    """Raised when there's an authentication error with the API."""
    pass

class RateLimitExceededError(APIError):
    """Raised when the API rate limit is exceeded."""
    pass

class InsufficientDiskSpaceError(OllamaError):
    """Raised when there's not enough disk space for model operations."""
    pass

class ModelValidationError(ModelError):
    """Raised when a model fails validation."""
    pass
