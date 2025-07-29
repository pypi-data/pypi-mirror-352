"""Utility functions for reading Ollama model data."""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from rich.console import Console
from rich.table import Table

# Directory containing Ollama models data
OLLAMA_MODELS_DIR = Path(__file__).parent.parent / "ollama_models_data"

def get_latest_models_file() -> Optional[Path]:
    """Get the most recent Ollama models JSON file.
    
    Returns:
        Path to the latest models file, or None if no files found
    """
    if not OLLAMA_MODELS_DIR.exists():
        return None
        
    # Find all JSON files matching the pattern
    model_files = list(OLLAMA_MODELS_DIR.glob("ollama_models_*.json"))
    if not model_files:
        return None
        
    # Sort by modification time (newest first)
    return max(model_files, key=os.path.getmtime)

def load_ollama_models(file_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load Ollama models from a JSON file.
    
    Args:
        file_path: Path to the JSON file. If None, loads the latest file.
        
    Returns:
        List of model dictionaries
    """
    if file_path is None:
        file_path = get_latest_models_file()
        if file_path is None:
            return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('models', [])
    except (json.JSONDecodeError, FileNotFoundError) as e:
        console = Console()
        console.print(f"[red]Error loading models from {file_path}: {e}[/red]")
        return []

def display_ollama_models(
    models: List[Dict[str, Any]],
    limit: Optional[int] = None,
    show_details: bool = False
) -> None:
    """Display Ollama models in a formatted table.
    
    Args:
        models: List of model dictionaries
        limit: Maximum number of models to display
        show_details: Whether to show detailed information
    """
    console = Console()
    
    if not models:
        console.print("[yellow]No models found.[/yellow]")
        return
    
    if limit is not None:
        models = models[:limit]
    
    if show_details:
        table = Table(title="Ollama Models (Detailed)", show_lines=True)
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Sizes", style="magenta")
        table.add_column("Metadata", style="yellow")
        
        for model in models:
            sizes = ", ".join(model.get('sizes', []))
            metadata = model.get('metadata', {})
            metadata_str = "\n".join(f"{k}: {v}" for k, v in metadata.items())
            
            table.add_row(
                model.get('name', 'N/A'),
                model.get('description', ''),
                sizes or 'N/A',
                metadata_str or 'N/A'
            )
    else:
        table = Table(title="Available Ollama Models")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Sizes", style="magenta")
        
        for model in models:
            sizes = ", ".join(model.get('sizes', []))
            table.add_row(
                model.get('name', 'N/A'),
                model.get('description', '')[:100] + ('...' if len(model.get('description', '')) > 100 else ''),
                sizes or 'N/A'
            )
    
    console.print(table)

def search_ollama_models(
    query: str,
    models: Optional[List[Dict[str, Any]]] = None,
    case_sensitive: bool = False
) -> List[Dict[str, Any]]:
    """Search for models by name or description.
    
    Args:
        query: Search term
        models: List of models to search. If None, loads the latest models.
        case_sensitive: Whether the search should be case sensitive
        
    Returns:
        List of matching models
    """
    if models is None:
        models = load_ollama_models()
    
    if not case_sensitive:
        query = query.lower()
    
    results = []
    for model in models:
        name = model.get('name', '')
        description = model.get('description', '')
        
        if not case_sensitive:
            name = name.lower()
            description = description.lower()
        
        if query in name or query in description:
            results.append(model)
    
    return results
