"""Ollama model management."""

import os
import logging
from typing import List, Dict, Any, Optional
import requests

logger = logging.getLogger('getllm.ollama.models.manager')

class OllamaModelManager:
    """Manages Ollama models and their lifecycle."""
    
    def __init__(self, base_url: str = "http://localhost:11434/api"):
        """Initialize the model manager.
        
        Args:
            base_url: Base URL for the Ollama API
        """
        self.base_url = base_url
        self.models_url = f"{base_url}/tags"
        self.pull_url = f"{base_url}/pull"
        self.push_url = f"{base_url}/push"
        self.delete_url = f"{base_url}/delete"
        self.copy_url = f"{base_url}/copy"
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models.
        
        Returns:
            List of model dictionaries with their details
        """
        try:
            response = requests.get(self.models_url, timeout=10)
            response.raise_for_status()
            return response.json().get('models', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model.
        
        Args:
            model_name: Name of the model to get info for
            
        Returns:
            Dictionary with model information or None if not found
        """
        models = self.list_models()
        for model in models:
            if model.get('name') == model_name:
                return model
        return None
    
    def model_exists(self, model_name: str) -> bool:
        """Check if a model exists.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            bool: True if the model exists, False otherwise
        """
        return self.get_model_info(model_name) is not None
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a model.
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            response = requests.delete(
                self.delete_url,
                json={'name': model_name},
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete model {model_name}: {str(e)}")
            return False
    
    def copy_model(self, source_name: str, target_name: str) -> bool:
        """Create a copy of a model with a new name.
        
        Args:
            source_name: Name of the source model
            target_name: Name for the new model
            
        Returns:
            bool: True if the copy was successful, False otherwise
        """
        try:
            response = requests.post(
                self.copy_url,
                json={'source': source_name, 'destination': target_name},
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to copy model {source_name} to {target_name}: {str(e)}")
            return False
