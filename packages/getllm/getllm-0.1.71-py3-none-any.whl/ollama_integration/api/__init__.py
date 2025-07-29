"""
Ollama API client and endpoints.
"""

from .client import OllamaAPIClient
from .endpoints import (
    generate_completion,
    generate_chat_completion,
    list_available_models,
    check_model_availability
)

__all__ = [
    'OllamaAPIClient',
    'generate_completion',
    'generate_chat_completion',
    'list_available_models',
    'check_model_availability'
]
