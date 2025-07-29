"""
Utility functions for model management.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .constants import (
    get_models_dir, 
    get_models_metadata_path,
    get_hf_models_cache_path,
    get_ollama_models_cache_path,
    DEFAULT_MODELS,
    DEFAULT_HF_MODELS
)

logger = logging.getLogger(__name__)

def ensure_models_dir():
    """Ensure the models directory exists."""
    models_dir = get_models_dir()
    os.makedirs(models_dir, exist_ok=True)
    return models_dir

def save_models_to_json(models: List[Dict], file_path: str = None) -> bool:
    """
    Save models to a JSON file.
    
    Args:
        models: The models to save.
        file_path: The path to the JSON file. If None, uses the default path.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        file_path = file_path or get_models_metadata_path()
        ensure_models_dir()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(models, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving models to {file_path}: {e}")
        return False

def load_models_from_json(file_path: str = None) -> List[Dict]:
    """
    Load models from a JSON file.
    
    Args:
        file_path: The path to the JSON file. If None, uses the default path.
        
    Returns:
        The loaded models, or the default models if the file doesn't exist.
    """
    try:
        file_path = file_path or get_models_metadata_path()
        if not os.path.exists(file_path):
            return DEFAULT_MODELS
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading models from {file_path}: {e}")
        return DEFAULT_MODELS

def get_default_model() -> Optional[str]:
    """
    Get the default model from the environment variables.
    
    Returns:
        The default model name, or None if not set.
    """
    return os.environ.get('OLLAMA_MODEL')

def set_default_model(model_name: str) -> bool:
    """
    Set the default model in the environment variables.
    
    Args:
        model_name: The name of the model to set as default.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Update environment variable for current process
        os.environ['OLLAMA_MODEL'] = model_name
        
        # Update .env file for future sessions
        env_path = os.path.join(os.path.expanduser('~'), '.getllm', '.env')
        os.makedirs(os.path.dirname(env_path), exist_ok=True)
        
        # Read existing .env file if it exists
        env_vars = {}
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        
        # Update OLLAMA_MODEL
        env_vars['OLLAMA_MODEL'] = f'"{model_name}"'
        
        # Write back to .env file
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
                
        return True
    except Exception as e:
        logger.error(f"Error setting default model: {e}")
        return False

def get_models() -> List[Dict]:
    """
    Get a list of available models from the models.json file or default list.
    Also updates the models metadata file if needed.
    
    Returns:
        A list of dictionaries containing model information.
    """
    # Try to load from models.json first
    models = load_models_from_json()
    
    # If no models found, use the default ones
    if not models:
        models = DEFAULT_MODELS
        save_models_to_json(models)
        
    return models

def install_model(model_name: str) -> bool:
    """
    Install a model using Ollama.
    
    Args:
        model_name: The name of the model to install.
        
    Returns:
        True if installation was successful, False otherwise.
    """
    try:
        from getllm.ollama import install_ollama_model
        return install_ollama_model(model_name)
    except Exception as e:
        logger.error(f"Error installing model {model_name}: {e}")
        return False

def list_installed_models() -> List[str]:
    """
    List models that are currently installed in Ollama.
    
    Returns:
        A list of installed model names.
    """
    try:
        from getllm.ollama import list_ollama_models
        return [model['name'] for model in list_ollama_models()]
    except Exception as e:
        logger.error(f"Error listing installed models: {e}")
        return []

def get_model_metadata(model_name: str) -> Optional[Dict]:
    """
    Get metadata for a specific model.
    
    Args:
        model_name: The name of the model to get metadata for.
        
    Returns:
        A dictionary containing model metadata, or None if not found.
    """
    # First check the local models
    for model in get_models():
        if model.get('name') == model_name:
            return model
            
    # Then check the default models
    for model in DEFAULT_MODELS:
        if model.get('name') == model_name:
            return model
            
    # Finally, check Hugging Face models
    hf_models = load_huggingface_models_from_cache()
    for model in hf_models:
        if model.get('name') == model_name or model.get('id') == model_name:
            return model
            
    return None

def load_huggingface_models_from_cache() -> List[Dict]:
    """
    Load Hugging Face models from the cache file.
    
    Returns:
        A list of Hugging Face models, or an empty list if the cache file doesn't exist or is invalid.
    """
    cache_path = get_hf_models_cache_path()
    try:
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading Hugging Face models from cache: {e}")
    
    return DEFAULT_HF_MODELS

def load_ollama_models_from_cache() -> List[Dict]:
    """
    Load Ollama models from the cache file.
    
    Returns:
        A list of Ollama models, or an empty list if the cache file doesn't exist or is invalid.
    """
    cache_path = get_ollama_models_cache_path()
    try:
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading Ollama models from cache: {e}")
    
    return []
