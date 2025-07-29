"""Utility functions for model-related operations in the CLI."""
from typing import Dict, List, Optional, Any, Union
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    from getllm import ModelManager, ModelInfo
    MODEL_INFO_AVAILABLE = True
except ImportError:
    from getllm import ModelManager
    MODEL_INFO_AVAILABLE = False
    ModelInfo = Any  # Type hint fallback

console = Console()

def display_models(
    models: List[Union[dict, Any]],
    installed_only: bool = False,
    source: Optional[str] = None,
    limit: Optional[int] = None,
    show_sizes: bool = False
) -> None:
    """Display a list of models in a formatted table.
    
    Args:
        models: List of model objects or dictionaries to display
        installed_only: If True, only show installed models
        source: Filter models by source (e.g., 'huggingface', 'ollama')
        limit: Maximum number of models to display
        show_sizes: Whether to show model sizes in the output
    """
    if not models:
        console.print("[yellow]No models found.[/yellow]")
        return
    
    # Initialize model manager
    try:
        manager = ModelManager()
    except Exception as e:
        console.print(f"[yellow]Warning: Could not initialize ModelManager: {e}[/yellow]")
        manager = None
    
    # Process models
    filtered_models = []
    
    for model in models:
        model_dict = {}
        
        try:
            # Handle dictionaries
            if isinstance(model, dict):
                model_dict = {
                    'id': str(model.get('id', '')),
                    'name': str(model.get('name', '')),
                    'description': str(model.get('description', '')),
                    'source': str(model.get('source', 'unknown')),
                    'type': str(model.get('type', model.get('model_type', 'N/A'))),
                    'installed': manager.is_model_installed(model.get('id', '')) if manager else False,
                    'sizes': model.get('sizes', [])
                }
            # Handle ModelInfo objects if available
            elif MODEL_INFO_AVAILABLE and isinstance(model, ModelInfo):
                model_id = getattr(model, 'id', '')
                model_source = model.source.value if hasattr(model, 'source') and hasattr(model.source, 'value') else 'unknown'
                model_dict = {
                    'id': model_id,
                    'name': getattr(model, 'name', ''),
                    'description': getattr(model, 'description', ''),
                    'source': model_source,
                    'type': model.model_type.value if hasattr(model, 'model_type') and model.model_type else 'N/A',
                    'installed': manager.is_model_installed(model_id) if manager else False,
                    'sizes': getattr(model, 'sizes', [])
                }
            # Fallback for other object types
            elif hasattr(model, '__dict__'):
                model_dict = {
                    'id': str(getattr(model, 'id', '')),
                    'name': str(getattr(model, 'name', '')),
                    'description': str(getattr(model, 'description', '')),
                    'source': str(getattr(model, 'source', 'unknown')),
                    'type': str(getattr(model, 'type', getattr(model, 'model_type', 'N/A'))),
                    'installed': manager.is_model_installed(getattr(model, 'id', '')) if manager else False,
                    'sizes': getattr(model, 'sizes', [])
                }
            else:
                console.print(f"[yellow]Warning: Unknown model format: {type(model)}[/yellow]")
                continue
                
        except Exception as e:
            console.print(f"[yellow]Warning: Error processing model {model}: {e}[/yellow]")
            continue
            
        # Skip if we couldn't create a valid model dict
        if not model_dict.get('id') and not model_dict.get('name'):
            continue
        
        # Apply filters
        if installed_only and not model_dict['installed']:
            continue
            
        if source and model_dict['source'].lower() != source.lower():
            continue
            
        filtered_models.append(model_dict)
    
    # Apply limit
    if limit is not None:
        filtered_models = filtered_models[:limit]
    
    if not filtered_models:
        console.print("[yellow]No models found matching the criteria.[/yellow]")
        return
    
    # Create and display table
    table = Table(title="Available Models")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Source", style="magenta")
    
    if show_sizes:
        table.add_column("Sizes", style="yellow")
    
    table.add_column("Type", style="yellow")
    table.add_column("Installed", style="green")
    
    for model in filtered_models:
        row = [
            model['id'],
            model['name'],
            model['source'],
        ]
        
        if show_sizes:
            sizes = model.get('sizes', [])
            row.append(", ".join(sizes) if sizes else "N/A")
        
        row.extend([
            model['type'],
            "✓" if model['installed'] else "✗"
        ])
        
        table.add_row(*row)
    
    console.print(table)


def install_model_with_progress(
    model_id: str,
    force: bool = False,
    **kwargs
) -> bool:
    """Install a model with a progress indicator.
    
    Args:
        model_id: ID of the model to install
        force: Whether to force reinstallation if already installed
        **kwargs: Additional arguments to pass to install_model
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    manager = ModelManager()
    
    if not force and manager.is_model_installed(model_id):
        console.print(f"[yellow]Model {model_id} is already installed. Use --force to reinstall.[/yellow]")
        return False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"[cyan]Installing {model_id}...", total=None)
        
        try:
            success = manager.install_model(model_id, force=force, **kwargs)
            if success:
                progress.update(task, description=f"[green]✓ Installed {model_id}[/green]")
                return True
            else:
                progress.update(task, description=f"[red]Failed to install {model_id}[/red]")
                return False
        except Exception as e:
            progress.update(task, description=f"[red]Error installing {model_id}: {str(e)}[/red]")
            return False


def uninstall_model_with_progress(model_id: str) -> bool:
    """Uninstall a model with a progress indicator.
    
    Args:
        model_id: ID of the model to uninstall
        
    Returns:
        bool: True if uninstallation was successful, False otherwise
    """
    manager = ModelManager()
    
    if not manager.is_model_installed(model_id):
        console.print(f"[yellow]Model {model_id} is not installed.[/yellow]")
        return False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"[cyan]Uninstalling {model_id}...", total=None)
        
        try:
            success = manager.uninstall_model(model_id)
            if success:
                progress.update(task, description=f"[green]✓ Uninstalled {model_id}[/green]")
                return True
            else:
                progress.update(task, description=f"[red]Failed to uninstall {model_id}[/red]")
                return False
        except Exception as e:
            progress.update(task, description=f"[red]Error uninstalling {model_id}: {str(e)}[/red]")
            return False


def display_model_info(model_id: str) -> None:
    """Display detailed information about a model.
    
    Args:
        model_id: ID of the model to display information for
    """
    manager = ModelManager()
    
    try:
        model_info = manager.get_model_info(model_id)
        if not model_info:
            console.print(f"[red]Model not found: {model_id}[/red]")
            return
        
        console.print(f"[bold cyan]Model:[/bold cyan] {model_info.id}")
        console.print(f"[bold]Name:[/bold] {model_info.name}")
        console.print(f"[bold]Source:[/bold] {model_info.source.value}")
        console.print(f"[bold]Type:[/bold] {model_info.model_type.value if model_info.model_type else 'N/A'}")
        console.print(f"[bold]Installed:[/bold] {'✓' if manager.is_model_installed(model_id) else '✗'}")
        
        if model_info.description:
            console.print("\n[bold]Description:[/bold]")
            console.print(model_info.description)
            
        if model_info.tags:
            console.print("\n[bold]Tags:[/bold]", ", ".join(f"[yellow]{tag}[/yellow]" for tag in model_info.tags))
            
        if model_info.metadata:
            console.print("\n[bold]Metadata:[/bold]")
            for key, value in model_info.metadata.items():
                console.print(f"  [cyan]{key}:[/cyan] {value}")
                
    except Exception as e:
        console.print(f"[red]Error getting model info: {str(e)}[/red]")
        return
