"""
Interactive model search and selection functionality.
"""
import logging
from typing import Optional, List, Dict, Any

import questionary
from rich.console import Console
from rich.table import Table

# Get logger
logger = logging.getLogger('getllm.models.interactive')

def interactive_model_search(query: str = None, check_ollama: bool = True) -> Optional[str]:
    """
    Interactive model search that allows the user to select a model.
    
    Args:
        query: Optional search query to filter models
        check_ollama: Whether to check if the selected model is installed in Ollama
        
    Returns:
        The name of the selected model, or None if no model was selected
    """
    from . import (
        search_huggingface_models,
        get_huggingface_models,
        update_models_from_huggingface,
        list_installed_models,
        get_default_model
    )
    
    console = Console()
    
    try:
        # Update models from Hugging Face
        console.print("\n[bold]Updating model list from Hugging Face...[/]")
        update_models_from_huggingface(query=query)
        
        # Get available models
        if query:
            models = search_huggingface_models(query=query)
        else:
            models = get_huggingface_models()
        
        if not models:
            console.print("[yellow]No models found matching your query.[/]")
            return None
            
        # Get installed models for reference
        installed_models = {m['name'] for m in list_installed_models()}
        
        # Create a table to display the models
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name")
        table.add_column("Size")
        table.add_column("Description")
        table.add_column("Status")
        
        # Add models to the table
        for i, model in enumerate(models, 1):
            model_name = model.get('name', model.get('id', 'unknown'))
            status = "[green]✓ Installed[/]" if model_name in installed_models else "[yellow]Not Installed[/]"
            table.add_row(
                str(i),
                model_name,
                model.get('size', 'N/A'),
                model.get('description', 'No description available')[:60] + '...',
                status
            )
        
        # Display the table
        console.print("\n[bold]Available Models:[/]")
        console.print(table)
        
        # Let the user select a model
        choices = [str(i) for i in range(1, len(models) + 1)]
        choice = questionary.select(
            "Select a model (or press Ctrl+C to cancel):",
            choices=choices,
            style=lambda x: 'fg:green' if models[int(x)-1]['name'] in installed_models else ''
        ).ask()
        
        if choice:
            selected_model = models[int(choice) - 1]
            model_name = selected_model.get('name', selected_model.get('id'))
            return model_name
            
    except KeyboardInterrupt:
        console.print("\nOperation cancelled by user.")
    except Exception as e:
        logger.error(f"Error during interactive model search: {e}", exc_info=True)
        console.print(f"[red]Error: {str(e)}[/]")
    
    return None
