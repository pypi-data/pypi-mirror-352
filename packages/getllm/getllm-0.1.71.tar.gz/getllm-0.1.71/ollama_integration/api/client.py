"""
Ollama API client implementation.
"""

import os
import logging
import requests
from typing import Dict, Any, List, Optional, Union

from ..exceptions import (
    APIError,
    AuthenticationError,
    RateLimitExceededError,
    ModelNotFoundError,
    ModelGenerationError
)

logger = logging.getLogger('getllm.ollama.api.client')

class OllamaAPIClient:
    """Client for interacting with the Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434/api", api_key: Optional[str] = None):
        """Initialize the API client.
        
        Args:
            base_url: Base URL for the Ollama API
            api_key: API key for authentication (if required)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv('OLLAMA_API_KEY')
        self.session = requests.Session()
        
        # Set up session headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if self.api_key:
            self.session.headers['Authorization'] = f"Bearer {self.api_key}"
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Ollama API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests.request()
            
        Returns:
            The parsed JSON response
            
        Raises:
            APIError: For API-level errors
            AuthenticationError: For authentication errors
            RateLimitExceededError: For rate limiting errors
            requests.RequestException: For other request errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                raise RateLimitExceededError(
                    f"Rate limit exceeded. Please try again after {retry_after} seconds"
                )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication token")
            
            # Handle not found errors
            if response.status_code == 404:
                error_data = response.json()
                if 'error' in error_data and 'model' in error_data['error'].lower():
                    raise ModelNotFoundError(error_data['error'])
                raise APIError(f"Resource not found: {error_data.get('error', 'Unknown error')}")
            
            # Handle other error status codes
            if response.status_code >= 400:
                error_data = response.json()
                raise APIError(
                    f"API request failed with status {response.status_code}: "
                    f"{error_data.get('error', 'Unknown error')}"
                )
            
            # Return parsed JSON for successful responses
            return response.json()
            
        except requests.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise APIError("Invalid JSON response from server") from e
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise APIError(f"Request failed: {e}") from e
    
    def generate(
        self,
        model: str,
        prompt: str,
        **generation_params
    ) -> Dict[str, Any]:
        """Generate text using the specified model.
        
        Args:
            model: The model to use for generation
            prompt: The prompt to generate text from
            **generation_params: Additional parameters for text generation
            
        Returns:
            The generated text and metadata
            
        Raises:
            ModelGenerationError: If there's an error generating text
            APIError: For other API errors
        """
        try:
            return self._request(
                'POST',
                '/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    **generation_params
                },
                timeout=60
            )
        except APIError as e:
            if 'model' in str(e).lower() and 'not found' in str(e).lower():
                raise ModelNotFoundError(f"Model not found: {model}") from e
            raise ModelGenerationError(f"Failed to generate text: {e}") from e
    
    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **generation_params
    ) -> Dict[str, Any]:
        """Generate a chat response using the specified model.
        
        Args:
            model: The model to use for generation
            messages: List of message dictionaries with 'role' and 'content' keys
            **generation_params: Additional parameters for text generation
            
        Returns:
            The generated response and metadata
            
        Raises:
            ModelGenerationError: If there's an error generating the response
            APIError: For other API errors
        """
        try:
            return self._request(
                'POST',
                '/chat',
                json={
                    'model': model,
                    'messages': messages,
                    **generation_params
                },
                timeout=60
            )
        except APIError as e:
            if 'model' in str(e).lower() and 'not found' in str(e).lower():
                raise ModelNotFoundError(f"Model not found: {model}") from e
            raise ModelGenerationError(f"Failed to generate chat response: {e}") from e
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models.
        
        Returns:
            List of model information dictionaries
            
        Raises:
            APIError: If there's an error listing models
        """
        response = self._request('GET', '/tags')
        return response.get('models', [])
    
    def get_model(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model.
        
        Args:
            model_name: Name of the model to get information about
            
        Returns:
            Model information dictionary
            
        Raises:
            ModelNotFoundError: If the model is not found
            APIError: For other API errors
        """
        try:
            models = self.list_models()
            for model in models:
                if model.get('name') == model_name:
                    return model
            raise ModelNotFoundError(f"Model not found: {model_name}")
        except APIError as e:
            raise APIError(f"Failed to get model info: {e}") from e
    
    def pull_model(self, model_name: str, **kwargs) -> bool:
        """Download a model from the Ollama model hub.
        
        Args:
            model_name: Name of the model to download
            **kwargs: Additional parameters for the pull operation
            
        Returns:
            bool: True if the model was downloaded successfully
            
        Raises:
            APIError: If there's an error downloading the model
        """
        try:
            self._request(
                'POST',
                '/pull',
                json={
                    'name': model_name,
                    **kwargs
                },
                stream=True
            )
            return True
        except APIError as e:
            raise APIError(f"Failed to pull model {model_name}: {e}") from e
