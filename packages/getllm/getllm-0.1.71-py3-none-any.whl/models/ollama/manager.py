"""
Ollama model manager implementation.
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
import requests
from requests.exceptions import RequestException

from getllm.exceptions import ModelError, ModelInstallationError, ModelNotFoundError, ModelQueryError
from ..base import BaseModelManager, ModelMetadata, ModelSource, ModelType


logger = logging.getLogger('getllm.models.ollama.manager')

# Default Ollama API endpoint
OLLAMA_API_BASE = "http://localhost:11434/api"

# Default model tags to filter by
DEFAULT_TAGS = [
    "text-generation",
    "code",
    "chat",
    "instruct"
]


class OllamaModelManager(BaseModelManager):
    """Manager for Ollama models."""
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        base_url: Optional[str] = None,
        ollama_path: Optional[str] = None
    ):
        """Initialize the Ollama model manager.
        
        Args:
            cache_dir: Directory to cache model metadata
            base_url: Base URL for the Ollama API
            ollama_path: Path to the Ollama executable
        """
        self.cache_dir = cache_dir or os.path.join(
            os.path.expanduser("~"), ".cache", "getllm", "ollama"
        )
        self.base_url = base_url or OLLAMA_API_BASE
        
        # Set up models directory
        self.models_dir = os.path.join(os.path.expanduser('~'), '.ollama', 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        self.ollama_path = ollama_path or os.getenv("OLLAMA_PATH", "ollama")
        self._models_cache: Dict[str, Dict[str, Any]] = {}
        self._is_installed = self._check_ollama_installed()
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
    
    @property
    def cache_file(self) -> str:
        """Get the path to the models cache file."""
        return os.path.join(self.cache_dir, "models.json")
    
    def _check_ollama_installed(self) -> bool:
        """Check if Ollama is installed and accessible."""
        try:
            result = subprocess.run(
                [self.ollama_path, "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _load_models_cache(self) -> None:
        """Load models from the cache file."""
        if not os.path.exists(self.cache_file):
            self._models_cache = {}
            return
            
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self._models_cache = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load models cache: {e}")
            self._models_cache = {}
    
    def _save_models_cache(self) -> None:
        """Save models to the cache file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._models_cache, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save models cache: {e}")
    
    def _fetch_models_from_api(self) -> List[Dict[str, Any]]:
        """Fetch available models from the Ollama API.
        
        Returns:
            List of model information dictionaries
            
        Raises:
            ModelError: If there's an error fetching models
        """
        if not self._is_installed:
            raise ModelError("Ollama is not installed or not in PATH")
        
        try:
            # First, check if the server is running
            response = requests.get(f"{self.base_url}/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            
            # If not, try to start the server
            logger.info("Ollama server not running, attempting to start it...")
            subprocess.Popen(
                [self.ollama_path, "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            import time
            for _ in range(10):  # Try for up to 10 seconds
                try:
                    response = requests.get(f"{self.base_url}/tags", timeout=1)
                    if response.status_code == 200:
                        data = response.json()
                        return data.get("models", [])
                except requests.RequestException:
                    pass
                time.sleep(1)
            
            raise ModelError("Failed to start Ollama server")
            
        except RequestException as e:
            raise ModelError(f"Failed to fetch models from Ollama API: {e}") from e
    
    def _fetch_model_info(self, model_name: str) -> Dict[str, Any]:
        """Fetch information about a specific model.
        
        Args:
            model_name: The name of the model
            
        Returns:
            Dictionary containing model information
            
        Raises:
            ModelNotFoundError: If the model is not found
            ModelError: If there's an error fetching the model info
        """
        try:
            # First check local models
            response = requests.get(
                f"{self.base_url}/tags",
                timeout=10
            )
            response.raise_for_status()
            
            models = response.json().get("models", [])
            for model in models:
                if model.get("name") == model_name:
                    return model
            
            # If not found locally, try to pull it
            logger.info(f"Model {model_name} not found locally, attempting to pull...")
            pull_response = requests.post(
                f"{self.base_url}/pull",
                json={"name": model_name},
                stream=True
            )
            
            if pull_response.status_code != 200:
                error_msg = f"Failed to pull model {model_name}"
                if pull_response.text:
                    error_msg += f": {pull_response.text}"
                raise ModelError(error_msg)
            
            # Process the streaming response
            for line in pull_response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if data.get("status") == "success":
                            # Model was pulled successfully, get its info
                            response = requests.get(
                                f"{self.base_url}/tags",
                                timeout=10
                            )
                            response.raise_for_status()
                            
                            for model in response.json().get("models", []):
                                if model.get("name") == model_name:
                                    return model
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse response line: {line}")
            
            raise ModelNotFoundError(f"Model {model_name} not found after pull attempt")
            
        except RequestException as e:
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                raise ModelNotFoundError(f"Model '{model_name}' not found")
            raise ModelError(f"Failed to fetch model info: {e}") from e
    
    def search_models(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        sort: str = "downloads",
        direction: str = "-1"
    ) -> List[Dict[str, Any]]:
        """Search for models in the Ollama library.
        
        Args:
            query: Search query string
            tags: List of tags to filter by (not currently used in Ollama)
            limit: Maximum number of results to return
            sort: Field to sort by (not currently used in Ollama)
            direction: Sort direction (not currently used in Ollama)
            
        Returns:
            List of model information dictionaries
            
        Raises:
            ModelError: If there's an error searching for models
        """
        try:
            models = self._fetch_models_from_api()
            
            # Filter by query if provided
            if query:
                query = query.lower()
                models = [
                    model for model in models 
                    if query in model.get("name", "").lower()
                ]
            
            # Apply limit
            if limit > 0:
                models = models[:limit]
                
            return models
            
        except Exception as e:
            error_msg = f"Failed to search Ollama models: {e}"
            logger.error(error_msg)
            raise ModelError(error_msg) from e
    
    def list_models(self) -> List[ModelMetadata]:
        """List all available models.
        
        Returns:
            List of ModelMetadata objects
        """
        try:
            models = self._fetch_models_from_api()
            return [self._model_dict_to_metadata(model) for model in models]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            # Fall back to cache if available
            self._load_models_cache()
            return [
                self._model_dict_to_metadata(model_info)
                for model_info in self._models_cache.values()
            ]
    
    def get_model(self, model_name: str) -> Optional[ModelMetadata]:
        """Get a model by name.
        
        Args:
            model_name: The name of the model
            
        Returns:
            ModelMetadata if found, None otherwise
        """
        try:
            model_info = self._fetch_model_info(model_name)
            return self._model_dict_to_metadata(model_info)
        except ModelNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error getting model {model_name}: {e}")
            return None
    
    def install_model(self, model_name: str, **kwargs) -> bool:
        """Install a model.
        
        Args:
            model_name: The name of the model to install
            **kwargs: Additional installation options
                - insecure: Use insecure registry
                - insecure_registry: Insecure registry URL
                - username: Registry username
                - password: Registry password
                - stream: Whether to stream the download
                
        Returns:
            bool: True if installation was successful
            
        Raises:
            ModelInstallationError: If installation fails
        """
        if not self._is_installed:
            raise ModelInstallationError("Ollama is not installed or not in PATH")
        
        try:
            logger.info(f"Pulling model: {model_name}")
            
            # Prepare pull request
            pull_data = {"name": model_name}
            if "insecure" in kwargs:
                pull_data["insecure"] = kwargs["insecure"]
            if "insecure_registry" in kwargs:
                pull_data["insecure_registry"] = kwargs["insecure_registry"]
            if "username" in kwargs and "password" in kwargs:
                pull_data["username"] = kwargs["username"]
                pull_data["password"] = kwargs["password"]
            
            stream = kwargs.get("stream", True)
            
            if stream:
                # Stream the download
                response = requests.post(
                    f"{self.base_url}/pull",
                    json=pull_data,
                    stream=True,
                    timeout=60
                )
                
                if response.status_code != 200:
                    error_msg = f"Failed to pull model {model_name}"
                    if response.text:
                        error_msg += f": {response.text}"
                    raise ModelInstallationError(error_msg)
                
                # Process the streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get("status"):
                                logger.info(f"Status: {data['status']}")
                            if data.get("error"):
                                raise ModelInstallationError(f"Error pulling model: {data['error']}")
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse response line: {line}")
            else:
                # Non-streaming pull
                response = requests.post(
                    f"{self.base_url}/pull",
                    json=pull_data,
                    timeout=300  # 5 minute timeout for non-streaming
                )
                response.raise_for_status()
            
            logger.info(f"Successfully installed model: {model_name}")
            
            # Update cache
            try:
                model_info = self._fetch_model_info(model_name)
                self._models_cache[model_name] = model_info
                self._save_models_cache()
            except Exception as e:
                logger.warning(f"Failed to update model cache: {e}")
            
            return True
            
        except RequestException as e:
            error_msg = f"Failed to install model {model_name}: {e}"
            logger.error(error_msg)
            raise ModelInstallationError(error_msg) from e
    
    def uninstall_model(self, model_name: str) -> bool:
        """Uninstall a model.
        
        Args:
            model_name: The name of the model to uninstall
            
        Returns:
            bool: True if uninstallation was successful
        """
        if not self._is_installed:
            logger.warning("Ollama is not installed or not in PATH")
            return False
        
        try:
            logger.info(f"Deleting model: {model_name}")
            
            response = requests.delete(
                f"{self.base_url}/delete",
                json={"name": model_name},
                timeout=30
            )
            
            if response.status_code == 200:
                # Update cache
                self._load_models_cache()
                if model_name in self._models_cache:
                    del self._models_cache[model_name]
                    self._save_models_cache()
                return True
            
            if response.status_code == 404:
                logger.warning(f"Model {model_name} not found")
                return False
                
            error_msg = f"Failed to delete model {model_name}"
            if response.text:
                error_msg += f": {response.text}"
            logger.error(error_msg)
            return False
            
        except RequestException as e:
            logger.error(f"Error deleting model {model_name}: {e}")
            return False
    
    def is_model_installed(self, model_name: str) -> bool:
        """Check if a model is installed.
        
        Args:
            model_name: The name of the model to check
            
        Returns:
            bool: True if the model is installed
        """
        try:
            models = self.list_models()
            return any(model.id == model_name for model in models)
        except Exception as e:
            logger.error(f"Error checking if model {model_name} is installed: {e}")
            return False
    
    def _model_dict_to_metadata(self, model_info: Dict[str, Any]) -> ModelMetadata:
        """Convert a model info dictionary to a ModelMetadata object.
        
        Args:
            model_info: Dictionary containing model information
            
        Returns:
            ModelMetadata object
        """
        model_name = model_info.get("name", "")
        
        # Determine model type
        model_type = ModelType.TEXT
        if any(tag in model_name.lower() for tag in ["chat", "instruct"]):
            model_type = ModelType.CHAT
        elif "code" in model_name.lower():
            model_type = ModelType.CODE
        
        # Get model size if available
        size = model_info.get("size")
        
        # Get parameter count if available in the model name
        parameters = None
        import re
        param_match = re.search(r'(\d+\.?\d*)(B|M)', model_name.upper())
        if param_match:
            value, unit = param_match.groups()
            value = float(value)
            if unit == 'B':
                parameters = int(value * 1_000_000_000)
            elif unit == 'M':
                parameters = int(value * 1_000_000)
        
        return ModelMetadata(
            id=model_name,
            name=model_name.split(':')[0],  # Remove tag if present
            description=model_info.get("details", {}).get("description", ""),
            source=ModelSource.OLLAMA,
            model_type=model_type,
            size=size,
            parameters=parameters,
            tags=model_info.get("details", {}).get("tags", []),
            config={
                "modified_at": model_info.get("modified_at"),
                "size": model_info.get("size"),
                "digest": model_info.get("digest")
            }
        )
        
    def query(
        self,
        prompt: str,
        model: str = "llama3",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Query the model with a prompt.
        
        Args:
            prompt: The input prompt
            model: The model to use (default: "llama3")
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional parameters for the API call
            
        Returns:
            The generated text response
            
        Raises:
            ModelError: If there's an error querying the model
        """
        if not self._is_installed:
            raise ModelError("Ollama is not installed or not in PATH")
            
        try:
            # Ensure the model is available
            if not self.is_model_installed(model):
                logger.info(f"Model {model} not found, attempting to pull...")
                if not self.install_model(model):
                    raise ModelError(f"Failed to install model: {model}")
            
            # Prepare the request data
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": max(0.01, min(1.0, temperature)),
                }
            }
            
            # Add any additional parameters
            if "options" in kwargs:
                data["options"].update(kwargs["options"])
                del kwargs["options"]
            data.update(kwargs)
            
            # Make the API request
            response = requests.post(
                f"{self.base_url}/generate",
                json=data,
                timeout=300  # 5 minute timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except requests.RequestException as e:
            error_msg = f"Error querying model {model}: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get('error', '')
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {e.response.text}"
            raise ModelError(error_msg) from e


def get_ollama_model_manager(**kwargs) -> OllamaModelManager:
    """Get an OllamaModelManager instance with default settings.
    
    Args:
        **kwargs: Additional arguments to pass to OllamaModelManager
        
    Returns:
        OllamaModelManager instance
    """
    return OllamaModelManager(**kwargs)
