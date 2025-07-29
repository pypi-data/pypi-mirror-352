"""
Caching mechanisms for model data.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .constants import (
    get_models_dir,
    get_hf_models_cache_path,
    get_ollama_models_cache_path,
    get_models_metadata_path
)

# Cache expiration in seconds (1 week)
CACHE_EXPIRY = 7 * 24 * 60 * 60

def is_cache_valid(cache_path: str, max_age: int = CACHE_EXPIRY) -> bool:
    """
    Check if a cache file is still valid.
    
    Args:
        cache_path: Path to the cache file.
        max_age: Maximum age of the cache in seconds.
        
    Returns:
        True if the cache is valid, False otherwise.
    """
    if not os.path.exists(cache_path):
        return False
        
    try:
        # Check file modification time
        file_mtime = os.path.getmtime(cache_path)
        return (time.time() - file_mtime) <= max_age
    except Exception:
        return False

def load_json_cache(cache_path: str, default: Any = None) -> Any:
    """
    Load data from a JSON cache file.
    
    Args:
        cache_path: Path to the cache file.
        default: Default value to return if the cache is invalid.
        
    Returns:
        The cached data, or the default value if the cache is invalid.
    """
    if not is_cache_valid(cache_path):
        return default
        
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default

def save_json_cache(data: Any, cache_path: str) -> bool:
    """
    Save data to a JSON cache file.
    
    Args:
        data: The data to cache.
        cache_path: Path to the cache file.
        
    Returns:
        True if the cache was saved successfully, False otherwise.
    """
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, TypeError):
        return False

def get_cached_hf_models() -> List[Dict]:
    """Get cached Hugging Face models."""
    cache_path = get_hf_models_cache_path()
    return load_json_cache(cache_path, [])

def get_cached_ollama_models() -> List[Dict]:
    """Get cached Ollama models."""
    cache_path = get_ollama_models_cache_path()
    return load_json_cache(cache_path, [])

def get_cached_models_metadata() -> Dict[str, Any]:
    """Get cached models metadata."""
    cache_path = get_models_metadata_path()
    return load_json_cache(cache_path, {})
