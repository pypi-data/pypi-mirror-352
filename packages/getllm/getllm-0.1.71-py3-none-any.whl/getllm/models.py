"""
Model management for PyLLM.

This module provides a high-level interface for managing LLM models,
including installation, listing, and updating models from various sources.
It uses a modular structure with separate modules for different functionalities.
"""

# Re-export everything from the models package
from getllm.models import *

# For backward compatibility
try:
    from getllm.models.manager import ModelManager
    from getllm.models.constants import DEFAULT_MODELS, DEFAULT_HF_MODELS
    from getllm.models.utils import (
        get_models_dir,
        get_default_model,
        set_default_model,
        get_models,
        install_model,
        list_installed_models,
        update_models_metadata,
        get_model_metadata,
        load_huggingface_models_from_cache,
        load_ollama_models_from_cache
    )
    from getllm.models.huggingface import (
        search_huggingface_models,
        interactive_model_search,
        update_models_from_huggingface,
        update_huggingface_models_cache
    )
    from getllm.models.ollama import (
        update_models_from_ollama,
        update_ollama_models_cache,
        list_ollama_models,
        install_ollama_model
    )
    
    # Initialize the default model manager
    model_manager = ModelManager()
    
except ImportError as e:
    import logging
    logging.error(f"Error importing models package: {e}")
    logging.error("Please make sure the package is properly installed.")
    
    # Define empty defaults to prevent import errors
    class ModelManager:
        pass
    
    DEFAULT_MODELS = []
    DEFAULT_HF_MODELS = []
    model_manager = None

# For backward compatibility with existing code
__all__ = [
    'ModelManager',
    'DEFAULT_MODELS',
    'DEFAULT_HF_MODELS',
    'get_models_dir',
    'get_default_model',
    'set_default_model',
    'get_models',
    'install_model',
    'list_installed_models',
    'update_models_metadata',
    'get_model_metadata',
    'search_huggingface_models',
    'interactive_model_search',
    'update_models_from_huggingface',
    'update_huggingface_models_cache',
    'update_models_from_ollama',
    'update_ollama_models_cache',
    'list_ollama_models',
    'install_ollama_model',
    'load_huggingface_models_from_cache',
    'load_ollama_models_from_cache',
    'model_manager'
]
        file_path = os.path.join(models_dir, MODELS_JSON)
    
    # Use Path.exists() instead of os.path.exists() for test compatibility
    if Path(file_path).exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                models = json.load(f)
                return models
        except Exception as e:
            print(f"Error loading JSON: {e}")
    
    return DEFAULT_MODELS

