"""
Configuration utilities for the getllm application.
"""
import os
import json
import platform
from pathlib import Path
from typing import Optional, Dict, Any
import dotenv
import appdirs


def get_central_env_path() -> Path:
    """
    Get the path to the central .env file in the PyLama root directory.
    
    Returns:
        Path to the central .env file.
    """
    # Start from the current directory and go up to find the py-lama directory
    current_dir = Path(__file__).parent.parent.absolute()
    
    # Check if we're in a subdirectory of py-lama
    parts = current_dir.parts
    for i in range(len(parts) - 1, 0, -1):
        if parts[i] == "py-lama":
            return Path(*parts[:i+1]) / "devlama" / ".env"
    
    # If not found, look for the directory structure
    while current_dir != current_dir.parent:  # Stop at the root directory
        # Check if this looks like the py-lama directory
        if (current_dir / "devlama").exists() and (current_dir / "loglama").exists():
            return current_dir / "devlama" / ".env"
        if (current_dir / "devlama").exists() and (current_dir / "getllm").exists():
            return current_dir / "devlama" / ".env"
        
        # Move up one directory
        current_dir = current_dir.parent
    
    # If no central .env found, fall back to local .env
    return Path(__file__).parent.parent / ".env"


def get_config_dir() -> Path:
    """
    Get the configuration directory for the application.
    
    Returns:
        Path to the configuration directory.
    """
    # Use appdirs to get the appropriate config directory for the OS
    config_dir = Path(appdirs.user_config_dir("getllm"))
    
    # Create the directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    return config_dir


def get_models_dir() -> Path:
    """
    Get the models directory from the environment variables.
    
    Returns:
        Path to the models directory.
    """
    # Try to load from the central .env file first
    central_env_path = get_central_env_path()
    env = {}
    
    if central_env_path.exists():
        env = dotenv.dotenv_values(central_env_path)
    
    # Then try to load from local .env if it exists
    local_env_path = Path(__file__).parent.parent / ".env"
    if local_env_path.exists():
        local_env = dotenv.dotenv_values(local_env_path)
        env.update(local_env)
    
    # Get models directory from environment or use default
    models_dir = env.get("MODELS_DIR")
    if not models_dir:
        # Default to ~/.cache/getllm/models
        models_dir = Path.home() / ".cache" / "getllm" / "models"
    else:
        models_dir = Path(models_dir)
    
    # Create directory if it doesn't exist
    models_dir.mkdir(parents=True, exist_ok=True)
    
    return models_dir


def get_models_metadata_path() -> Path:
    """
    Get the path to the models metadata file.
    
    Returns:
        Path to the models metadata JSON file in the ~/.getllm/logs/ directory.
    """
    # Create the logs directory if it doesn't exist
    log_dir = Path.home() / ".getllm" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "models_metadata.json"


def get_default_model() -> Optional[str]:
    """
    Get the default model from the environment variables.
    
    Returns:
        The default model name, or None if not set.
    """
    # Try to load from the central .env file first
    central_env_path = get_central_env_path()
    env = {}
    
    if central_env_path.exists():
        env = dotenv.dotenv_values(central_env_path)
    
    # Then try to load from local .env if it exists
    local_env_path = Path(__file__).parent.parent / ".env"
    if local_env_path.exists():
        local_env = dotenv.dotenv_values(local_env_path)
        env.update(local_env)
    
    return env.get("DEFAULT_MODEL")


def set_default_model(model_name: str) -> bool:
    """
    Set the default model in the environment variables.
    
    Args:
        model_name: The name of the model to set as default.
        
    Returns:
        True if successful, False otherwise.
    """
    # First try to update the central .env file
    central_env_path = get_central_env_path()
    env_updated = False
    
    if central_env_path.exists():
        # Load existing variables
        env = dotenv.dotenv_values(central_env_path)
        env["DEFAULT_MODEL"] = model_name
        
        # Write back to the file
        try:
            with open(central_env_path, 'w') as f:
                for key, value in env.items():
                    # Skip comments and empty lines
                    if key.startswith('#') or not key.strip():
                        continue
                    f.write(f"{key}={value}\n")
            env_updated = True
        except IOError:
            env_updated = False
    
    # If central .env update failed or doesn't exist, try local .env
    if not env_updated:
        local_env_path = Path(__file__).parent.parent / ".env"
        
        # Load existing variables if file exists
        env = {}
        if local_env_path.exists():
            env = dotenv.dotenv_values(local_env_path)
        
        # Update the default model
        env["DEFAULT_MODEL"] = model_name
        
        # Write back to the file
        try:
            with open(local_env_path, 'w') as f:
                for key, value in env.items():
                    # Skip comments and empty lines
                    if key.startswith('#') or not key.strip():
                        continue
                    f.write(f"{key}={value}\n")
            return True
        except IOError:
            return False
    
    return env_updated


__all__ = [
    'get_config_dir',
    'get_models_dir',
    'get_models_metadata_path',
    'get_default_model',
    'set_default_model',
    'get_central_env_path'
]
