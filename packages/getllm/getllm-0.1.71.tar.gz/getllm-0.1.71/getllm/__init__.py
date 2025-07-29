#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
getLLM: A package for managing LLM models with Ollama and Hugging Face integration.

This package provides functionality for managing, installing, and configuring
LLM models from various sources including Ollama and Hugging Face.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from .models import (
    ModelManager,
    ModelMetadataManager,
    HuggingFaceModelManager,
    OllamaModelManager,
    get_models,
    get_huggingface_models,
    update_models_from_huggingface,
    get_default_model,
    set_default_model,
    install_model,
    list_installed_models,
    search_huggingface_models,
    interactive_model_search,
    update_models_from_ollama
)

from .ollama import (
    OllamaServer,
    get_ollama_integration,
    start_ollama_server,
    install_ollama_model,
    list_ollama_models,
    OllamaError,
    ModelNotFoundError
)

# For backward compatibility (deprecated)
OllamaIntegration = OllamaServer

__version__ = '0.2.0'

__all__ = [
    # Main classes
    'ModelManager',
    'HuggingFaceModelManager',
    'OllamaModelManager',
    'ModelMetadataManager',
    'OllamaIntegration',
    
    # Utility functions
    'get_models_dir',
    'get_default_model',
    'set_default_model',
    'get_models_metadata_path',
    'get_central_env_path',
    
    # Ollama integration (legacy - deprecated)
    'OllamaIntegration',  # Deprecated, use OllamaServer instead
    'get_ollama_integration',  # Deprecated, use OllamaServer directly
    'start_ollama_server',  # Deprecated, use OllamaServer directly
    'install_ollama_model',  # Deprecated, use OllamaServer.install_model()
    'list_ollama_models'  # Deprecated, use OllamaServer.list_models()
]
