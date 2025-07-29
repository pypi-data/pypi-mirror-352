"""
Ollama model management for PyLLM.
"""

import os
import re
import json
import logging
import subprocess
from typing import List, Dict, Optional, Tuple

from .constants import get_ollama_models_cache_path

logger = logging.getLogger(__name__)

def update_ollama_models_cache(save_to_cache: bool = True, limit: int = 50) -> Tuple[bool, str]:
    """
    Fetch the latest coding-related models from the Ollama library.
    
    Args:
        save_to_cache: Whether to save the models to the cache file.
        limit: Maximum number of models to fetch.
        
    Returns:
        A tuple of (success, message)
    """
    try:
        # Check if Ollama is installed
        try:
            result = subprocess.run(['ollama', '--version'], 
                                 capture_output=True, text=True)
            if result.returncode != 0:
                return False, "Ollama is not installed or not in PATH"
        except FileNotFoundError:
            return False, "Ollama is not installed or not in PATH"
        
        # Get list of available models
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            return False, f"Failed to list Ollama models: {result.stderr}"
        
        # Parse the output
        models = []
        lines = result.stdout.strip().split('\n')
        
        # Skip header line
        for line in lines[1:]:
            if not line.strip():
                continue
                
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 2:
                model_name = parts[0]
                model_id = parts[1]
                
                # Skip empty models
                if not model_name or model_name == '<none>':
                    continue
                    
                models.append({
                    'name': model_name,
                    'id': model_id,
                    'source': 'ollama',
                    'description': f"Ollama model: {model_name}",
                    'size': extract_model_size(model_name)
                })
                
                if len(models) >= limit:
                    break
        
        # Save to cache if requested
        if save_to_cache and models:
            cache_path = get_ollama_models_cache_path()
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2, ensure_ascii=False)
        
        return True, f"Found {len(models)} Ollama models"
        
    except Exception as e:
        error_msg = f"Error updating Ollama models cache: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def extract_model_size(model_name: str) -> str:
    """Extract model size from model name."""
    # Look for patterns like 7b, 13b, 70b, etc.
    match = re.search(r'(\d+[bB])', model_name)
    if match:
        return match.group(1).upper()
    
    # Check for size in the name
    for size in ['7b', '13b', '20b', '30b', '65b', '70b']:
        if size in model_name.lower():
            return size.upper()
    
    return 'Unknown'

def install_ollama_model(model_name: str) -> Tuple[bool, str]:
    """
    Install a model using Ollama.
    
    Args:
        model_name: The name of the model to install.
        
    Returns:
        A tuple of (success, message)
    """
    try:
        # Check if Ollama is installed
        try:
            result = subprocess.run(['ollama', '--version'], 
                                 capture_output=True, text=True)
            if result.returncode != 0:
                return False, "Ollama is not installed or not in PATH"
        except FileNotFoundError:
            return False, "Ollama is not installed or not in PATH"
        
        # Install the model
        logger.info(f"Installing model: {model_name}")
        print(f"Downloading {model_name} (this may take a while)...")
        
        process = subprocess.Popen(
            ['ollama', 'pull', model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Stream the output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Check the result
        if process.returncode == 0:
            return True, f"Successfully installed model: {model_name}"
        else:
            error = process.stderr.read()
            return False, f"Failed to install model: {error}"
            
    except Exception as e:
        error_msg = f"Error installing model {model_name}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def list_ollama_models() -> List[Dict]:
    """
    List all models available in Ollama.
    
    Returns:
        A list of dictionaries containing model information.
    """
    try:
        # Check if Ollama is installed
        try:
            result = subprocess.run(['ollama', '--version'], 
                                 capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Ollama is not installed or not in PATH")
                return []
        except FileNotFoundError:
            logger.error("Ollama is not installed or not in PATH")
            return []
        
        # Get list of available models
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Failed to list Ollama models: {result.stderr}")
            return []
        
        # Parse the output
        models = []
        lines = result.stdout.strip().split('\n')
        
        # Skip header line
        for line in lines[1:]:
            if not line.strip():
                continue
                
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 2:
                model_name = parts[0]
                model_id = parts[1]
                
                # Skip empty models
                if not model_name or model_name == '<none>':
                    continue
                    
                models.append({
                    'name': model_name,
                    'id': model_id,
                    'source': 'ollama',
                    'description': f"Ollama model: {model_name}",
                    'size': extract_model_size(model_name)
                })
        
        return models
        
    except Exception as e:
        logger.error(f"Error listing Ollama models: {str(e)}")
        return []
