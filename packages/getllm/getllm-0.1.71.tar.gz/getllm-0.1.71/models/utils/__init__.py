"""
Utility functions for model management.

This module provides helper functions for working with models,
including model loading, saving, and other common operations.
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

from ..exceptions import ModelError, ModelNotFoundError, ModelInstallationError

logger = logging.getLogger('getllm.models.utils')

# --- Path related utilities ---

def get_models_metadata_path() -> str:
    """Get the path to the models metadata file.
    
    Returns:
        str: Path to the models metadata JSON file
    """
    return os.path.join(get_models_dir(), "models.json")

def get_hf_models_cache_path() -> str:
    """Get the path to the Hugging Face models cache file.
    
    Returns:
        str: Path to the Hugging Face models cache JSON file
    """
    return os.path.join(get_models_dir(), "hf_models.json")

def get_ollama_models_cache_path() -> str:
    """Get the path to the Ollama models cache file.
    
    Returns:
        str: Path to the Ollama models cache JSON file
    """
    return os.path.join(get_models_dir(), "ollama_models.json")

def get_default_model() -> Optional[str]:
    """Get the default model name.
    
    Returns:
        Optional[str]: Name of the default model, or None if not set
    """
    default_model_path = os.path.join(get_models_dir(), "default_model.txt")
    if os.path.exists(default_model_path):
        with open(default_model_path, "r") as f:
            return f.read().strip()
    return None

def set_default_model(model_name: str) -> None:
    """Set the default model.
    
    Args:
        model_name: Name of the model to set as default
    """
    os.makedirs(get_models_dir(), exist_ok=True)
    default_model_path = os.path.join(get_models_dir(), "default_model.txt")
    with open(default_model_path, "w") as f:
        f.write(model_name)

def get_models() -> Dict[str, Any]:
    """Get all models metadata.
    
    Returns:
        Dict containing all models metadata
    """
    metadata_path = get_models_metadata_path()
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            return json.load(f)
    return {}

def load_huggingface_models_from_cache() -> Dict[str, Any]:
    """Load Hugging Face models from cache.
    
    Returns:
        Dict containing Hugging Face models data
    """
    cache_path = get_hf_models_cache_path()
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    return {}

def load_ollama_models_from_cache() -> Dict[str, Any]:
    """Load Ollama models from cache.
    
    Returns:
        Dict containing Ollama models data
    """
    cache_path = get_ollama_models_cache_path()
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    return {}

def save_models_to_json(models_data: Dict[str, Any], file_path: str) -> None:
    """Save models data to a JSON file.
    
    Args:
        models_data: Dictionary containing models data
        file_path: Path to save the JSON file
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(models_data, f, indent=2)

def load_models_from_json(file_path: str) -> Dict[str, Any]:
    """Load models data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dict containing models data
    """
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

# --- Model installation utilities ---

def install_model(model_name: str, source: str = "huggingface", **kwargs) -> bool:
    """Install a model from the specified source.
    
    Args:
        model_name: Name of the model to install
        source: Source of the model (huggingface, ollama, etc.)
        **kwargs: Additional arguments for the installation process
        
    Returns:
        bool: True if installation was successful, False otherwise
        
    Raises:
        ModelInstallationError: If there's an error during installation
    """
    try:
        from ..manager import get_model_manager
        
        manager = get_model_manager(source=source)
        if not manager:
            raise ModelInstallationError(f"Unsupported model source: {source}")
            
        # Ensure the model directory exists
        model_dir = get_model_dir(model_name)
        os.makedirs(model_dir, exist_ok=True)
        
        # Install the model
        success = manager.install_model(model_name, **kwargs)
        if not success:
            raise ModelInstallationError(f"Failed to install model: {model_name}")
            
        return True
        
    except Exception as e:
        if not isinstance(e, ModelInstallationError):
            raise ModelInstallationError(f"Error installing model {model_name}: {str(e)}")
        raise

# --- Model listing utilities ---

def list_installed_models() -> List[Dict[str, Any]]:
    """List all installed models with their metadata.
    
    Returns:
        List of dictionaries containing model metadata
    """
    models = []
    models_dir = get_models_dir()
    
    if not os.path.exists(models_dir):
        return models
        
    for model_name in os.listdir(models_dir):
        model_dir = os.path.join(models_dir, model_name)
        if os.path.isdir(model_dir):
            try:
                metadata = load_model_metadata(model_name)
                models.append({
                    'name': model_name,
                    'source': metadata.get('source', 'unknown'),
                    'installed': True,
                    'size': get_model_size(model_name),
                    'metadata': metadata
                })
            except ModelError:
                # Skip models with invalid metadata
                continue
                
    return models

