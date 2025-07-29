"""
This package contains model-related functionality for the getllm application.
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# Get logger
logger = logging.getLogger('getllm.models')

from .base import ModelManager
from .huggingface import HuggingFaceModelManager
from .ollama import OllamaModelManager
from .metadata import ModelMetadataManager
from .interactive import interactive_model_search
from .utils import (
    get_models_dir,
    get_models_metadata_path,
    get_config_dir,
    update_models_metadata,
    update_models_from_ollama
)

# Initialize model managers
huggingface_manager = HuggingFaceModelManager()
ollama_manager = OllamaModelManager()
metadata_manager = ModelMetadataManager()

# Define default models
DEFAULT_HF_MODELS = [
    {
        'id': 'TheBloke/Llama-2-7B-Chat-GGUF',
        'name': 'llama-2-7b-chat',
        'size': '7B',
        'description': 'Llama 2 7B Chat model in GGUF format',
        'source': 'huggingface',
        'format': 'gguf'
    },
    {
        'id': 'bielik-ai/Bielik-13B-v0.1-GGUF',
        'name': 'bielik-13b-v0.1',
        'size': '13B',
        'description': 'Bielik 13B v0.1 model in GGUF format',
        'source': 'huggingface',
        'format': 'gguf'
    },
    {
        'id': 'bielik-ai/Bielik-7B-v0.1-GGUF',
        'name': 'bielik-7b-v0.1',
        'size': '7B',
        'description': 'Bielik 7B v0.1 model in GGUF format',
        'source': 'huggingface',
        'format': 'gguf'
    },
    {
        'id': 'TheBloke/Mistral-7B-Instruct-v0.2-GGUF',
        'name': 'mistral-7b-instruct-v0.2',
        'size': '7B',
        'description': 'Mistral 7B Instruct v0.2 model in GGUF format',
        'source': 'huggingface',
        'format': 'gguf'
    },
    {
        'id': 'TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF',
        'name': 'mixtral-8x7b-instruct-v0.1',
        'size': '8x7B',
        'description': 'Mixtral 8x7B Instruct v0.1 model in GGUF format',
        'source': 'huggingface',
        'format': 'gguf'
    }
]

def get_models() -> List[Dict[str, Any]]:
    """
    Get all available models from all sources.
    
    Returns:
        List of model dictionaries with metadata.
    """
    models = []
    
    # Get models from Hugging Face
    try:
        hf_models = huggingface_manager.get_available_models()
        models.extend([{"source": "huggingface", **model} for model in hf_models])
    except Exception as e:
        logger.error(f"Error getting Hugging Face models: {e}")
    
    # Get models from Ollama
    try:
        ollama_models = ollama_manager.get_available_models()
        models.extend([{"source": "ollama", **model} for model in ollama_models])
    except Exception as e:
        logger.error(f"Error getting Ollama models: {e}")
    
    return models

def get_hf_models_cache_path() -> Path:
    """
    Get the path to the Hugging Face models cache file.
    
    Returns:
        Path to the cache file.
    """
    return get_models_dir() / "huggingface_models.json"

def update_huggingface_models_cache(limit: int = 50) -> bool:
    """
    Update the cache of available Hugging Face models.
    
    Args:
        limit: Maximum number of models to fetch.
        
    Returns:
        True if successful, False otherwise.
    """
    logger.debug('Updating Hugging Face models cache...')
    try:
        models = huggingface_manager.get_available_models(limit=limit)
        cache_path = get_hf_models_cache_path()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'w') as f:
            json.dump(models, f, indent=2)
        
        logger.info('Successfully updated Hugging Face models cache')
        return True
    except Exception as e:
        logger.error(f"Error updating Hugging Face models cache: {e}", exc_info=True)
        print(f"Error updating Hugging Face models cache: {e}")
        return False

def update_models_from_ollama(mock: bool = False) -> bool:
    """
    Update the list of available Ollama models.
    
    Args:
        mock: If True, skip Ollama server checks and return mock data
        
    Returns:
        True if successful, False otherwise.
    """
    logger.debug('Updating Ollama models...')
    
    if mock:
        logger.debug('Running in mock mode - skipping Ollama server checks')
        print("Running in mock mode - Ollama server checks bypassed")
        return True
        
    try:
        ollama_models = ollama_manager.get_available_models()
        logger.debug(f'Found {len(ollama_models)} Ollama models')
        
        # Update metadata
        for model in ollama_models:
            logger.debug(f'Updating metadata for Ollama model: {model.get("name", "unknown")}')
            metadata_manager.update_metadata(
                model['name'],
                {"source": "ollama", "last_updated": str(metadata_manager.get_current_timestamp())}
            )
        logger.info('Successfully updated Ollama models')
        return True
    except Exception as e:
        logger.error(f"Error updating Ollama models: {e}", exc_info=True)
        print(f"Error updating Ollama models: {e}")
        return False
        return False

def update_models_metadata() -> bool:
    """
    Update metadata for all models.
    
    Returns:
        True if successful, False otherwise.
    """
    logger.debug('Updating metadata for all models...')
    try:
        # Update Hugging Face models metadata
        logger.debug('Fetching Hugging Face models...')
        hf_models = huggingface_manager.get_available_models()
        logger.debug(f'Found {len(hf_models)} Hugging Face models')
        
        for model in hf_models:
            model_name = model.get('name', model.get('id', 'unknown'))
            logger.debug(f'Updating metadata for Hugging Face model: {model_name}')
            metadata_manager.update_metadata(
                model['name'],
                {"source": "huggingface", "last_updated": str(metadata_manager.get_current_timestamp())}
            )
        
        # Update Ollama models metadata
        logger.debug('Updating Ollama models metadata...')
        update_models_from_ollama()
        
        logger.info('Successfully updated metadata for all models')
        return True
    except Exception as e:
        logger.error(f"Error updating models metadata: {e}", exc_info=True)
        print(f"Error updating models metadata: {e}")
        return False

def search_huggingface_models(query: str = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for models on Hugging Face based on a query string.
    
    Args:
        query: Search query string
        limit: Maximum number of models to return
        
    Returns:
        List of model dictionaries matching the query
    """
    try:
        # First try to use the huggingface_manager to search for models
        models_list = huggingface_manager.search_models(query=query, limit=limit)
        
        # If no models found or there was an error, fall back to DEFAULT_HF_MODELS
        if not models_list:
            # If query is provided, filter the default models
            if query:
                query = query.lower()
                models_list = [
                    model for model in DEFAULT_HF_MODELS
                    if (query in model.get('name', '').lower() or
                        query in model.get('id', '').lower() or
                        query in model.get('description', '').lower())
                ]
            else:
                # If no query, return all default models
                models_list = DEFAULT_HF_MODELS[:limit]
                
        return models_list
    except Exception as e:
        logger.error(f"Error searching Hugging Face models: {e}", exc_info=True)
        print(f"Error searching Hugging Face models: {e}")
        # Fall back to DEFAULT_HF_MODELS
        if query:
            query = query.lower()
            return [
                model for model in DEFAULT_HF_MODELS
                if (query in model.get('name', '').lower() or
                    query in model.get('id', '').lower() or
                    query in model.get('description', '').lower())
            ][:limit]
        return DEFAULT_HF_MODELS[:limit]

