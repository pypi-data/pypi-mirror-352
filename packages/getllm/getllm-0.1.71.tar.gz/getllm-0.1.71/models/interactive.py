"""Interactive model search and selection."""
from typing import List, Dict, Optional, Union
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import questionary
import json
from pathlib import Path

console = Console()

def load_ollama_models() -> List[Dict]:
    """Load Ollama models from the latest JSON file."""
    models_dir = Path(__file__).parent.parent / 'ollama_models_data'
    if not models_dir.exists():
        return []
    
    # Find the most recent JSON file
    json_files = list(models_dir.glob('ollama_models_*.json'))
    if not json_files:
        return []
    
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
            return data.get('models', [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def interactive_model_search(query: str = None) -> Optional[str]:
    """
    Interactive model search that allows the user to select a model.
    
    Args:
        query: Optional search query to filter models
        
    Returns:
        The name of the selected model, or None if no model was selected
    """
    try:
        # Load models from Ollama
        ollama_models = load_ollama_models()
        
        # Filter models based on search query
        if query:
            ollama_results = [
                m for m in ollama_models 
                if query.lower() in m.get('name', '').lower() or \
                   query.lower() in m.get('description', '').lower()
            ]
        else:
            ollama_results = ollama_models[:50]  # Limit initial results
        
        if not ollama_results:
            console.print("[yellow]No models found matching your query.[/yellow]")
            return None
            
        # Format choices for the menu
        choices = []
        model_map = {}
        
        # Add Ollama models
        for i, model in enumerate(ollama_results, 1):
            model_id = model['name']
            model_name = model.get('name', 'Unnamed')
            model_desc = model.get('description', 'No description')
            
            # Truncate long descriptions
            if len(model_desc) > 100:
                model_desc = model_desc[:97] + '...'
                
            choices.append(
                questionary.Choice(
                    title=f"[{i}] {model_name} - {model_desc}",
                    value=model_id
                )
            )
            model_map[model_id] = model
        
        # Add exit option
        choices.append(
            questionary.Choice(
                title="[q] Cancel and exit",
                value=None
            )
        )
        
        # Show selection
        selected = questionary.select(
            "Select a model to install:",
            choices=choices,
            use_shortcuts=True,
            style=lambda x: "fg:cyan"
        ).ask()
        
        return selected

    except Exception as e:
        console.print(f"[red]Error during model search: {str(e)}[/red]")
        return None
