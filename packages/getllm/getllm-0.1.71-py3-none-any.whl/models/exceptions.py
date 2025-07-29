"""
Custom exceptions for the getllm.models module.

This module defines custom exceptions used throughout the models package.
"""

class ModelError(Exception):
    """Base exception for all model-related errors."""
    pass

class ModelNotFoundError(ModelError):
    """Raised when a model is not found."""
    pass

class ModelInstallationError(ModelError):
    """Raised when there's an error installing a model."""
    pass

class ModelQueryError(ModelError):
    """Raised when there's an error querying a model."""
    pass

class ModelValidationError(ModelError):
    """Raised when there's a validation error with a model."""
    pass

class ModelLoadingError(ModelError):
    """Raised when there's an error loading a model."""
    pass

class ModelSavingError(ModelError):
    """Raised when there's an error saving a model."""
    pass

class ModelDeletionError(ModelError):
    """Raised when there's an error deleting a model."""
    pass
