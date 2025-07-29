"""
Hugging Face model cache management.

This module handles caching of Hugging Face model metadata to improve performance
and reduce API calls to the Hugging Face Hub.
"""

import os
import json
import logging
from typing import List, Dict, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

logger = logging.getLogger('getllm.models.huggingface.cache')

# Headers to avoid 403 Forbidden errors
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_hf_models_cache_path() -> str:
    """Get the path to the Hugging Face models cache file."""
    cache_dir = os.path.join(os.path.expanduser('~'), '.getllm')
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, 'hf_models.json')

def extract_model_size(model_info: Dict) -> str:
    """Extract model size from model info."""
    # Try to get size from tags
    for tag in model_info.get('tags', []):
        if any(x in str(tag).lower() 
               for x in ['1b', '1.4b', '2b', '3b', '4b', '7b', '8b', '13b', '20b', '30b', '40b', '65b', '70b']):
            return str(tag).upper()
    
    # Try to get size from model ID or name
    name = str(model_info.get('id', '')).lower()
    for size in ['1b', '1.4b', '2b', '3b', '4b', '7b', '8b', '13b', '20b', '30b', '40b', '65b', '70b']:
        if size in name:
            return size.upper()
    
    # Try to get size from description
    description = str(model_info.get('description', '')).lower()
    for size in ['1b', '1.4b', '2b', '3b', '4b', '7b', '8b', '13b', '20b', '30b', '40b', '65b', '70b']:
        if size in description:
            return size.upper()
    
    return 'Unknown'

def load_huggingface_models_from_cache() -> List[Dict]:
    """
    Load Hugging Face models from the cache file.
    
    Returns:
        A list of Hugging Face models, or an empty list if the cache file doesn't exist or is invalid.
    """
    try:
        cache_file = get_hf_models_cache_path()
        if not os.path.exists(cache_file):
            logger.debug("No Hugging Face cache file found")
            return []
            
        with open(cache_file, 'r', encoding='utf-8') as f:
            models = json.load(f)
            if not isinstance(models, list):
                logger.warning("Invalid cache format: expected a list of models")
                return []
            return models
            
    except Exception as e:
        logger.warning(f"Error loading Hugging Face models from cache: {e}")
        return []

def update_huggingface_models_cache(limit: int = 50) -> Tuple[bool, str]:
    """
    Update the Hugging Face models cache by fetching from the HF website.
    
    Args:
        limit: Maximum number of models to fetch
        
    Returns:
        A tuple of (success, message)
    """
    def fetch_from_api() -> Tuple[bool, str, List[Dict]]:
        """Try to fetch models from Hugging Face API."""
        try:
            api_url = "https://huggingface.co/api/models"
            params = {
                'search': 'GGUF',
                'sort': 'downloads',
                'direction': '-1',
                'limit': min(limit, 100),
                'full': 'false'
            }
            
            response = requests.get(api_url, headers=HEADERS, params=params, timeout=30)
            response.raise_for_status()
            api_models = response.json()
            
            models = []
            for model in api_models:
                models.append({
                    'id': model.get('modelId', ''),
                    'name': model.get('modelId', '').split('/')[-1],
                    'author': model.get('author', ''),
                    'description': model.get('cardData', {}).get('description', ''),
                    'downloads': model.get('downloads', 0),
                    'likes': model.get('likes', 0),
                    'tags': model.get('tags', []) + (['gguf'] if 'gguf' not in model.get('tags', []) else [])
                })
            
            return True, f"Fetched {len(models)} models from API", models
            
        except Exception as e:
            logger.warning(f"HF API request failed: {e}")
            return False, f"API request failed: {e}", []
    
    def fetch_from_web() -> Tuple[bool, str, List[Dict]]:
        """Fallback to web scraping if API fails."""
        try:
            url = "https://huggingface.co/models?sort=trending&search=GGUF"
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            model_cards = soup.find_all('article', {'class': 'card'})
            
            models = []
            for card in tqdm(model_cards[:limit], desc="Fetching models"):
                try:
                    model_id = card.find('a')['href'].strip('/')
                    title = card.find('h4').text.strip()
                    
                    model_url = f"https://huggingface.co/api/models/{model_id}"
                    model_resp = requests.get(model_url, headers=HEADERS, timeout=10)
                    
                    if model_resp.status_code == 200:
                        model_data = model_resp.json()
                        
                        model_info = {
                            'id': model_id,
                            'name': model_data.get('modelId', '').split('/')[-1],
                            'author': model_data.get('author', ''),
                            'description': model_data.get('cardData', {}).get('description', ''),
                            'tags': model_data.get('tags', []),
                            'downloads': model_data.get('downloads', 0),
                            'likes': model_data.get('likes', 0),
                        }
                        
                        model_info['size'] = extract_model_size(model_info)
                        models.append(model_info)
                        
                except Exception as e:
                    logger.warning(f"Error processing model {model_id if 'model_id' in locals() else 'unknown'}: {e}")
                    continue
            
            if models:
                return True, f"Fetched {len(models)} models from web", models
            return False, "No models found on Hugging Face", []
            
        except Exception as e:
            logger.error(f"Web scraping failed: {e}")
            return False, f"Web scraping failed: {e}", []
    
    # Main function logic
    try:
        # Create cache directory if it doesn't exist
        cache_file = get_hf_models_cache_path()
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        
        # Try API first
        success, message, models = fetch_from_api()
        
        # Fall back to web scraping if API fails
        if not success or not models:
            logger.warning(f"Falling back to web scraping: {message}")
            success, message, models = fetch_from_web()
        
        # If we have models, save them to cache
        if models:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(models, f, indent=2, ensure_ascii=False)
                return True, f"Successfully updated {len(models)} models in cache"
            except IOError as e:
                error_msg = f"Error writing to cache: {e}"
                logger.error(error_msg)
                return False, error_msg
        
        return success, message or "No models found"
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg)
        return False, error_msg
