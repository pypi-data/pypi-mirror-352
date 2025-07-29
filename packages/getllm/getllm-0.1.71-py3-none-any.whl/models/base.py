"""
Base classes for model management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, TypeVar, Generic, Any
from pathlib import Path


class ModelSource(str, Enum):
    """Enum representing different model sources."""
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    LOCAL = "local"
    OTHER = "other"


class ModelType(str, Enum):
    """Enum representing different model types."""
    TEXT = "text"
    CODE = "code"
    CHAT = "chat"
    EMBEDDING = "embedding"
    MULTIMODAL = "multimodal"


@dataclass
class ModelMetadata:
    """Metadata for a model."""
    id: str
    name: str
    description: str = ""
    source: ModelSource = ModelSource.OTHER
    model_type: ModelType = ModelType.TEXT
    size: Optional[int] = None  # Size in bytes
    parameters: Optional[int] = None  # Number of parameters (e.g., 7B, 13B)
    tags: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class BaseModel(ABC):
    """Base class for all model implementations."""
    
    def __init__(self, metadata: ModelMetadata):
        """Initialize with model metadata."""
        self.metadata = metadata
    
    @property
    def id(self) -> str:
        """Get the model ID."""
        return self.metadata.id
    
    @property
    def name(self) -> str:
        """Get the model name."""
        return self.metadata.name
    
    @abstractmethod
    def load(self):
        """Load the model into memory."""
        pass
    
    @abstractmethod
    def unload(self):
        """Unload the model from memory."""
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if the model is loaded in memory."""
        pass


class BaseModelManager(ABC):
    """Base class for model managers."""
    
    @abstractmethod
    def list_models(self) -> List[ModelMetadata]:
        """List all available models."""
        pass
    
    @abstractmethod
    def get_model(self, model_id: str) -> Optional[BaseModel]:
        """Get a model by ID."""
        pass
    
    @abstractmethod
    def install_model(self, model_id: str, **kwargs) -> bool:
        """Install a model."""
        pass
    
    @abstractmethod
    def uninstall_model(self, model_id: str) -> bool:
        """Uninstall a model."""
        pass
    
    @abstractmethod
    def is_model_installed(self, model_id: str) -> bool:
        """Check if a model is installed."""
        pass


# Type variable for model managers
M = TypeVar('M', bound=BaseModelManager)
