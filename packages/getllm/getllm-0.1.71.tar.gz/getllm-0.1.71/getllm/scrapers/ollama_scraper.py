"""
Ollama Models Fetcher

This module provides functionality to fetch model information from the Ollama API.
"""

import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional, Any

# Ollama API endpoints - using local server
OLLAMA_API_BASE = "http://localhost:11434/api"
OLLAMA_TAGS_URL = f"{OLLAMA_API_BASE}/tags"  # Endpoint to list local models


class OllamaModelsScraper:
    """Fetcher for Ollama models using the Ollama API."""
    
    def __init__(self, api_base: str = None):
        """
        Initialize the OllamaModelsFetcher.
        
        Args:
            api_base: Base URL for the Ollama API. Defaults to the official API.
        """
        self.api_base = api_base or OLLAMA_API_BASE
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get all available models from the local Ollama server.
        
        Returns:
            List of model dictionaries with metadata.
        """
        try:
            # First, try to get the list of models from the local Ollama server
            response = requests.get(OLLAMA_TAGS_URL, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            models_data = data.get('models', [])
            
            if not models_data:
                print("No models found in local Ollama instance")
                return []
                
            models = []
            for model in models_data:
                try:
                    model_name = model.get('name', '')
                    if not model_name:
                        continue
                        
                    # Split model name into name and tag
                    if ':' in model_name:
                        name, tag = model_name.split(':', 1)
                    else:
                        name = model_name
                        tag = 'latest'
                    
                    model_info = {
                        'name': name,
                        'tag': tag,
                        'full_name': model_name,
                        'source': 'ollama',
                        'url': f"https://ollama.ai/library/{name}",
                        'metadata': {
                            'size': model.get('size', 0),
                            'digest': model.get('digest', ''),
                            'modified_at': model.get('modified_at', '')
                        }
                    }
                    
                    # Add model details if available
                    if 'details' in model:
                        details = model['details']
                        model_info['metadata'].update({
                            'format': details.get('format', ''),
                            'family': details.get('family', ''),
                            'parameter_size': details.get('parameter_size', ''),
                            'quantization_level': details.get('quantization_level', '')
                        })
                    
                    models.append(model_info)
                    
                except Exception as e:
                    print(f"Error processing model {model_name}: {e}")
                    continue
                    
            return models
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models from local Ollama server: {e}")
            return []
    
    def save_models_to_file(self, file_path: str) -> bool:
        """
        Save the scraped models to a JSON file.
        
        Args:
            file_path: Path to save the models JSON file.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            models = self.get_models()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving models to file: {e}")
            return False


def update_ollama_models_cache(file_path: Optional[str] = None) -> bool:
    """
    Update the local cache of Ollama models.
    
    Args:
        file_path: Optional path to save the cache file. If not provided,
                  will use the default cache path.
                  
    Returns:
        True if successful, False otherwise.
    """
    if file_path is None:
        # Create the cache directory if it doesn't exist
        cache_dir = os.path.join(os.path.expanduser('~'), '.getllm', 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        file_path = os.path.join(cache_dir, 'ollama_models.json')
    
    try:
        with OllamaModelsScraper() as scraper:
            models = scraper.get_models()
            if not models:
                print("❌ No models found in the Ollama library")
                return False
                
            # Save the models to the cache file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully updated Ollama models cache with {len(models)} models")
            return True
            
    except Exception as e:
        print(f"❌ Error updating Ollama models cache: {str(e)}")
        return False
    
    try:
        with OllamaModelsScraper() as scraper:
            return scraper.save_models_to_file(str(file_path))
    except Exception as e:
        print(f"Error updating Ollama models cache: {e}")
        return False
