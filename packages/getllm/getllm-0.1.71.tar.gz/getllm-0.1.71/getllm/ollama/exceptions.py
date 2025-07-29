"""
Custom exceptions for the Ollama integration.
"""

class OllamaError(Exception):
    """Base exception for all Ollama-related errors."""
    pass

class OllamaInstallationError(OllamaError):
    """Raised when there's an error with the Ollama installation."""
    pass

class OllamaStartupError(OllamaError):
    """Raised when there's an error starting the Ollama server."""
    pass

class ModelNotFoundError(OllamaError):
    """Raised when a specified model is not found."""
    pass

class InstallationError(OllamaError):
    """Raised when there's an error during installation."""
    pass

class ModelGenerationError(OllamaError):
    """Raised when there's an error during model generation."""
    pass

class APIError(OllamaError):
    """Raised when there's an error with the Ollama API."""
    pass

class AuthenticationError(OllamaError):
    """Raised when there's an authentication error with the Ollama API."""
    pass

class RateLimitExceededError(OllamaError):
    """Raised when the rate limit for the Ollama API has been exceeded."""
    pass

class InsufficientDiskSpaceError(OllamaError):
    """Raised when there's not enough disk space for an operation."""
    def __init__(self, message, available=None, required=None):
        super().__init__(message)
        self.available = available
        self.required = required

class ModelValidationError(OllamaError):
    """Raised when there's an error validating a model."""
    pass

class ServerError(OllamaError):
    """Raised when there's an error with the Ollama server."""
    pass

class DiskSpaceError(OllamaError):
    """Raised when there's not enough disk space for an operation."""
    def __init__(self, message, available_gb=None, required_gb=None):
        super().__init__(message)
        self.available_gb = available_gb
        self.required_gb = required_gb

class ModelInstallationError(OllamaError):
    """Raised when there's an error installing a model."""
    pass
