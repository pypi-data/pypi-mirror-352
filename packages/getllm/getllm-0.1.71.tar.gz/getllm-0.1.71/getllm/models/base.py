"""
Base model manager class that defines the interface for all model managers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseModelManager(ABC):
    """Abstract base class for model managers."""
    
    @abstractmethod
    def get_available_models(self) -> List[Dict]:
        """Get a list of available models."""
        pass
    
    @abstractmethod
    def install_model(self, model_name: str) -> bool:
        """Install a model.
        
        Args:
            model_name: Name of the model to install.
            
        Returns:
            bool: True if installation was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def list_installed_models(self) -> List[str]:
        """List all installed models.
        
        Returns:
            List of installed model names.
        """
        pass


class ModelManager(BaseModelManager):
    """Main model manager that delegates to specific model managers."""
    
    def __init__(self):
        from .huggingface import HuggingFaceModelManager
        from .ollama import OllamaModelManager
        
        self.hf_manager = HuggingFaceModelManager()
        self.ollama_manager = OllamaModelManager()
        self.default_model = self.get_default_model_name()
        self.models = self.get_available_models()
    
    def get_available_models(self) -> List[Dict]:
        """Get all available models from all sources."""
        hf_models = self.hf_manager.get_available_models()
        ollama_models = self.ollama_manager.get_available_models()
        return hf_models + ollama_models
    
    def install_model(self, model_name: str) -> bool:
        """Install a model from any source."""
        # Try Ollama first, then Hugging Face
        if self.ollama_manager.install_model(model_name):
            return True
        return self.hf_manager.install_model(model_name)
    
    def list_installed_models(self) -> List[str]:
        """List all installed models from all sources."""
        installed = set(self.ollama_manager.list_installed_models())
        installed.update(self.hf_manager.list_installed_models())
        return list(installed)
    
    def get_default_model_name(self) -> str:
        """Get the default model name."""
        from ..utils.config import get_default_model
        return get_default_model() or "llama3"
    
    def set_default_model(self, model_name: str) -> None:
        """Set the default model."""
        from ..utils.config import set_default_model
        set_default_model(model_name)
        self.default_model = model_name
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a specific model."""
        # Try Ollama first, then Hugging Face
        info = self.ollama_manager.get_model_info(model_name)
        if info is None:
            info = self.hf_manager.get_model_info(model_name)
        return info
