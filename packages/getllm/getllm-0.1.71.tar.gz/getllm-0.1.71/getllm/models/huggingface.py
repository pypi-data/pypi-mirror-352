"""
Hugging Face model manager for handling Hugging Face models.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
import requests
from bs4 import BeautifulSoup

from .base import BaseModelManager
from ..utils.config import get_models_dir, get_models_metadata_path


class HuggingFaceModelManager(BaseModelManager):
    """Manages Hugging Face models."""
    
    DEFAULT_MODELS = [
        {
            'id': 'TheBloke/Llama-2-7B-Chat-GGUF',
            'name': 'llama-2-7b-chat',
            'size': '7B',
            'description': 'Llama 2 7B Chat model in GGUF format',
            'source': 'huggingface',
            'format': 'gguf'
        },
        # Add more default models as needed
    ]
    
    def __init__(self):
        # Use the logs directory in the user's home directory for cache
        self.logs_dir = Path.home() / ".getllm" / "logs"
        self.cache_file = self.logs_dir / "huggingface_models.json"
        self.models_metadata_file = get_models_metadata_path()
        
        # Ensure the logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def get_available_models(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get available Hugging Face models.
        
        Args:
            limit: Maximum number of models to return. If None, returns all available models.
            
        Returns:
            List of model dictionaries with metadata.
        """
        # First try to load from cache
        cached_models = self._load_cached_models()
        if cached_models:
            return cached_models[:limit] if limit is not None else cached_models
        
        # Fall back to default models if cache is empty
        return self.DEFAULT_MODELS[:limit] if limit is not None else self.DEFAULT_MODELS
    
    def install_model(self, model_name: str) -> bool:
        """Install a Hugging Face model."""
        # Implementation for installing HF models
        # This is a placeholder - actual implementation would use the Hugging Face Hub
        print(f"Installing Hugging Face model: {model_name}")
        return False  # Not implemented yet
    
    def list_installed_models(self) -> List[str]:
        """List installed Hugging Face models."""
        # Implementation to list installed models
        return []
    
    def search_models(self, query: str = None, limit: int = 20) -> List[Dict]:
        """Search for models on Hugging Face."""
        # Implementation for searching HF models
        models = self.get_available_models()
        if not query:
            return models[:limit]
        
        query = query.lower()
        return [
            model for model in models 
            if query in model.get('name', '').lower() or 
               query in model.get('description', '').lower()
        ][:limit]
    
    def update_models_cache(self) -> bool:
        """Update the local cache of Hugging Face models."""
        # Implementation to fetch and update the models cache
        return False  # Not implemented yet
    
    def _load_cached_models(self) -> List[Dict]:
        """Load models from the cache file."""
        if not self.cache_file.exists():
            return []
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a specific model."""
        models = self.get_available_models()
        for model in models:
            if model.get('name') == model_name or model.get('id') == model_name:
                return model
        return None