# --- End model listing utilities ---

def get_models_dir() -> str:
    """Get the directory where models are stored.
    
    Returns:
        str: Path to the models directory
    """
    return os.path.join(os.path.expanduser("~"), ".cache", "getllm", "models")

def ensure_models_dir() -> str:
    """Ensure the models directory exists.
    
    Returns:
        str: Path to the models directory
    """
    models_dir = get_models_dir()
    os.makedirs(models_dir, exist_ok=True)
    return models_dir

def get_model_dir(model_name: str) -> str:
    """Get the directory for a specific model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        str: Path to the model directory
    """
    return os.path.join(get_models_dir(), model_name)

def ensure_model_dir_exists(model_name: str) -> str:
    """Ensure the directory for a model exists.
    
    Args:
        model_name: Name of the model
        
    Returns:
        str: Path to the model directory
    """
    model_dir = get_model_dir(model_name)
    os.makedirs(model_dir, exist_ok=True)
    return model_dir

def load_model_metadata(model_name: str) -> Dict[str, Any]:
    """Load metadata for a model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        dict: Model metadata
        
    Raises:
        ModelError: If the metadata file doesn't exist or is invalid
    """
    metadata_path = os.path.join(get_model_dir(model_name), "metadata.json")
    if not os.path.exists(metadata_path):
        raise ModelError(f"Metadata not found for model: {model_name}")
        
    try:
        with open(metadata_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ModelError(f"Invalid metadata for model {model_name}: {str(e)}")
    except Exception as e:
        raise ModelError(f"Error loading metadata for model {model_name}: {str(e)}")

# Alias for backward compatibility
get_model_metadata = load_model_metadata

def save_model_metadata(model_name: str, metadata: Dict[str, Any]) -> None:
    """Save metadata for a model.
    
    Args:
        model_name: Name of the model
        metadata: Model metadata to save
        
    Raises:
        ModelError: If the metadata cannot be saved
    """
    model_dir = ensure_model_dir_exists(model_name)
    metadata_path = os.path.join(model_dir, "metadata.json")
    
    try:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    except (IOError, TypeError) as e:
        raise ModelError(f"Failed to save metadata for model {model_name}: {e}")

def get_model_size(model_name: str) -> Optional[int]:
    """Get the size of a model in bytes.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Optional[int]: Size in bytes, or None if unknown
    """
    try:
        model_dir = get_model_dir(model_name)
        if not os.path.exists(model_dir):
            return None
            
        total_size = 0
        for dirpath, _, filenames in os.walk(model_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    except Exception as e:
        logger.warning(f"Error calculating model size for {model_name}: {e}")
        return None

def format_model_size(size_bytes: Optional[int]) -> str:
    """Format a model size in a human-readable format.
    
    Args:
        size_bytes: Size in bytes, or None
        
    Returns:
        str: Formatted size string (e.g., "1.2 GB")
    """
    if size_bytes is None:
        return "Unknown"
        
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def get_available_models() -> List[str]:
    """Get a list of all available models.
    
    Returns:
        List of model names
    """
    models_dir = get_models_dir()
    if not os.path.exists(models_dir):
        return []
        
    return [
        name for name in os.listdir(models_dir)
        if os.path.isdir(os.path.join(models_dir, name))
    ]

def is_model_installed(model_name: str) -> bool:
    """Check if a model is installed.
    
    Args:
        model_name: Name of the model to check
        
    Returns:
        bool: True if the model is installed
    """
    model_dir = get_model_dir(model_name)
    return os.path.exists(model_dir) and os.path.isdir(model_dir)

def delete_model(model_name: str) -> bool:
    """Delete a model.
    
    Args:
        model_name: Name of the model to delete
        
    Returns:
        bool: True if the model was deleted successfully
    """
    import shutil
    
    model_dir = get_model_dir(model_name)
    if not os.path.exists(model_dir):
        return False
        
    try:
        shutil.rmtree(model_dir)
        return True
    except Exception as e:
        logger.error(f"Failed to delete model {model_name}: {e}")
        return False
