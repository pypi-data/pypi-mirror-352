"""
Utility functions for model management in the getllm application.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Get logger
logger = logging.getLogger('getllm.models.utils')

def get_models_dir() -> Path:
    """
    Get the directory where models are stored.
    
    Returns:
        Path: Path to the models directory
    """
    from ..utils.config import get_models_dir as _get_models_dir
    return _get_models_dir()

def get_models_metadata_path() -> Path:
    """
    Get the path to the models metadata file.
    
    Returns:
        Path: Path to the models metadata file
    """
    from ..utils.config import get_models_metadata_path as _get_models_metadata_path
    return _get_models_metadata_path()

def get_config_dir() -> Path:
    """
    Get the configuration directory.
    
    Returns:
        Path: Path to the configuration directory
    """
    from ..utils.config import get_config_dir as _get_config_dir
    return _get_config_dir()

def update_models_metadata() -> bool:
    """
    Update metadata for all models.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    from . import huggingface_manager, ollama_manager, metadata_manager
    
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

def update_models_from_ollama(mock: bool = False) -> bool:
    """
    Update the list of available Ollama models.
    
    Args:
        mock: If True, skip Ollama server checks and return mock data
        
    Returns:
        bool: True if successful, False otherwise.
    """
    from . import ollama_manager, metadata_manager
    
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
