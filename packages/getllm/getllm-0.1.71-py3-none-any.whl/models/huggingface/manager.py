"""
Hugging Face model manager implementation.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import requests
from requests.exceptions import RequestException

from getllm.exceptions import ModelError, ModelInstallationError, ModelNotFoundError
from ..base import BaseModelManager, ModelMetadata, ModelSource, ModelType


logger = logging.getLogger('getllm.models.huggingface.manager')

# Default Hugging Face API endpoint
HF_API_BASE = "https://huggingface.co/api"

# Default model tags to filter by
DEFAULT_TAGS = [
    "text-generation",
    "text2text-generation",
    "text-classification",
    "fill-mask"
]

# Default model parameters to include in search
DEFAULT_PARAMS = {
    "sort": "downloads",
    "direction": "-1",
    "limit": "50",
    "full": "true"
}


class HuggingFaceModelManager(BaseModelManager):
    """Manager for Hugging Face models."""
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        hf_token: Optional[str] = None
    ):
        """Initialize the Hugging Face model manager.
        
        Args:
            cache_dir: Directory to cache model metadata
            hf_token: Hugging Face authentication token
        """
        self.cache_dir = cache_dir or os.path.join(
            os.path.expanduser("~"), ".cache", "getllm", "huggingface"
        )
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self._models_cache: Dict[str, Dict[str, Any]] = {}
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
    
    @property
    def cache_file(self) -> str:
        """Get the path to the models cache file."""
        return os.path.join(self.cache_dir, "models.json")
    
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
    
    def _fetch_model_info(self, model_id: str) -> Dict[str, Any]:
        """Fetch model information from the Hugging Face Hub.
        
        Args:
            model_id: The model ID (e.g., 'gpt2')
            
        Returns:
            Dictionary containing model information
            
        Raises:
            ModelNotFoundError: If the model is not found
            ModelError: If there's an error fetching the model info
        """
        url = f"{HF_API_BASE}/models/{model_id}"
        headers = {}
        
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            if hasattr(e.response, 'status_code') and e.response.status_code == 404:
                raise ModelNotFoundError(f"Model '{model_id}' not found on Hugging Face Hub")
            raise ModelError(f"Failed to fetch model info: {e}") from e
    
    def search_models(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        sort: str = "downloads",
        direction: str = "-1"
    ) -> List[Dict[str, Any]]:
        """Search for models on the Hugging Face Hub.
        
        Args:
            query: Search query string
            tags: List of tags to filter by
            limit: Maximum number of results to return
            sort: Field to sort by (e.g., 'downloads', 'likes', 'modified')
            direction: Sort direction ('1' for ascending, '-1' for descending)
            
        Returns:
            List of model information dictionaries
            
        Raises:
            ModelError: If there's an error searching for models
        """
        params = {
            "search": query or "",
            "tags": ",".join(tags or DEFAULT_TAGS),
            "sort": sort,
            "direction": direction,
            "limit": str(limit),
            "full": "true"
        }
        
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        try:
            response = requests.get(
                f"{HF_API_BASE}/models",
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise ModelError(f"Failed to search models: {e}") from e
    
    def list_models(self) -> List[ModelMetadata]:
        """List all available models.
        
        Returns:
            List of ModelMetadata objects
        """
        self._load_models_cache()
        return [
            self._model_dict_to_metadata(model_id, model_info)
            for model_id, model_info in self._models_cache.items()
        ]
    
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get a model by ID.
        
        Args:
            model_id: The model ID
            
        Returns:
            ModelMetadata if found, None otherwise
        """
        self._load_models_cache()
        model_info = self._models_cache.get(model_id)
        if model_info:
            return self._model_dict_to_metadata(model_id, model_info)
        return None
    
    def install_model(self, model_id: str, **kwargs) -> bool:
        """Install a model.
        
        Args:
            model_id: The model ID to install
            **kwargs: Additional installation options
                - revision: The model revision to install
                - cache_dir: Directory to cache the model
                - force_download: Whether to force download
                - resume_download: Whether to resume downloads
                - proxies: Dictionary of proxies
                - local_files_only: Whether to use local files only
                - use_auth_token: Authentication token
                
        Returns:
            bool: True if installation was successful
            
        Raises:
            ModelInstallationError: If installation fails
        """
        try:
            from transformers import AutoModel, AutoTokenizer
            
            # Get model info first
            model_info = self._fetch_model_info(model_id)
            
            # Update cache
            self._models_cache[model_id] = model_info
            self._save_models_cache()
            
            # Download the model
            logger.info(f"Downloading model: {model_id}")
            
            # Download tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                **{k: v for k, v in kwargs.items() if k in [
                    'revision', 'cache_dir', 'force_download',
                    'resume_download', 'proxies', 'local_files_only',
                    'use_auth_token'
                ]}
            )
            
            # Download model
            model = AutoModel.from_pretrained(
                model_id,
                **{k: v for k, v in kwargs.items() if k in [
                    'revision', 'cache_dir', 'force_download',
                    'resume_download', 'proxies', 'local_files_only',
                    'use_auth_token'
                ]}
            )
            
            logger.info(f"Successfully installed model: {model_id}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to install model {model_id}: {e}"
            logger.error(error_msg)
            raise ModelInstallationError(error_msg) from e
    
    def uninstall_model(self, model_id: str) -> bool:
        """Uninstall a model.
        
        Args:
            model_id: The model ID to uninstall
            
        Returns:
            bool: True if uninstallation was successful
        """
        # Note: This only removes the model from the cache, not the actual files
        # since they're managed by the transformers library's cache
        self._load_models_cache()
        if model_id in self._models_cache:
            del self._models_cache[model_id]
            self._save_models_cache()
            return True
        return False
    
    def is_model_installed(self, model_id: str) -> bool:
        """Check if a model is installed.
        
        Args:
            model_id: The model ID to check
            
        Returns:
            bool: True if the model is installed
        """
        try:
            from transformers import AutoConfig, AutoTokenizer
            
            # Try to load the model config
            AutoConfig.from_pretrained(model_id)
            return True
        except Exception:
            return False
    
    def _model_dict_to_metadata(
        self,
        model_id: str,
        model_info: Dict[str, Any]
    ) -> ModelMetadata:
        """Convert a model info dictionary to a ModelMetadata object.
        
        Args:
            model_id: The model ID
            model_info: Dictionary containing model information
            
        Returns:
            ModelMetadata object
        """
        # Determine model type
        model_type = ModelType.TEXT
        if any(tag.startswith('text2text') for tag in model_info.get('tags', [])):
            model_type = ModelType.TEXT2TEXT
        elif any(tag.startswith('text-classification') for tag in model_info.get('tags', [])):
            model_type = ModelType.TEXT
        
        # Get model size
        size = None
        if 'safetensors' in model_info.get('siblings', []):
            for sibling in model_info['siblings']:
                if sibling.get('rfilename', '').endswith('.safetensors'):
                    size = sibling.get('size', size)
                    break
        
        # Get parameter count if available
        parameters = None
        if 'config' in model_info and 'num_parameters' in model_info['config']:
            parameters = model_info['config']['num_parameters']
        
        return ModelMetadata(
            id=model_id,
            name=model_info.get('modelId', model_id),
            description=model_info.get('cardData', {}).get('description', ''),
            source=ModelSource.HUGGINGFACE,
            model_type=model_type,
            size=size,
            parameters=parameters,
            tags=model_info.get('tags', []),
            config=model_info.get('config', {})
        )


def get_hf_model_manager(**kwargs) -> HuggingFaceModelManager:
    """Get a HuggingFaceModelManager instance with default settings.
    
    Args:
        **kwargs: Additional arguments to pass to HuggingFaceModelManager
        
    Returns:
        HuggingFaceModelManager instance
    """
    return HuggingFaceModelManager(**kwargs)
