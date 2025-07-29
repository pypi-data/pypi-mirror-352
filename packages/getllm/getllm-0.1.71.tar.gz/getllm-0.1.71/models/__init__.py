"""
Model management for PyLLM.

This package provides functionality for managing LLM models, including
installation, listing, and updating models from various sources.
"""

import os
import sys
import subprocess
from pathlib import Path

# --- Auto dependency setup ---
REQUIRED_PACKAGES = ["requests", "bs4", "python-dotenv"]
IMPORT_NAMES = ["requests", "bs4", "dotenv"]  # Correct import for python-dotenv
VENV_DIR = os.path.join(os.path.dirname(__file__), ".venv")

# 1. Create venv if missing
if not os.path.isdir(VENV_DIR):
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
    print(f"Created virtual environment: {VENV_DIR}")

def _venv_python():
    """Get the path to the Python interpreter in the virtual environment."""
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")

# 2. Install missing packages
missing = []
for pkg, imp in zip(REQUIRED_PACKAGES, IMPORT_NAMES):
    try:
        __import__(imp)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f"Installing missing packages: {', '.join(missing)}")
    subprocess.run([_venv_python(), "-m", "pip", "install"] + missing, check=True)
    print("Required dependencies installed. Please restart the script.")
    sys.exit(0)
# --- End auto dependency setup ---

# Import the main components
from .manager import ModelManager
from .constants import DEFAULT_MODELS, DEFAULT_HF_MODELS
from .huggingface.manager import HuggingFaceModelManager, get_hf_model_manager
from .huggingface.cache import load_huggingface_models_from_cache, update_huggingface_models_cache
from .utils import (
    get_models_dir,
    get_models_metadata_path,
    get_hf_models_cache_path,
    get_ollama_models_cache_path,
    get_default_model,
    set_default_model,
    get_models,
    install_model,
    list_installed_models,
    get_model_metadata,
    load_ollama_models_from_cache,
    save_models_to_json,
    load_models_from_json,
    ensure_models_dir
)

# For backward compatibility
update_models_metadata = save_models_to_json
update_models_from_ollama = load_ollama_models_from_cache
update_models_from_huggingface = load_huggingface_models_from_cache
update_huggingface_models_cache = update_huggingface_models_cache

# Import additional components
# Import these at the end to avoid circular imports
def _import_huggingface():
    from .huggingface import search_huggingface_models
    from .huggingface.cache import update_huggingface_models_cache, load_huggingface_models_from_cache
    
    return {
        'search_huggingface_models': search_huggingface_models,
        'update_huggingface_models_cache': update_huggingface_models_cache,
        'load_huggingface_models_from_cache': load_huggingface_models_from_cache
    }

# Import Ollama components
from .ollama.manager import (
    get_ollama_model_manager,
    OllamaModelManager
)

# Create a default manager instance
ollama_manager = get_ollama_model_manager()

# Define wrapper functions for backward compatibility
def update_ollama_models_cache():
    """Update the cache of available Ollama models."""
    return ollama_manager._fetch_models_from_api() is not None

def list_ollama_models():
    """List all available Ollama models."""
    return ollama_manager.list_models()

def install_ollama_model(model_name: str, **kwargs):
    """Install an Ollama model."""
    return ollama_manager.install_model(model_name, **kwargs)

def search_ollama_models(query: str = "", limit: int = 10, **kwargs):
    """Search for Ollama models."""
    return ollama_manager.search_models(query=query, limit=limit, **kwargs)

# Import interactive utilities
from .utils.interactive import interactive_model_search

# Import Hugging Face components after other imports to avoid circular imports
huggingface_exports = _import_huggingface()
search_huggingface_models = huggingface_exports['search_huggingface_models']
update_huggingface_models_cache = huggingface_exports['update_huggingface_models_cache']
load_huggingface_models_from_cache = huggingface_exports['load_huggingface_models_from_cache']

__all__ = [
    # Main classes
    'ModelManager',
    'HuggingFaceModelManager',
    'OllamaModelManager',
    
    # Manager instances
    'ollama_manager',
    
    # Constants
    'DEFAULT_MODELS',
    'DEFAULT_HF_MODELS',
    
    # Functions
    'get_models_dir',
    'get_models_metadata_path',
    'get_hf_models_cache_path',
    'get_ollama_models_cache_path',
    'get_default_model',
    'set_default_model',
    'get_models',
    'install_model',
    'list_installed_models',
    'get_model_metadata',
    'save_models_to_json',
    'load_models_from_json',
    'ensure_models_dir',
    'interactive_model_search',
    
    # Hugging Face functions
    'search_huggingface_models',
    'update_huggingface_models_cache',
    'load_huggingface_models_from_cache',
    'get_hf_model_manager',
    
    # Ollama functions
    'update_ollama_models_cache',
    'list_ollama_models',
    'install_ollama_model',
    'search_ollama_models',
]

# Initialize the default model manager instance
model_manager = ModelManager()