def load_huggingface_models_from_cache() -> List[Dict]:
    """
    Load Hugging Face models from cache.
    
    Returns:
        List of Hugging Face models from cache.
    """
    cache_path = get_hf_models_cache_path()
    if not cache_path.exists():
        return []
    
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading Hugging Face models from cache: {e}", exc_info=True)
        print(f"Error loading Hugging Face models from cache: {e}")
        return []

def load_ollama_models_from_cache() -> List[Dict]:
    """
    Load Ollama models from cache.
    
    Returns:
        List of Ollama models from cache.
    """
    cache_path = get_models_dir() / "ollama_models.json"
    if not cache_path.exists():
        return []
    
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading Ollama models from cache: {e}", exc_info=True)
        print(f"Error loading Ollama models from cache: {e}")
        return []

def get_huggingface_models(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get available models from Hugging Face.
    
    Args:
        limit: Maximum number of models to return
        
    Returns:
        List of model dictionaries
    """
    try:
        # First try to get models from the huggingface_manager
        models = huggingface_manager.get_available_models()
        if models:
            return models[:limit]
        # Fall back to DEFAULT_HF_MODELS if no models found
        return DEFAULT_HF_MODELS[:limit]
    except Exception as e:
        logger.error(f"Error getting Hugging Face models: {e}", exc_info=True)
        print(f"Error getting Hugging Face models: {e}")
        # Fall back to DEFAULT_HF_MODELS in case of error
        return DEFAULT_HF_MODELS[:limit]

def update_models_from_huggingface(query: str = None, limit: int = 20) -> bool:
    """
    Update models from Hugging Face.
    
    Args:
        query: Optional search query to filter models
        limit: Maximum number of models to return
        
    Returns:
        True if successful, False otherwise.
    """
    logger.debug(f'Updating models from Hugging Face with query: {query}, limit: {limit}')
    try:
        # First update the cache
        logger.debug('Updating Hugging Face models cache...')
        cache_updated = update_huggingface_models_cache()
        logger.debug(f'Cache update result: {cache_updated}')
        
        # Then update the models list
        logger.debug('Searching for Hugging Face models...')
        models = search_huggingface_models(query=query, limit=limit)
        logger.debug(f'Found {len(models)} Hugging Face models matching query')
        
        # Update metadata for each model
        for model in models:
            model_name = model.get('name', model.get('id', 'unknown'))
            logger.debug(f'Updating metadata for Hugging Face model: {model_name}')
            metadata_manager.update_metadata(
                model.get('name', model.get('id', '')),
                {"source": "huggingface", "last_updated": str(metadata_manager.get_current_timestamp())}
            )
        
        logger.info(f'Successfully updated {len(models)} models from Hugging Face')
        return True
    except Exception as e:
        logger.error(f"Error updating models from Hugging Face: {e}", exc_info=True)
        print(f"Error updating models from Hugging Face: {e}")
        return False

def get_default_model() -> Optional[str]:
    """
    Get the default model name.
    
    Returns:
        The name of the default model or None if not set
    """
    config_dir = get_config_dir()
    config_file = config_dir / 'default_model.json'
    
    if not config_file.exists():
        return None
        
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('name') if isinstance(config, dict) else None
    except (json.JSONDecodeError, IOError):
        return None

def set_default_model(model_name: str, model_source: str = 'ollama') -> bool:
    """
    Set the default model.
    
    Args:
        model_name: Name of the model to set as default
        model_source: Source of the model ('ollama' or 'huggingface')
        
    Returns:
        True if successful, False otherwise
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'default_model.json'
    
    try:
        default_model = {
            'name': model_name,
            'source': model_source,
            'timestamp': str(datetime.datetime.now().isoformat())
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_model, f, indent=2)
        return True
    except (IOError, TypeError):
        return False


def install_model(model_name: str, model_source: str = 'ollama') -> bool:
    """
    Install a model from the specified source.
    
    Args:
        model_name: Name of the model to install
        model_source: Source of the model ('ollama' or 'huggingface')
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    if model_source.lower() == 'ollama':
        return ollama_manager.install_model(model_name)
    elif model_source.lower() == 'huggingface':
        return huggingface_manager.install_model(model_name)
    else:
        raise ValueError(f"Unsupported model source: {model_source}")


def list_installed_models() -> List[Dict[str, Any]]:
    """
    List all installed models from all sources.
    
    Returns:
        List of installed models with their metadata
    """
    installed_models = []
    
    # Get installed models from Ollama
    try:
        ollama_models = ollama_manager.list_installed_models()
        installed_models.extend([{
            'name': model.get('name', 'unknown'),
            'source': 'ollama',
            'size': model.get('size', 'unknown'),
            'description': model.get('description', '')
        } for model in ollama_models])
    except Exception as e:
        print(f"Error listing Ollama models: {e}")
    
    # Get installed models from Hugging Face
    try:
        hf_models = huggingface_manager.list_installed_models()
        installed_models.extend([{
            'name': model.get('name', 'unknown'),
            'source': 'huggingface',
            'size': model.get('size', 'unknown'),
            'description': model.get('description', '')
        } for model in hf_models])
    except Exception as e:
        print(f"Error listing Hugging Face models: {e}")
    
    return installed_models

__all__ = [
    'ModelManager',
    'HuggingFaceModelManager',
    'OllamaModelManager',
    'interactive_model_search',
    'ModelMetadataManager',
    'get_models',
    'get_huggingface_models',
    'get_default_model',
    'set_default_model',
    'install_model',
    'list_installed_models',
    'get_hf_models_cache_path',
    'update_huggingface_models_cache',
    'update_models_from_ollama',
    'update_models_metadata',
    'DEFAULT_HF_MODELS',
    'search_huggingface_models',
    'update_models_from_huggingface',
    'load_huggingface_models_from_cache',
    'load_ollama_models_from_cache'
]
