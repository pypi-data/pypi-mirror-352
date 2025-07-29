"""
Ollama model integration for PyLLM.

This module provides functionality for working with Ollama models,
including downloading, loading, and interacting with them through a
unified interface.
"""

from typing import List, Dict, Any, Optional

from .manager import OllamaModelManager, get_ollama_model_manager


def search_ollama_models(
    query: str = "",
    tags: Optional[List[str]] = None,
    limit: int = 10,
    **kwargs
) -> List[Dict[str, Any]]:
    """Search for Ollama models.
    
    Args:
        query: Search query string
        tags: List of tags to filter by
        limit: Maximum number of results to return
        **kwargs: Additional search parameters
        
    Returns:
        List of model dictionaries with metadata
    """
    manager = get_ollama_model_manager()
    return manager.search_models(query=query, tags=tags, limit=limit, **kwargs)


__all__ = [
    'OllamaModelManager',
    'get_ollama_model_manager',
    'search_ollama_models'
]
