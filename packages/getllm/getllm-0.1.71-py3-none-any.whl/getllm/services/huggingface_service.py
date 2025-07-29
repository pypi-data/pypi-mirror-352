"""
Service for interacting with Hugging Face models.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
import requests
from bs4 import BeautifulSoup

from ..utils.config import get_models_dir


class HuggingFaceService:
    """Service for interacting with Hugging Face models."""
    
    BASE_URL = "https://huggingface.co"
    API_URL = f"{BASE_URL}/api"
    
    def __init__(self):
        # Use the logs directory in the user's home directory for cache
        self.logs_dir = Path.home() / ".getllm" / "logs"
        self.cache_file = self.logs_dir / "huggingface_models.json"
        
        # Ensure the logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def search_models(self, query: str = None, limit: int = 20) -> List[Dict]:
        """Search for models on Hugging Face.
        
        Args:
            query: The search query (e.g., "bielik"). If None, returns all models.
            limit: Maximum number of results to return.
            
        Returns:
            A list of dictionaries containing model information.
        """
        # First try to load from cache
        cached_models = self._load_cached_models()
        
        # If no cache, try to fetch from API
        if not cached_models:
            cached_models = self._fetch_models_from_api()
            if cached_models:
                self._save_models_to_cache(cached_models)
        
        # Filter by query if provided
        if query:
            query = query.lower()
            cached_models = [
                model for model in cached_models
                if query in model.get('id', '').lower() or
                   query in model.get('description', '').lower() or
                   any(query in tag.lower() for tag in model.get('tags', []))
            ]
        
        return cached_models[:limit]
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get detailed information about a specific model.
        
        Args:
            model_id: The ID of the model (e.g., "TheBloke/Llama-2-7B-Chat-GGUF").
            
        Returns:
            Dictionary containing model information, or None if not found.
        """
        try:
            # Try to fetch model info from the API
            response = requests.get(f"{self.API_URL}/models/{model_id}")
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            # If API fails, try to find in cached models
            models = self._load_cached_models()
            for model in models:
                if model.get('id') == model_id:
                    return model
            return None
    
    def update_models_cache(self) -> bool:
        """Update the local cache of Hugging Face models.
        
        Returns:
            True if successful, False otherwise.
        """
        models = self._fetch_models_from_api()
        if models:
            return self._save_models_to_cache(models)
        return False
    
    def _fetch_models_from_api(self) -> List[Dict]:
        """Fetch models from the Hugging Face API.
        
        Returns:
            List of model dictionaries.
        """
        try:
            # This is a simplified example - in a real implementation,
            # you would want to handle pagination and potentially rate limiting
            response = requests.get(f"{self.API_URL}/models")
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            return []
    
    def _load_cached_models(self) -> List[Dict]:
        """Load models from the cache file.
        
        Returns:
            List of model dictionaries, or empty list if cache doesn't exist or is invalid.
        """
        if not self.cache_file.exists():
            return []
            
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def _save_models_to_cache(self, models: List[Dict]) -> bool:
        """Save models to the cache file.
        
        Args:
            models: List of model dictionaries to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
