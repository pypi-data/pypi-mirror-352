"""
Helper functions for the Ollama integration.
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger('getllm.ollama.utils.helpers')

def get_default_model() -> str:
    """Get the default model name.
    
    Returns:
        str: The default model name
    """
    return os.getenv('OLLAMA_MODEL', 'llama3')

def format_model_name(model_name: str) -> str:
    """Format a model name for display.
    
    Args:
        model_name: The raw model name
        
    Returns:
        The formatted model name
    """
    # Remove any tag/version if present
    if ':' in model_name:
        model_name = model_name.split(':', 1)[0]
    # Replace hyphens and underscores with spaces and title case
    return model_name.replace('-', ' ').replace('_', ' ').title()

def parse_model_name(model_name: str) -> Dict[str, str]:
    """Parse a model name into its components.
    
    Args:
        model_name: The model name to parse (e.g., 'llama3:7b')
        
    Returns:
        Dictionary with parsed components (name, tag, version, etc.)
    """
    parts = model_name.split(':', 1)
    result = {'full_name': model_name, 'name': parts[0], 'tag': 'latest'}
    
    if len(parts) > 1:
        result['tag'] = parts[1]
    
    # Try to extract version from name (e.g., 'llama2-7b' -> '7b')
    version_match = re.search(r'-(\d+[bBmM]|\d+\.\d+[bBmM]?)$', result['name'])
    if version_match:
        result['version'] = version_match.group(1)
        result['base_name'] = result['name'][:version_match.start()]
    else:
        result['version'] = None
        result['base_name'] = result['name']
    
    return result

def validate_model_name(model_name: str) -> bool:
    """Validate a model name.
    
    Args:
        model_name: The model name to validate
        
    Returns:
        bool: True if the model name is valid, False otherwise
    """
    if not model_name or not isinstance(model_name, str):
        return False
    
    # Basic validation - alphanumeric, underscores, hyphens, colons, dots
    if not re.match(r'^[a-zA-Z0-9_\-\.:]+$', model_name):
        return False
    
    return True

def get_model_disk_usage(model_name: str) -> Optional[int]:
    """Get the disk usage of a model in bytes.
    
    Args:
        model_name: The name of the model
        
    Returns:
        The size of the model in bytes, or None if unknown
    """
    try:
        # Try to get model info from the API
        from ..api.endpoints import get_api_client
        client = get_api_client()
        model_info = client.get_model(model_name)
        return model_info.get('size_bytes')
    except Exception as e:
        logger.warning(f"Could not get disk usage for model {model_name}: {e}")
        return None

def check_disk_space(required_bytes: int, path: Optional[str] = None) -> Tuple[bool, int]:
    """Check if there's enough disk space available.
    
    Args:
        required_bytes: Number of bytes required
        path: Path to check disk space for (default: current working directory)
        
    Returns:
        Tuple of (has_enough_space, available_bytes)
    """
    path = path or os.getcwd()
    try:
        total, used, free = shutil.disk_usage(path)
        return (free >= required_bytes, free)
    except Exception as e:
        logger.warning(f"Could not check disk space: {e}")
        # If we can't check, assume there's enough space
        return (True, float('inf'))

def format_bytes(size_bytes: int) -> str:
    """Format a size in bytes to a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., '1.2 MB')
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {units[i]}"

def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def ensure_directory_exists(directory: str) -> None:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        raise
