"""CLI utility functions."""

from .logging import configure_logging, get_default_log_file
from .models import (
    display_models,
    install_model_with_progress,
    uninstall_model_with_progress,
    display_model_info
)

__all__ = [
    # Logging utilities
    'configure_logging',
    'get_default_log_file',
    
    # Model utilities
    'display_models',
    'install_model_with_progress',
    'uninstall_model_with_progress',
    'display_model_info',
]