def update_models_metadata():
    """
    Create and update a combined models metadata file that contains information
    about both Hugging Face and Ollama models.
    
    This function loads models from both Hugging Face and Ollama caches and
    combines them into a single metadata file for easier access.
    
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15'
            },
            {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
            }
        ]
        
        # Try different URLs and User-Agents
        urls = [
            "https://huggingface.co/models?sort=downloads&filter=gguf",
            "https://huggingface.co/models?filter=gguf&sort=downloads",
            "https://huggingface.co/models?filter=gguf"
        ]
        
        response = None
        success = False
        
        # Try each combination of URL and header until one works
        for url in urls:
            for headers in headers_options:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    success = True
                    break
                except Exception as e:
                    print(f"Attempt failed with {url}: {e}")
                    continue
            if success:
                break
        
        # If all attempts failed, raise an exception
        if not success or not response:
            raise Exception("All attempts to fetch models from Hugging Face failed")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all model cards
        model_cards = soup.select('article.overview-card')
        
        results = []
        for card in model_cards[:50]:  # Get top 50 models
            # Extract model ID (username/model_name)
            model_id_elem = card.select_one('a.header-link')
            if not model_id_elem:
                continue
            
            model_id = model_id_elem.text.strip()
            
            # Extract description
            desc_elem = card.select_one('p.description')
            description = desc_elem.text.strip() if desc_elem else ""
            
            # Extract downloads count
            downloads_elem = card.select_one('div.flex.flex-col span.whitespace-nowrap')
            downloads = downloads_elem.text.strip() if downloads_elem else ""
            
            # Extract last updated time
            updated_elem = card.select_one('div.metadata time')
            updated = updated_elem.text.strip() if updated_elem else ""
            
            # Extract model URL
            model_url = None
            if model_id_elem and 'href' in model_id_elem.attrs:
                href = model_id_elem['href']
                if href.startswith('/'):
                    model_url = f"https://huggingface.co{href}"
                elif href.startswith('http'):
                    model_url = href
            
            # Extract size from description if available
            size = "Unknown"
            size_match = re.search(r'\b(\d+(\.\d+)?[BM])\b', description)
            if size_match:
                size = size_match.group(1)
            
            # Create metadata dictionary
            metadata = {
                'description': description,
                'downloads': downloads,
                'updated': updated,
                'url': model_url,
                'size': size,
                'source': 'huggingface'
            }
            
            # Create the model entry
            model_entry = {
                'id': model_id,
                'name': model_id,  # Use id as name for consistency
                'description': description,
                'downloads': downloads,
                'updated': updated,
                'url': model_url,
                'size': size,
                'source': 'huggingface',
                'metadata': metadata
            }
            
            results.append(model_entry)
        
        # Always ensure Bielik models are included
        # First, get all Bielik models from DEFAULT_HF_MODELS
        bielik_models = [m for m in DEFAULT_HF_MODELS if 'bielik' in m['id'].lower()]
        
        # Then check if they're already in the results
        existing_ids = [m['id'] for m in results]
        for bielik_model in bielik_models:
            if bielik_model['id'] not in existing_ids:
                # Add metadata if not present
                if 'metadata' not in bielik_model:
                    bielik_model['metadata'] = {
                        'description': bielik_model.get('description', ''),
                        'downloads': bielik_model.get('downloads', ''),
                        'updated': bielik_model.get('updated', ''),
                        'url': f"https://huggingface.co/{bielik_model['id']}",
                        'size': bielik_model.get('size', 'Unknown'),
                        'source': 'huggingface'
                    }
                # Add name if not present
                if 'name' not in bielik_model:
                    bielik_model['name'] = bielik_model['id']
                
                results.append(bielik_model)
                existing_ids.append(bielik_model['id'])
        
        # If we didn't find any models, use the default list
        if not results:
            # Ensure all DEFAULT_HF_MODELS have metadata
            for model in DEFAULT_HF_MODELS:
                if 'metadata' not in model:
                    model['metadata'] = {
                        'description': model.get('description', ''),
                        'downloads': model.get('downloads', ''),
                        'updated': model.get('updated', ''),
                        'url': f"https://huggingface.co/{model['id']}",
                        'size': model.get('size', 'Unknown'),
                        'source': 'huggingface'
                    }
                if 'name' not in model:
                    model['name'] = model['id']
            
            results = DEFAULT_HF_MODELS
        
        # Save to cache file
        cache_path = get_hf_models_cache_path()
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"Successfully updated HF models cache with {len(results)} models.")
            return True
        except Exception as e:
            print(f"Error saving HF models cache: {e}")
            return False
    
    except Exception as e:
        print(f"Error updating HF models cache: {e}")
        # If there was an error, ensure we at least have the default models in the cache
        try:
            cache_path = get_hf_models_cache_path()
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            # Ensure all DEFAULT_HF_MODELS have metadata
            for model in DEFAULT_HF_MODELS:
                if 'metadata' not in model:
                    model['metadata'] = {
                        'description': model.get('description', ''),
                        'downloads': model.get('downloads', ''),
                        'updated': model.get('updated', ''),
                        'url': f"https://huggingface.co/{model['id']}",
                        'size': model.get('size', 'Unknown'),
                        'source': 'huggingface'
                    }
                if 'name' not in model:
                    model['name'] = model['id']
            
            with open(cache_path, 'w') as f:
                json.dump(DEFAULT_HF_MODELS, f, indent=2)
            print("Created default HF models cache.")
            return False
        except Exception as inner_e:
            print(f"Error creating default HF models cache: {inner_e}")
            return False

def interactive_model_search(query=None, check_ollama=True):
    """
    Search for models on Hugging Face and allow the user to interactively select one to install.
    
    Args:
        query: The search query (e.g., "bielik"). If None, prompts the user for a query.
        check_ollama: Whether to check if Ollama is installed before proceeding.
        
    Returns:
        The selected model ID or None if cancelled.
    """
    try:
        import questionary
        
        # Check if Ollama is installed if requested
        if check_ollama:
            from getllm.ollama import OllamaServer
            ollama = OllamaServer()
            
            # Check if we're already in mock mode (set by previous installation choice)
            if os.environ.get('GETLLM_MOCK_MODE') == 'true':
                print("\nRunning in mock mode - Ollama checks bypassed")
                # Continue with model search in mock mode
            elif not ollama.is_ollama_installed:
                print("\nOllama is not installed but required for model installation.")
                
                # Use the enhanced installation options
                if ollama._install_ollama():
                    print("\n✅ Ollama installed successfully! Continuing with model search...")
                elif os.environ.get('GETLLM_MOCK_MODE') == 'true':
                    # User chose mock mode in the installation menu
                    print("\nContinuing with model search in mock mode...")
                else:
                    # User cancelled or installation failed
                    print("\nIf you want to continue without Ollama, use the --mock flag:")
                    print("  getllm --mock --search <query>")
                    return None
        
        # If no query provided, ask the user
        if query is None:
            query = questionary.text("Enter a search term for Hugging Face models:").ask()
            if not query:
                print("Search cancelled.")
                return None
        
        print(f"Searching for models matching '{query}' on Hugging Face...")
        
        # First try to update the cache, but don't fail if it doesn't work
        try:
            update_huggingface_models_cache()
        except Exception as e:
            print(f"Warning: Could not update Hugging Face models cache: {e}")
            print("Using cached or default models instead.")
        
        # Search for models with our enhanced search function
        models_list = search_huggingface_models(query)
        
        if not models_list:
            print(f"No models found matching '{query}'.")
            return None
        
        # Create choices for the questionary select
        choices = []
        for m in models_list:
            # Handle different model formats (from cache vs. direct search)
            model_id = m.get('id', m.get('name', ''))
            model_size = m.get('size', 'Unknown')
            model_desc = m.get('description', m.get('desc', ''))
            model_downloads = m.get('downloads', 'N/A')
            
            # Format the display title
            if isinstance(model_downloads, (int, float)):
                title = f"{model_id:<50} {model_size:<10} Downloads: {model_downloads:,} | {model_desc}"
            else:
                title = f"{model_id:<50} {model_size:<10} {model_desc}"
            
            choices.append(questionary.Choice(title=title, value=model_id))
        
        if not choices:
            print(f"No models found matching '{query}'.")
            return None
        
        # Add a cancel option
        choices.append(questionary.Choice(title="Cancel", value="__CANCEL__"))
        
        # Ask the user to select a model
        selected = questionary.select(
            "Select a model to install:",
            choices=choices
        ).ask()
        
        # If user selected Cancel, return early
        if selected == "__CANCEL__":
            print("Selection cancelled.")
            return None
        
        return selected
    except Exception as e:
        print(f"Error in interactive model search: {e}")
        return None

def update_models_from_huggingface(query=None, interactive=True):
    """
    Update the local models.json file with models from Hugging Face.
    First updates the HF models cache, then allows selection of models to add to the local models list.
    
    Args:
        query: The search query (e.g., "bielik"). If None and interactive is True, prompts the user.
        interactive: Whether to allow interactive selection of models.
        
    Returns:
        The updated list of models.
    """
    # First update the HF models cache
    print("Updating Hugging Face models cache...")
    success = update_huggingface_models_cache()
    if not success:
        print("Warning: Using fallback models list due to update failure.")
    
    # Check if questionary is available for interactive mode
    if interactive:
        try:
            import questionary
        except ImportError:
            print("questionary package is required for interactive mode.")
            print("Install it with: pip install questionary")
            interactive = False
    
    # Get all HF models from cache or default list
    all_hf_models = get_huggingface_models()
    
    # If query is provided, filter models
    if query:
        print(f"Filtering models matching '{query}'...")
        query = query.lower()
        filtered_models = [
            model for model in all_hf_models 
            if query in model['id'].lower() or 
               query in model.get('description', '').lower()
        ]
        models_data = filtered_models
    else:
        models_data = all_hf_models
    
    if not models_data:
        print(f"No models found matching '{query if query else 'criteria'}'.")
        return get_models()
    
    # If interactive mode, allow selection of models to add
    if interactive:
        # If no query and interactive mode, prompt for filtering
        if query is None:
            filter_query = questionary.text("Enter filter term for Hugging Face models (or leave empty for all):").ask()
            if filter_query:
                filter_query = filter_query.lower()
                models_data = [
                    model for model in models_data 
                    if filter_query in model['id'].lower() or 
                       filter_query in model.get('description', '').lower()
                ]
                if not models_data:
                    print(f"No models found matching '{filter_query}'.")
                    return get_models()
        
        choices = []
        for model in models_data:
            model_id = model.get('id', '')
            desc = model.get('description', '')[:50] + ('...' if len(model.get('description', '')) > 50 else '')
            downloads = model.get('downloads', '')
            
            choices.append(
                questionary.Choice(
                    title=f"{model_id} - {desc} ({downloads})",
                    value=model
                )
            )
        
        if not choices:
            print("No models found to add.")
            return get_models()
        
        print("\nSelect models to add to your local models list:")
        selected_models = questionary.checkbox(
            "Select models:",
            choices=choices
        ).ask()
        
        if not selected_models:
            print("No models selected.")
            return get_models()
        
        models_data = selected_models
    
    # Load existing models
    existing_models = load_models_from_json()
    existing_model_names = {m['name'] for m in existing_models}
    
    # Add new models
    new_models = []
    for model in models_data:
        model_id = model.get('id', '')
        if model_id and model_id not in existing_model_names:
            # Extract size from description if available
            size = "Unknown"
            desc = model.get('description', '')
            size_match = re.search(r'\b(\d+(\.\d+)?[BM])\b', desc)
            if size_match:
                size = size_match.group(1)
            
            new_model = {
                'name': model_id,
                'size': size,
                'desc': desc[:100] + ('...' if len(desc) > 100 else ''),
                'source': 'huggingface'
            }
            
            new_models.append(new_model)
            existing_model_names.add(model_id)  # Add to set to avoid duplicates
    
    if new_models:
        # Add new models to existing models
        existing_models.extend(new_models)
        
        # Save updated models list
        save_models_to_json(existing_models)
        
        print(f"Added {len(new_models)} new models to the local models list.")
        
        # Print the new models
        print("\nNew models added:")
        for model in new_models:
            print(f"  {model['name']:<40} {model['size']:<6} {model['desc']}")
    else:
        print("No new models added. All selected models already exist in the local list.")

    return existing_models

def update_models_from_ollama(save_to_cache=True, limit=50):
    """
    Fetch the latest coding-related models up to 7B from the Ollama library web page
    and update the local models.json file.

    Args:
        save_to_cache: Whether to save the models to the ollama_models.json cache file.
        limit: Maximum number of models to fetch

    Returns:
        The list of models from Ollama.
    """
    # Try to use the model_scrapers module first
    try:
        from .model_scrapers import scrape_ollama_models, are_scrapers_available
        if are_scrapers_available():
            print("Using model scrapers to fetch Ollama models")
            models = scrape_ollama_models(limit=limit)
            if models:
                return models
    except ImportError:
        print("Model scrapers not available, using fallback method")
        # Continue with the fallback method below
    import requests
    import re
    from bs4 import BeautifulSoup
    import json

    MODELS_HTML_URL = "https://ollama.com/library"
    try:
        # Fetch the Ollama library page
        response = requests.get("https://ollama.com/library")
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all model cards
        model_cards = soup.find_all('div', class_=re.compile('card'))

        # Extract model information
        models = []
        for card in model_cards:
            try:
                # Extract the model name
                name_elem = card.find('h3') or card.find('h2')
                if not name_elem:
                    continue

                # Get the full name with tag
                model_name = name_elem.text.strip()

                # Extract the description
                desc_elem = card.find('p')
                description = desc_elem.text.strip() if desc_elem else ""

                # Extract the model size if available
                size_match = re.search(r'\b(\d+(\.\d+)?[BM])\b', description)
                size = size_match.group(1) if size_match else "Unknown"

                # Try to extract the model URL
                model_url = None
                link_elem = card.find('a')
                if link_elem and 'href' in link_elem.attrs:
                    href = link_elem['href']
                    if href.startswith('/'):
                        model_url = f"https://ollama.com{href}"
                    elif href.startswith('http'):
                        model_url = href

                # Extract metadata
                metadata = {
                    'size_b': size,
                    'description': description,
                    'url': model_url,
                    'source': 'ollama'
                }

                # Check if this is a coding-related model
                is_coding = any(keyword in description.lower() for keyword in ['code', 'program', 'develop', 'python', 'javascript', 'java', 'c++', 'typescript'])

                # Check if this is a small enough model (up to 7B)
                is_small = True  # Default to True
                if size.endswith('B'):
                    try:
                        size_value = float(size[:-1])
                        is_small = size_value <= 7.0
                    except ValueError:
                        pass  # If we can't parse the size, assume it's small enough

                # Only add coding-related models up to 7B
                if is_small and (is_coding or 'code' in model_name.lower()):
                    models.append({
                        'name': model_name,
                        'size': size,
                        'desc': description,
                        'url': model_url,
                        'source': 'ollama',
                        'metadata': metadata
                    })
            except Exception as e:
                print(f"Error processing model card: {e}")
                continue

        # Save to ollama_models.json cache file if requested
        if save_to_cache and models:
            try:
                cache_path = get_ollama_models_cache_path()
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, 'w') as f:
                    json.dump(models, f, indent=2)
                print(f"Saved {len(models)} Ollama models to cache file.")
            except Exception as e:
                print(f"Error saving Ollama models to cache: {e}")

        # If we found models, also update the models.json file
        if models:
            # Load existing models
            existing_models = load_models_from_json()

            # Create a set of existing model names for quick lookup
            existing_model_names = {m['name'] for m in existing_models}

            # Add new models that don't already exist
            for model in models:
                if model['name'] not in existing_model_names:
                    # Create a simplified version for models.json
                    simple_model = {
                        'name': model['name'],
                        'size': model['size'],
                        'desc': model['desc'],
                        'source': 'ollama'
                    }
                    existing_models.append(simple_model)
                    existing_model_names.add(model['name'])

            # Save the updated models list
            save_models_to_json(existing_models)

            print(f"Updated models list with {len(models)} models from Ollama library.")
            return models
        else:
            print("No models found on Ollama library page.")
            return load_ollama_models_from_cache() or []

        # Save the updated models to the JSON file
        save_models_to_json(models)
        
        print(f"Updated models.json with {len(models)} models from Ollama library")
        return models
    except Exception as e:
        print(f"Error updating models from Ollama: {e}")
        return load_ollama_models_from_cache() or DEFAULT_MODELS


def load_ollama_models_from_cache():
    """
    Load Ollama models from the cache file.
    
    Returns:
        A list of Ollama models, or an empty list if the cache file doesn't exist or is invalid.
    """
    try:
        cache_path = get_ollama_models_cache_path()
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading Ollama models from cache: {e}")
        return []


class ModelManager:
    """
    Class for managing LLM models in the PyLLM system.
    Provides methods for listing, installing, and using models.
    
    This class uses the centralized environment system to access model information
    and configuration that is shared across all PyLama components.
    """
    
    def __init__(self):
        # Use the centralized environment to get the default model
        self.default_model = get_default_model() or "llama3"
        self.models = self.get_available_models()
    
    def get_available_models(self):
        """
        Get a list of available models from the models.json file or default list.
        """
        return get_models()
    
    def list_models(self):
        """
        Return a list of available models.
        """
        return self.models
    
    def get_model_info(self, model_name):
        """
        Get information about a specific model.
        """
        for model in self.models:
            if model.get("name") == model_name:
                return model
        return None
    
    def install_model(self, model_name):
        """
        Install a model using Ollama.
        
        Args:
            model_name: The name of the model to install.
            
        Returns:
            True if installation was successful, False otherwise.
        """
        try:
            # Use the OllamaServer module to install the model
            return install_ollama_model(model_name)
        except Exception as e:
            print(f"Error installing model: {e}")
            return False
    
    def list_installed_models(self):
        """
        List models that are currently installed.
        
        Returns:
            A list of installed model names.
        """
        # Use the OllamaServer module to list installed models
        ollama = get_ollama_integration()
        try:
            # Start the Ollama server if it's not already running
            ollama.start_ollama()
            
            # Get the list of installed models
            models = ollama.list_installed_models()
            return [model['name'] for model in models]
        except Exception as e:
            print(f"Error listing installed models: {e}")
            return []
    
    def set_default_model(self, model_name):
        """
        Set the default model to use.
        """
        set_default_model(model_name)
        self.default_model = model_name
        return True
    
    def get_default_model_name(self):
        """
        Get the name of the current default model.
        """
        return self.default_model
    
    def update_models_from_remote(self, source="ollama", query=None, interactive=True):
        """
        Update the models list from a remote source.
        
        Args:
            source: The source to update from ("ollama" or "huggingface").
            query: The search query for Hugging Face models.
            interactive: Whether to allow interactive selection for Hugging Face models.
            
        Returns:
            The updated list of models.
        """
        try:
            if source.lower() == "huggingface":
                models = update_models_from_huggingface(query, interactive)
            else:
                models = update_models_from_ollama()
                
            self.models = models
            return models
        except Exception as e:
            print(f"Error updating models from {source}: {e}")
            return self.models
            
    def search_huggingface_models(self, query=None, limit=20):
        """
        Search for models on Hugging Face.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of model dictionaries.
        """
        return search_huggingface_models(query, limit)
        
    def interactive_model_search(self, query=None):
        """
        Interactive search for models on Hugging Face.
        
        Args:
            query: The search query.
            
        Returns:
            The selected model ID or None if cancelled.
        """
        return interactive_model_search(query)

if __name__ == "__main__":
    default_model = get_default_model()
    print("Available models:")
    models = get_models()
    for idx, m in enumerate(models, 1):
        print(f"{idx}. {m['name']} ({m.get('desc', '')})")
    if default_model:
        print(f"\nCurrent default model: {default_model}\n")
    else:
        print("\nNo default model set in .env\n")
    print("\nSaving list to models.json...")
    save_models_to_json(models)
    print("\nZainstalowane modele:")
    list_installed_models()
    print("\n--- Model Installation ---")
    print("Enter the model number to download, 'u' to update the model list from the Ollama project, or 'q' to exit.")
    while True:
        wyb = input("Choose model (number/'u'/'q'): ").strip()
        if wyb.lower() == 'q':
            print("Done.")
            break
        if wyb.lower() == 'u':
            update_models_from_ollama()
            models = get_models()
            for idx, m in enumerate(models, 1):
                print(f"{idx}. {m['name']} ({m.get('desc', '')})")
            continue
        if wyb.isdigit() and 1 <= int(wyb) <= len(models):
            model_name = models[int(wyb) - 1]["name"]
            # Check if the model is installed
            installed = False
            try:
                output = subprocess.check_output(["ollama", "list"]).decode()
                installed = any(model_name in line for line in output.strip().split("\n")[1:])
            except Exception:
                pass
            if not installed:
                ok = install_model(model_name)
                if not ok:
                    continue
            set_default_model(model_name)
        else:
            print("Invalid choice.")
