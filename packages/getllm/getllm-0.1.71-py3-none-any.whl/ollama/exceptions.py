"""Custom exceptions for Ollama integration."""

class OllamaError(Exception):
    """Base exception for Ollama-related errors."""
    pass

class OllamaInstallationError(OllamaError):
    """Raised when there's an error installing Ollama."""
    pass

class OllamaStartupError(OllamaError):
    """Raised when the Ollama server fails to start."""
    pass

class ModelNotFoundError(OllamaError):
    """Raised when a requested model is not found."""
    pass

class ModelInstallationError(OllamaError):
    """Raised when there's an error installing a model."""
    pass

class ModelGenerationError(OllamaError):
    """Raised when there's an error generating a response."""
    pass

class APIError(OllamaError):
    """Raised when there's an error with the Ollama API."""
    pass

class AuthenticationError(OllamaError):
    """Raised when there's an authentication error with the Ollama API."""
    pass

class RateLimitExceededError(OllamaError):
    """Raised when the rate limit for the Ollama API is exceeded."""
    pass

class InsufficientDiskSpaceError(OllamaError):
    """Raised when there's not enough disk space to install a model."""
    pass

class ModelValidationError(OllamaError):
    """Raised when there's an error validating a model."""
    pass
