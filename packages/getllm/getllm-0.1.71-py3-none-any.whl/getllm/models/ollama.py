"""
Ollama model manager for handling Ollama models.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
import subprocess

from .base import BaseModelManager
from ..utils.config import get_models_dir, get_models_metadata_path


class OllamaModelManager(BaseModelManager):
    """Manages Ollama models."""
    
    DEFAULT_MODELS = [
        {
            'name': 'llama3',
            'size': '8B',
            'description': 'Meta\'s Llama 3 8B model',
            'source': 'ollama',
            'format': 'gguf'
        },
        # Add more default models as needed
    ]
    
    def __init__(self):
        # Use the logs directory in the user's home directory for cache
        self.logs_dir = Path.home() / ".getllm" / "logs"
        self.cache_file = self.logs_dir / "ollama_models.json"
        self.models_metadata_file = get_models_metadata_path()
        
        # Set up models directory
        self.models_dir = Path.home() / ".ollama" / "models"
        
        # Ensure the directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize models cache
        self._models_cache = []
    
    def get_available_models(self, limit: Optional[int] = None, force_refresh: bool = False) -> List[Dict]:
        """
        Get available Ollama models.
        
        Args:
            limit: Maximum number of models to return. If None, returns all available models.
            force_refresh: If True, force refresh the cache
            
        Returns:
            List of model dictionaries with metadata.
        """
        # Try to load from cache if not forcing refresh
        if not force_refresh:
            cached_models = self._load_cached_models()
            if cached_models:
                return cached_models[:limit] if limit is not None else cached_models
        
        # Try to update the cache
        if self.update_models_cache():
            cached_models = self._load_cached_models()
            if cached_models:
                return cached_models[:limit] if limit is not None else cached_models
        
        # Fall back to default models if all else fails
        return self.DEFAULT_MODELS[:limit] if limit is not None else self.DEFAULT_MODELS
    
    def install_model(self, model_name: str) -> bool:
        """Install an Ollama model."""
        try:
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def list_installed_models(self) -> List[str]:
        """List installed Ollama models."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                return []
                
            # Parse the output to get model names
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            return [line.split()[0] for line in lines if line.strip()]
            
        except (subprocess.SubprocessError, FileNotFoundError):
            return []
    
    def update_models_cache(self) -> bool:
        """Update the local cache of Ollama models by scraping the Ollama library."""
        try:
            from ..scrapers.ollama_scraper import OllamaModelsScraper
            
            print("🔄 Fetching latest Ollama models...")
            with OllamaModelsScraper() as scraper:
                models = scraper.get_models()
                
                if not models:
                    print("⚠️ No models found. Using cached data if available.")
                    return False
                
                # Ensure the cache directory exists
                self.models_dir.mkdir(parents=True, exist_ok=True)
                
                # Save models to cache file
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'models': models,
                        'count': len(models),
                        'last_updated': datetime.utcnow().isoformat(),
                        'source': 'ollama',
                        'updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
                    }, f, indent=2)
                
                print(f"✅ Successfully cached {len(models)} Ollama models")
                return True
                
        except Exception as e:
            print(f"❌ Error updating Ollama models cache: {e}")
            return False
    
    def _load_cached_models(self) -> List[Dict]:
        """Load models from the cache file."""
        if not self.cache_file.exists():
            return []
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both old and new cache formats
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'models' in data:
                    return data['models']
                return []
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Error loading cached models: {e}")
            return []
    
    def search_models(self, query: str = None, limit: int = 20, force_refresh: bool = False) -> List[Dict]:
        """
        Search for models matching a query string.
        
        Args:
            query: The search query string
            limit: Maximum number of models to return
            force_refresh: If True, force refresh the cache before searching
            
        Returns:
            List of model dictionaries matching the query
        """
        # Get models, potentially forcing a refresh
        models = self.get_available_models(force_refresh=force_refresh)
        
        # If no query, return all models up to the limit
        if not query:
            return models[:limit]
        
        # Filter models by query across multiple fields
        query = query.lower()
        filtered_models = []
        
        for model in models:
            # Check if query matches any of the model's fields
            search_fields = [
                model.get('name', '').lower(),
                model.get('description', '').lower(),
                model.get('full_name', '').lower(),
                model.get('tag', '').lower(),
                ' '.join(model.get('metadata', {}).get('tags', [])).lower()
            ]
            
            # Check if query is in any of the search fields
            if any(query in field for field in search_fields if field):
                filtered_models.append(model)
                
                # Early exit if we've reached the limit
                if len(filtered_models) >= limit:
                    break
        
        return filtered_models[:limit]
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a specific model."""
        models = self.get_available_models()
        for model in models:
            if model.get('name') == model_name or model.get('id') == model_name:
                return model
        return None
