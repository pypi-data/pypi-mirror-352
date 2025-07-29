"""
Ollama API endpoint definitions.
"""

import logging
from typing import Dict, Any, List, Optional, Union

from ..exceptions import (
    APIError,
    ModelNotFoundError,
    ModelGenerationError
)
from .client import OllamaAPIClient

logger = logging.getLogger('getllm.ollama.api.endpoints')

# Global API client instance
_api_client = None

def get_api_client() -> OllamaAPIClient:
    """Get or create a global API client instance.
    
    Returns:
        OllamaAPIClient: The global API client instance
    """
    global _api_client
    if _api_client is None:
        _api_client = OllamaAPIClient()
    return _api_client

def set_api_client(client: OllamaAPIClient) -> None:
    """Set the global API client instance.
    
    Args:
        client: The API client instance to use
    """
    global _api_client
    _api_client = client

def generate_completion(
    model: str,
    prompt: str,
    **generation_params
) -> str:
    """Generate text using the specified model.
    
    Args:
        model: The model to use for generation
        prompt: The prompt to generate text from
        **generation_params: Additional parameters for text generation
        
    Returns:
        The generated text
        
    Raises:
        ModelNotFoundError: If the specified model is not found
        ModelGenerationError: If there's an error generating text
        APIError: For other API errors
    """
    client = get_api_client()
    try:
        response = client.generate(model, prompt, **generation_params)
        return response.get('response', '')
    except Exception as e:
        logger.error(f"Error in generate_completion: {e}")
        if isinstance(e, (ModelNotFoundError, ModelGenerationError, APIError)):
            raise
        raise ModelGenerationError(f"Failed to generate text: {e}") from e

def generate_chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    **generation_params
) -> str:
    """Generate a chat response using the specified model.
    
    Args:
        model: The model to use for generation
        messages: List of message dictionaries with 'role' and 'content' keys
        **generation_params: Additional parameters for text generation
        
    Returns:
        The generated chat response
        
    Raises:
        ModelNotFoundError: If the specified model is not found
        ModelGenerationError: If there's an error generating the response
        APIError: For other API errors
    """
    client = get_api_client()
    try:
        response = client.chat(model, messages, **generation_params)
        return response.get('message', {}).get('content', '')
    except Exception as e:
        logger.error(f"Error in generate_chat_completion: {e}")
        if isinstance(e, (ModelNotFoundError, ModelGenerationError, APIError)):
            raise
        raise ModelGenerationError(f"Failed to generate chat response: {e}") from e

def list_available_models() -> List[Dict[str, Any]]:
    """List all available models.
    
    Returns:
        List of model information dictionaries
        
    Raises:
        APIError: If there's an error listing models
    """
    client = get_api_client()
    try:
        return client.list_models()
    except Exception as e:
        logger.error(f"Error in list_available_models: {e}")
        if isinstance(e, APIError):
            raise
        raise APIError(f"Failed to list available models: {e}") from e

def check_model_availability(model_name: str) -> bool:
    """Check if a model is available.
    
    Args:
        model_name: Name of the model to check
        
    Returns:
        bool: True if the model is available, False otherwise
        
    Raises:
        APIError: If there's an error checking model availability
    """
    try:
        models = list_available_models()
        return any(model.get('name') == model_name for model in models)
    except Exception as e:
        logger.error(f"Error in check_model_availability: {e}")
        if isinstance(e, APIError):
            raise
        raise APIError(f"Failed to check model availability: {e}") from e

def install_model(model_name: str, **kwargs) -> bool:
    """Download a model from the Ollama model hub.
    
    Args:
        model_name: Name of the model to download
        **kwargs: Additional parameters for the pull operation
        
    Returns:
        bool: True if the model was downloaded successfully
        
    Raises:
        APIError: If there's an error downloading the model
    """
    client = get_api_client()
    try:
        return client.pull_model(model_name, **kwargs)
    except Exception as e:
        logger.error(f"Error in install_model: {e}")
        if isinstance(e, APIError):
            raise
        raise APIError(f"Failed to install model {model_name}: {e}") from e
