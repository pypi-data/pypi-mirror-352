"""
Hugging Face model integration for PyLLM.

This module provides functionality for working with Hugging Face models,
including downloading, loading, and interacting with them through a
unified interface.
"""

from typing import List, Dict, Any, Optional
from .manager import HuggingFaceModelManager, get_hf_model_manager
from .cache import update_huggingface_models_cache, load_huggingface_models_from_cache

def search_huggingface_models(
    query: str = "",
    tags: Optional[List[str]] = None,
    limit: int = 10,
    **kwargs
) -> List[Dict[str, Any]]:
    """Search for Hugging Face models.
    
    Args:
        query: Search query string
        tags: List of tags to filter by
        limit: Maximum number of results to return
        **kwargs: Additional search parameters
        
    Returns:
        List of model dictionaries with metadata
    """
    manager = get_hf_model_manager()
    return manager.search_models(query=query, tags=tags, limit=limit, **kwargs)

__all__ = [
    'HuggingFaceModelManager',
    'get_hf_model_manager',
    'search_huggingface_models',
    'update_huggingface_models_cache',
    'load_huggingface_models_from_cache'
]
