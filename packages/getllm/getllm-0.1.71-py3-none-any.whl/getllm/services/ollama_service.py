"""
Service for interacting with Ollama models.
"""
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
import requests

from ..utils.config import get_models_dir


class OllamaService:
    """Service for interacting with Ollama models."""
    
    def __init__(self):
        # Use the logs directory in the user's home directory for cache
        self.logs_dir = Path.home() / ".getllm" / "logs"
        self.cache_file = self.logs_dir / "ollama_models.json"
        
        # Ensure the logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def list_models(self) -> List[Dict]:
        """List all available Ollama models.
        
        Returns:
            List of dictionaries containing model information.
        """
        # First try to load from cache
        cached_models = self._load_cached_models()
        if cached_models:
            return cached_models
            
        # If no cache, try to fetch from Ollama
        models = self._fetch_models_from_ollama()
        if models:
            self._save_models_to_cache(models)
            return models
            
        return []
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a specific Ollama model.
        
        Args:
            model_name: The name of the model to get information about.
            
        Returns:
            Dictionary containing model information, or None if not found.
        """
        try:
            # Try using the API first
            try:
                response = requests.get(f"http://localhost:11434/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get('models', []):
                        if model.get('name') == model_name or model.get('model') == model_name:
                            return model
            except requests.exceptions.RequestException:
                pass
                
            # Fallback to CLI if API fails
            try:
                result = subprocess.run(
                    ["ollama", "show", "--json", model_name],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return json.loads(result.stdout)
            except (subprocess.SubprocessError, json.JSONDecodeError):
                pass
                
            return None
            
        except (subprocess.SubprocessError, json.JSONDecodeError):
            return None
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from the Ollama library.
        
        Args:
            model_name: The name of the model to pull.
            
        Returns:
            True if the pull was successful, False otherwise.
        """
        try:
            # Try using the API first
            try:
                response = requests.post(
                    "http://localhost:11434/api/pull",
                    json={"name": model_name},
                    stream=True
                )
                
                if response.status_code == 200:
                    # Read the response in chunks to show progress
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                status = data.get('status', '')
                                if status:
                                    print(f"Status: {status}")
                            except json.JSONDecodeError:
                                pass
                    
                    # Update the cache after successful pull
                    self.update_models_cache()
                    return True
                
                return False
                
            except requests.exceptions.RequestException:
                # Fallback to CLI if API fails
                try:
                    result = subprocess.run(
                        ["ollama", "pull", model_name],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        # Update the cache after successful pull
                        self.update_models_cache()
                        return True
                        
                    return False
                    
                except subprocess.SubprocessError as e:
                    print(f"Error pulling model: {str(e)}")
                    return False
                    
        except Exception as e:
            print(f"Error in pull_model: {str(e)}")
            return False
    
    def list_installed_models(self) -> List[str]:
        """List all installed Ollama models.
        
        Returns:
            List of installed model names.
        """
        try:
            # Try using the API first
            try:
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [model.get('name', '') for model in data.get('models', [])]
            except requests.exceptions.RequestException:
                pass
                
            # Fallback to CLI if API fails
            try:
                result = subprocess.run(
                    ["ollama", "list", "--json"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    models = json.loads(result.stdout)
                    return [model.get('name') for model in models if 'name' in model]
            except (subprocess.SubprocessError, json.JSONDecodeError):
                pass
                
            return []
            
        except Exception as e:
            print(f"Error listing installed models: {str(e)}")
            return []
    
    def update_models_cache(self) -> bool:
        """Update the local cache of Ollama models.
        
        Returns:
            True if successful, False otherwise.
        """
        models = self._fetch_models_from_ollama()
        if models:
            return self._save_models_to_cache(models)
        return False
    
    def _fetch_models_from_ollama(self) -> List[Dict]:
        """Fetch models from the Ollama library.
        
        Returns:
            List of model dictionaries.
        """
        try:
            # First, check if Ollama is running
            try:
                response = requests.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = data.get('models', [])
                    
                    # Get list of installed models
                    installed_models = {}
                    try:
                        result = subprocess.run(
                            ["ollama", "list", "--json"],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            installed = json.loads(result.stdout)
                            installed_models = {m['name']: m for m in installed if 'name' in m}
                    except (subprocess.SubprocessError, json.JSONDecodeError):
                        pass
                    
                    # Enrich with installation status
                    for model in models:
                        model_name = model.get('name', '')
                        model['installed'] = model_name in installed_models
                        if model['installed'] and model_name in installed_models:
                            model.update(installed_models[model_name])
                    
                    return models
            except requests.exceptions.RequestException:
                pass
                
            # Fallback to using the Ollama CLI if API is not available
            try:
                # Get list of installed models
                installed_models = {}
                result = subprocess.run(
                    ["ollama", "list", "--json"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    installed = json.loads(result.stdout)
                    for model in installed:
                        if 'name' in model:
                            installed_models[model['name']] = model
                
                # Get all available models from the library
                result = subprocess.run(
                    ["ollama", "list", "--all", "--json"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return []
                    
                models = json.loads(result.stdout)
                
                # Mark which models are installed
                for model in models:
                    if 'name' in model and model['name'] in installed_models:
                        model['installed'] = True
                        # Merge with installed model data
                        model.update(installed_models[model['name']])
                    else:
                        model['installed'] = False
                
                return models
                
            except (subprocess.SubprocessError, json.JSONDecodeError):
                pass
                
            return []
            
        except Exception as e:
            print(f"Error fetching models from Ollama: {str(e)}")
            return []
    
    def _load_cached_models(self) -> List[Dict]:
        """Load models from the cache file.
        
        Returns:
            List of model dictionaries, or empty list if cache doesn't exist or is invalid.
        """
        try:
            if not self.cache_file.exists():
                return []
                
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                return data
                
        except (json.JSONDecodeError, IOError, OSError) as e:
            print(f"Warning: Failed to load cached models: {str(e)}")
            return []
    
    def _save_models_to_cache(self, models: List[Dict]) -> bool:
        """Save models to the cache file.
        
        Args:
            models: List of model dictionaries to save.
            
        Returns:
            True if successful, False otherwise.
        """
        if not models or not isinstance(models, list):
            return False
            
        try:
            # Ensure the directory exists
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Write to a temporary file first
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(models, f, indent=2, ensure_ascii=False)
            
            # Rename the temp file to the final name (atomic on POSIX)
            temp_file.replace(self.cache_file)
            return True
            
        except (IOError, OSError, json.JSONEncodeError) as e:
            print(f"Error saving models to cache: {str(e)}")
            # Clean up temp file if it exists
            if 'temp_file' in locals() and temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass
            return False
