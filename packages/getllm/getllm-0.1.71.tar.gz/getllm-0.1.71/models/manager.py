"""
Model management for PyLLM.

This module provides a unified interface for managing LLM models
from various sources including Ollama and Hugging Face.
"""

import os
import logging
from typing import List, Dict, Optional, Any, Union, Type, TypeVar
from pathlib import Path

from .base import BaseModel, BaseModelManager, ModelMetadata, ModelSource, ModelType
from .huggingface.manager import HuggingFaceModelManager, get_hf_model_manager
from .ollama.manager import OllamaModelManager, get_ollama_model_manager
from getllm.exceptions import ModelError, ModelNotFoundError, ModelInstallationError, ModelQueryError

logger = logging.getLogger(__name__)

# Type variable for model managers
M = TypeVar('M', bound=BaseModelManager)


class ModelManager:
    """
    Unified model manager for PyLLM.
    
    This class provides a single interface for managing models from
    different sources (Ollama, Hugging Face, etc.) with a consistent API.
    """
    
    def __init__(
        self,
        default_source: str = "ollama",
        cache_dir: Optional[str] = None,
        **kwargs
    ):
        """Initialize the ModelManager.
        
        Args:
            default_source: Default model source ('ollama' or 'huggingface')
            cache_dir: Directory to cache model metadata
            **kwargs: Additional arguments to pass to model managers
        """
        self.default_source = default_source.lower()
        self.cache_dir = cache_dir or os.path.join(
            os.path.expanduser("~"), ".cache", "getllm"
        )
        
        # Initialize model managers
        self._managers: Dict[str, BaseModelManager] = {}
        self._init_managers(**kwargs)
        
        # Set default model
        self.default_model = os.getenv("GETLLM_DEFAULT_MODEL", "llama3")
    
    def _init_managers(self, **kwargs) -> None:
        """Initialize model managers for each source."""
        # Ollama manager
        ollama_kwargs = {
            k[8:]: v for k, v in kwargs.items() if k.startswith("ollama_")
        }
        self._managers["ollama"] = get_ollama_model_manager(
            cache_dir=os.path.join(self.cache_dir, "ollama"),
            **ollama_kwargs
        )
        
        # Hugging Face manager
        hf_kwargs = {
            k[3:]: v for k, v in kwargs.items() if k.startswith("hf_")
        }
        self._managers["huggingface"] = get_hf_model_manager(
            cache_dir=os.path.join(self.cache_dir, "huggingface"),
            **hf_kwargs
        )
    
    def _get_manager(self, source: Optional[str] = None) -> BaseModelManager:
        """Get the model manager for the specified source.
        
        Args:
            source: Model source ('ollama', 'huggingface', etc.)
            
        Returns:
            The model manager instance
            
        Raises:
            ValueError: If the source is not supported
        """
        source = (source or self.default_source).lower()
        if source not in self._managers:
            raise ValueError(f"Unsupported model source: {source}")
        return self._managers[source]
    
    def list_models(
        self, 
        source: Optional[str] = None,
        **filters
    ) -> List[ModelMetadata]:
        """List available models.
        
        Args:
            source: Model source ('ollama', 'huggingface', etc.)
            **filters: Additional filters to apply
                - model_type: Filter by model type (e.g., 'text', 'code')
                - tags: List of tags to filter by
                - min_size: Minimum model size in bytes
                - max_size: Maximum model size in bytes
                
        Returns:
            List of ModelMetadata objects
        """
        if source:
            return self._get_manager(source).list_models()
        
        # List models from all sources if no source is specified
        all_models = []
        for manager in self._managers.values():
            try:
                all_models.extend(manager.list_models())
            except Exception as e:
                logger.warning(f"Error listing models from {manager.__class__.__name__}: {e}")
        
        # Apply filters
        if filters:
            all_models = self._filter_models(all_models, **filters)
        
        return all_models
    
    def _filter_models(
        self, 
        models: List[ModelMetadata], 
        **filters
    ) -> List[ModelMetadata]:
        """Filter models based on the provided criteria.
        
        Args:
            models: List of models to filter
            **filters: Filter criteria
                - model_type: Filter by model type
                - tags: List of tags to filter by
                - min_size: Minimum model size in bytes
                - max_size: Maximum model size in bytes
                
        Returns:
            Filtered list of models
        """
        filtered = models
        
        if "model_type" in filters:
            model_type = ModelType(filters["model_type"])
            filtered = [m for m in filtered if m.model_type == model_type]
        
        if "tags" in filters:
            tags = set(tag.lower() for tag in filters["tags"])
            filtered = [
                m for m in filtered 
                if any(tag in (t.lower() for t in m.tags) for tag in tags)
            ]
        
        if "min_size" in filters and filters["min_size"] is not None:
            filtered = [m for m in filtered if m.size and m.size >= filters["min_size"]]
        
        if "max_size" in filters and filters["max_size"] is not None:
            filtered = [m for m in filtered if m.size and m.size <= filters["max_size"]]
        
        return filtered
    
    def get_model(
        self, 
        model_id: str, 
        source: Optional[str] = None
    ) -> Optional[ModelMetadata]:
        """Get a model by ID.
        
        Args:
            model_id: The model ID
            source: Optional source to look in ('ollama', 'huggingface')
            
        Returns:
            ModelMetadata if found, None otherwise
        """
        if source:
            return self._get_manager(source).get_model(model_id)
        
        # Search in all sources if no source is specified
        for manager in self._managers.values():
            try:
                model = manager.get_model(model_id)
                if model:
                    return model
            except Exception as e:
                logger.debug(f"Error getting model {model_id} from {manager.__class__.__name__}: {e}")
        
        return None
    
    def install_model(
        self, 
        model_id: str, 
        source: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Install a model.
        
        Args:
            model_id: The model ID to install
            source: Source to install from ('ollama', 'huggingface')
            **kwargs: Additional installation options
                - force: Force reinstall if already installed
                - progress_callback: Callback for progress updates
                
        Returns:
            bool: True if installation was successful
            
        Raises:
            ModelInstallationError: If installation fails
            ValueError: If source is not specified and model ID is ambiguous
        """
        if not source:
            # Try to determine source from model ID
            if ":" in model_id:
                source = model_id.split(":")[0]
            else:
                # Check which manager can handle this model
                possible_sources = []
                for src, manager in self._managers.items():
                    try:
                        if manager.get_model(model_id):
                            possible_sources.append(src)
                    except Exception:
                        pass
                
                if not possible_sources:
                    raise ModelInstallationError(f"Could not find model {model_id} in any source")
                if len(possible_sources) > 1:
                    raise ValueError(
                        f"Model ID {model_id} is ambiguous. "
                        f"Please specify a source: {', '.join(possible_sources)}"
                    )
                source = possible_sources[0]
        
        manager = self._get_manager(source)
        return manager.install_model(model_id, **kwargs)
    
    def uninstall_model(
        self, 
        model_id: str, 
        source: Optional[str] = None
    ) -> bool:
        """Uninstall a model.
        
        Args:
            model_id: The model ID to uninstall
            source: Source to uninstall from ('ollama', 'huggingface')
            
        Returns:
            bool: True if uninstallation was successful
        """
        if not source:
            # Try to find which manager has this model
            for src, manager in self._managers.items():
                try:
                    if manager.is_model_installed(model_id):
                        return manager.uninstall_model(model_id)
                except Exception as e:
                    logger.debug(f"Error checking if model {model_id} is installed in {src}: {e}")
            return False
        
        return self._get_manager(source).uninstall_model(model_id)
    
    def is_model_installed(
        self, 
        model_id: str, 
        source: Optional[str] = None
    ) -> bool:
        """Check if a model is installed.
        
        Args:
            model_id: The model ID to check
            source: Source to check in ('ollama', 'huggingface')
            
        Returns:
            bool: True if the model is installed
        """
        if source:
            return self._get_manager(source).is_model_installed(model_id)
        
        # Check all sources if no source is specified
        for manager in self._managers.values():
            try:
                if manager.is_model_installed(model_id):
                    return True
            except Exception as e:
                logger.debug(f"Error checking if model {model_id} is installed: {e}")
        
        return False
    
    def search_models(
        self, 
        query: str, 
        source: Optional[str] = None,
        limit: int = 10,
        **filters
    ) -> List[ModelMetadata]:
        """Search for models.
        
        Args:
            query: Search query
            source: Source to search in ('ollama', 'huggingface')
            limit: Maximum number of results to return
            **filters: Additional filters to apply
                - model_type: Filter by model type
                - tags: List of tags to filter by
                - min_size: Minimum model size in bytes
                - max_size: Maximum model size in bytes
                
        Returns:
            List of matching ModelMetadata objects
        """
        if source:
            manager = self._get_manager(source)
            if hasattr(manager, 'search_models'):
                return manager.search_models(query, limit=limit, **filters)
            # Fall back to client-side filtering if search is not implemented
            models = manager.list_models()
        else:
            # Search in all sources
            models = self.list_models()
        
        # Simple client-side search
        query = query.lower()
        results = [
            m for m in models 
            if (query in m.name.lower() or 
                query in (m.description or "").lower() or
                any(query in tag.lower() for tag in m.tags))
        ]
        
        # Apply additional filters
        if filters:
            results = self._filter_models(results, **filters)
        
        return results[:limit]
    
    def get_manager(self, source: str) -> BaseModelManager:
        """Get the model manager for a specific source.
        
        Args:
            source: Model source ('ollama', 'huggingface')
            
        Returns:
            The model manager instance
            
        Raises:
            ValueError: If the source is not supported
        """
        return self._get_manager(source)
    
    def set_default_model(self, model_id: str) -> bool:
        """Set the default model.
        
        Args:
            model_id: The model ID to set as default
            
        Returns:
            bool: True if the default model was set successfully
        """
        if not self.is_model_installed(model_id):
            return False
        
        self.default_model = model_id
        return True
    
    def update_models_cache(self, source: Optional[str] = None) -> bool:
        """Update the models cache.
        
        Args:
            source: Source to update ('ollama', 'huggingface')
            
        Returns:
            bool: True if the cache was updated successfully
        """
        if source:
            manager = self._get_manager(source)
            if hasattr(manager, 'update_cache'):
                return manager.update_cache()
            return False
        
        # Update all managers that support it
        success = True
        for manager in self._managers.values():
            try:
                if hasattr(manager, 'update_cache'):
                    if not manager.update_cache():
                        success = False
            except Exception as e:
                logger.error(f"Error updating cache for {manager.__class__.__name__}: {e}")
                success = False
        
        return success
        return self.models
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """
        Get information about a specific model.
        
        Args:
            model_name: The name of the model to get information about.
            
        Returns:
            A dictionary containing model information, or None if not found.
        """
        return get_model_metadata(model_name)
    
    def install_model(self, model_name: str) -> bool:
        """
        Install a model using Ollama.
        
        Args:
            model_name: The name of the model to install.
            
        Returns:
            True if installation was successful, False otherwise.
        """
        return install_model(model_name)
    
    def list_installed_models(self) -> List[str]:
        """
        List models that are currently installed.
        
        Returns:
            A list of installed model names.
        """
        return list_installed_models()
    
    def set_default_model(self, model_name: str) -> bool:
        """
        Set the default model to use.
        
        Args:
            model_name: The name of the model to set as default.
            
        Returns:
            True if successful, False otherwise.
        """
        if any(m['name'] == model_name for m in self.models):
            self.default_model = model_name
            return set_default_model(model_name)
        return False
    
    def get_default_model_name(self) -> str:
        """
        Get the name of the current default model.
        
        Returns:
            The name of the default model.
        """
        return self.default_model
    
    def query(
        self,
        prompt: str,
        model: Optional[str] = None,
        source: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Query a model with a prompt.
        
        Args:
            prompt: The input prompt to send to the model
            model: The model to use (defaults to the default model)
            source: The model source ('ollama' or 'huggingface'). If not specified,
                   will try to determine from the model name or use the default source.
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            The generated text response
            
        Raises:
            ModelError: If there's an error querying the model
            ValueError: If the model is not found or the source is not supported
        """
        # Use default model if none specified
        if model is None:
            model = self.default_model
            if not model:
                raise ValueError("No model specified and no default model set")
        
        # Try to determine source from model name if not specified
        if source is None and ":" in model:
            source, model = model.split(":", 1)
        
        # Get the appropriate model manager
        try:
            manager = self._get_manager(source)
        except ValueError as e:
            raise ValueError(
                f"Could not determine model source for '{model}'. "
                f"Please specify source with source='ollama' or source='huggingface'"
            ) from e
        
        # Check if the model is installed
        if not manager.is_model_installed(model):
            logger.info(f"Model {model} not found, attempting to install...")
            if not manager.install_model(model):
                raise ModelError(f"Failed to install model: {model}")
        
        # Delegate the query to the model manager
        try:
            return manager.query(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
        except Exception as e:
            raise ModelError(f"Error querying model {model}: {str(e)}") from e
    
    def update_models_from_remote(self, source: str = "ollama", 
                                query: str = None, 
                                interactive: bool = True) -> List[Dict]:
        """
        Update the models list from a remote source.
        
        Args:
            source: The source to update from ("ollama" or "huggingface").
            query: The search query for Hugging Face models.
            interactive: Whether to allow interactive selection for Hugging Face models.
            
        Returns:
            The updated list of models.
        """
        if source.lower() == "huggingface":
            return self.update_models_from_huggingface(query, interactive)
        elif source.lower() == "ollama":
            return self.update_models_from_ollama()
        else:
            logger.warning(f"Unknown source: {source}")
            return self.models
    
    def search_huggingface_models(self, query: str = None, limit: int = 20) -> List[Dict]:
        """
        Search for models on Hugging Face.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of model dictionaries.
        """
        return search_huggingface_models(query, limit)
    
    def interactive_model_search(self, query: str = None) -> Optional[str]:
        """
        Interactive search for models on Hugging Face.
        
        Args:
            query: The search query.
            
        Returns:
            The selected model ID or None if cancelled.
        """
        return interactive_model_search(query, check_ollama=True)
    
    def update_models_from_huggingface(self, query: str = None, 
                                     interactive: bool = True) -> List[Dict]:
        """
        Update models from Hugging Face.
        
        Args:
            query: The search query.
            interactive: Whether to use interactive mode.
            
        Returns:
            The updated list of models.
        """
        from .huggingface import update_models_from_huggingface
        return update_models_from_huggingface(query, interactive)
    
    def update_models_from_ollama(self) -> List[Dict]:
        """
        Update models from Ollama.
        
        Returns:
            The updated list of models.
        """
        success, message = update_ollama_models_cache()
        if not success:
            logger.warning(f"Failed to update Ollama models: {message}")
        
        # Reload models
        self.models = self.get_available_models()
        return self.models
