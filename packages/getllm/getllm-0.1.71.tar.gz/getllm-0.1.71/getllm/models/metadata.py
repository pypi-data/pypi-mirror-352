"""
Model metadata manager for handling model metadata operations.
"""
import json
import os
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Get logger
logger = logging.getLogger('getllm.models.metadata')

from ..utils.config import get_models_metadata_path, get_models_dir


class ModelMetadataManager:
    """Manages model metadata operations."""
    
    def __init__(self):
        # Use the logs directory in the user's home directory for metadata
        self.logs_dir = Path.home() / ".getllm" / "logs"
        self.metadata_file = self.logs_dir / "models_metadata.json"
        
        # Ensure the logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def get_metadata(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific model.
        
        Args:
            model_name: Name of the model to get metadata for.
            
        Returns:
            Dictionary containing model metadata, or None if not found.
        """
        metadata = self._load_metadata()
        return metadata.get(model_name)
    
    def update_metadata(self, model_name: str, data: Dict[str, Any]) -> bool:
        """Update metadata for a model.
        
        Args:
            model_name: Name of the model to update.
            data: Dictionary containing metadata to update.
            
        Returns:
            True if successful, False otherwise.
        """
        logger.debug(f'Updating metadata for model: {model_name}')
        metadata = self._load_metadata()
        
        if model_name not in metadata:
            logger.debug(f'Creating new metadata entry for model: {model_name}')
            metadata[model_name] = {}
        else:
            logger.debug(f'Updating existing metadata for model: {model_name}')
            
        metadata[model_name].update(data)
        logger.debug(f'Updated metadata for model {model_name}: {data}')
        
        return self._save_metadata(metadata)
    
    def remove_metadata(self, model_name: str) -> bool:
        """Remove metadata for a model.
        
        Args:
            model_name: Name of the model to remove.
            
        Returns:
            True if successful, False otherwise.
        """
        metadata = self._load_metadata()
        
        if model_name in metadata:
            logger.debug(f'Removing metadata for model: {model_name}')
            del metadata[model_name]
            return self._save_metadata(metadata)
            
        logger.debug(f'Metadata for model {model_name} not found')
        return True
    
    def list_models(self) -> List[str]:
        """List all models with metadata.
        
        Returns:
            List of model names that have metadata.
        """
        metadata = self._load_metadata()
        return list(metadata.keys())
    
    def get_current_timestamp(self):
        """Get the current timestamp.
        
        Returns:
            Current timestamp as a string.
        """
        return datetime.datetime.now().isoformat()
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load metadata from the metadata file.
        
        Returns:
            Dictionary containing all metadata.
        """
        logger.debug(f'Loading metadata from file: {self.metadata_file}')
        if not self.metadata_file.exists():
            logger.debug('Metadata file does not exist, returning empty metadata')
            return {}
            
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                logger.debug(f'Loaded metadata for {len(metadata)} models')
                return metadata
        except json.JSONDecodeError as e:
            logger.error(f'Error decoding metadata JSON: {e}', exc_info=True)
            return {}
        except IOError as e:
            logger.error(f'IO error loading metadata: {e}', exc_info=True)
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save metadata to the metadata file.
        
        Args:
            metadata: Dictionary containing all metadata to save.
            
        Returns:
            True if successful, False otherwise.
        """
        logger.debug(f'Saving metadata for {len(metadata)} models to {self.metadata_file}')
        try:
            # Ensure the directory exists
            self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with pretty-printing
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.debug('Metadata saved successfully')
            return True
        except IOError as e:
            logger.error(f'IO error saving metadata: {e}', exc_info=True)
            return False
