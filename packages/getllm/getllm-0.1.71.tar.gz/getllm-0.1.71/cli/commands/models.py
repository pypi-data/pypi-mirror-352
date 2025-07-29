"""Model-related CLI commands."""
from typing import Any, Dict, List, Optional
from pathlib import Path

import click
from rich.console import Console

from ..commands.base import BaseCommand
from ..utils import (
    display_models,
    install_model_with_progress,
    uninstall_model_with_progress,
    display_model_info
)
from getllm.utils.ollama_models import (
    load_ollama_models,
    display_ollama_models,
    search_ollama_models
)
from getllm import ModelManager, get_models

class ListModelsCommand(BaseCommand):
    """Command to list available models."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'list',
            'help': 'List available models',
            'options': [
                {
                    'param_decls': ['--source'],
                    'kwargs': {
                        'type': click.Choice(['all', 'huggingface', 'ollama'], case_sensitive=False),
                        'default': 'all',
                        'help': 'Filter models by source'
                    }
                },
                {
                    'param_decls': ['--installed'],
                    'kwargs': {
                        'is_flag': True,
                        'help': 'Show only installed models'
                    }
                },
                {
                    'param_decls': ['--limit'],
                    'kwargs': {
                        'type': int,
                        'default': None,
                        'help': 'Limit the number of results'
                    }
                },
                {
                    'param_decls': ['--details', '-d'],
                    'kwargs': {
                        'is_flag': True,
                        'help': 'Show detailed information about each model'
                    }
                },
                {
                    'param_decls': ['--search'],
                    'kwargs': {
                        'type': str,
                        'default': None,
                        'help': 'Search for models by name or description'
                    }
                }
            ]
        }
    
    def execute(
        self, 
        source: str, 
        installed: bool, 
        limit: Optional[int],
        details: bool,
        search: Optional[str],
        **kwargs
    ) -> None:
        """Execute the list models command."""
        console = Console()
        
        # Handle Ollama models
        if source in ['all', 'ollama']:
            ollama_models_list = load_ollama_models()
            
            # Apply search if provided
            if search:
                ollama_models_list = search_ollama_models(
                    search, 
                    models=ollama_models_list,
                    case_sensitive=False
                )
            
            if ollama_models_list:
                # Convert Ollama models to a consistent format
                ollama_models_formatted = []
                for m in ollama_models_list:
                    if not isinstance(m, dict):
                        continue
                    model_dict = {
                        'id': f"ollama/{m.get('name', '')}",
                        'name': m.get('name', ''),
                        'description': m.get('description', 'No description'),
                        'source': 'ollama',
                        'sizes': m.get('sizes', []),
                        'type': 'ollama',
                        'installed': False  # Will be updated by display_models
                    }
                    ollama_models_formatted.append(model_dict)
                
                if source == 'ollama':
                    # If only showing Ollama models, use the enhanced display_models
                    display_models(
                        models=ollama_models_formatted,
                        installed_only=installed,
                        source=source,
                        limit=limit,
                        show_sizes=True
                    )
                    return
                else:
                    # If showing all sources, include Ollama models in the general list
                    try:
                        models = list(get_models() or []) + ollama_models_formatted
                    except Exception as e:
                        console.print(f"[yellow]Warning: Could not load other models: {e}[/yellow]")
                        models = ollama_models_formatted
            else:
                models = list(get_models() or [])
        else:
            models = list(get_models() or [])
        
        # Filter by source if not 'all'
        if source != 'all':
            models = [
                m for m in models 
                if str(m.get('source', '')).lower() == source.lower()
            ]
        
        # Apply search if provided
        if search:
            search = search.lower()
            models = [
                m for m in models
                if (search in m.get('id', '').lower() or 
                    search in m.get('name', '').lower() or
                    search in m.get('description', '').lower())
            ]
        
        # Display the filtered models
        display_models(
            models=models,
            installed_only=installed,
            source=source,
            limit=limit,
            show_sizes=(source == 'ollama')
        )


class InstallModelCommand(BaseCommand):
    """Command to install a model."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'install',
            'help': 'Install a model',
            'args': [
                {
                    'name': 'model_id',
                    'type': str,
                    'required': True,
                    'help': 'ID of the model to install (e.g., huggingface/gpt2, ollama/llama2)'
                }
            ],
            'options': [
                {
                    'param_decls': ['--force'],
                    'kwargs': {
                        'is_flag': True,
                        'help': 'Force reinstall if already installed'
                    }
                }
            ]
        }
    
    def execute(self, model_id: str, force: bool, **kwargs) -> None:
        """Execute the install model command."""
        success = install_model_with_progress(model_id, force=force)
        
        if success:
            console = Console()
            console.print(f"[green]✓ Successfully installed {model_id}[/green]")


class UninstallModelCommand(BaseCommand):
    """Command to uninstall a model."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'uninstall',
            'help': 'Uninstall a model',
            'args': [
                {
                    'name': 'model_id',
                    'type': str,
                    'required': True,
                    'help': 'ID of the model to uninstall'
                }
            ]
        }
    
    def execute(self, model_id: str, **kwargs) -> None:
        """Execute the uninstall model command."""
        success = uninstall_model_with_progress(model_id)
        
        if success:
            console = Console()
            console.print(f"[green]✓ Successfully uninstalled {model_id}[/green]")


class InfoModelCommand(BaseCommand):
    """Command to show detailed information about a model."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'info',
            'help': 'Show detailed information about a model',
            'args': [
                {
                    'name': 'model_id',
                    'type': str,
                    'required': True,
                    'help': 'ID of the model to show information for'
                }
            ]
        }
    
    def execute(self, model_id: str, **kwargs) -> None:
        """Execute the model info command."""
        display_model_info(model_id)


def register_commands(cli_group: click.Group) -> None:
    """Register model-related commands with the CLI group."""
    # Create a model command group
    model_group = click.Group('model', help='Manage models')
    
    # Register all model commands
    commands = [
        ListModelsCommand,
        InstallModelCommand,
        UninstallModelCommand,
        InfoModelCommand,
    ]
    
    for cmd_class in commands:
        cmd = cmd_class.create_click_command()
        model_group.add_command(cmd)
    
    # Add the model group to the main CLI
    cli_group.add_command(model_group)
