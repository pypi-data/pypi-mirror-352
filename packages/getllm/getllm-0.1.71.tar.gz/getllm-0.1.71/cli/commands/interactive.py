"""Interactive model installation commands."""
from typing import Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from ..commands.base import BaseCommand
from getllm.models.interactive import interactive_model_search

class InteractiveInstallCommand(BaseCommand):
    """Interactive model installation command."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'interactive',
            'help': 'Interactive model installation',
            'aliases': ['i'],
            'options': [
                {
                    'param_decls': ['--source'],
                    'kwargs': {
                        'type': str,
                        'default': 'all',
                        'help': 'Source to search (all, ollama, huggingface)'
                    }
                }
            ]
        }
    
    def execute(self, source: str = 'all', **kwargs) -> None:
        """Execute interactive installation."""
        console = Console()
        
        console.print(Panel.fit(
            "[bold blue]Interactive Model Installation[/bold blue]\n"
            "Search for models by name or description. Press Ctrl+C to exit.",
            border_style="blue"
        ))
        
        while True:
            try:
                search_query = Prompt.ask("[bold]Search models[/bold] (or 'q' to quit)")
                if search_query.lower() in ('q', 'quit', 'exit'):
                    break
                
                model_id = interactive_model_search(search_query)
                if model_id:
                    console.print(f"\n[green]Selected model: {model_id}[/green]")
                    if Prompt.ask("Install this model? (y/N)").lower() == 'y':
                        from .models import install_model_with_progress
                        success = install_model_with_progress(model_id)
                        if success:
                            console.print(f"[green]✓ Successfully installed {model_id}[/green]")
                        else:
                            console.print(f"[red]Failed to install {model_id}[/red]")
                else:
                    console.print("[yellow]No models found matching your query.[/yellow]")
                
            except KeyboardInterrupt:
                console.print("\nExiting interactive mode.")
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                continue

def register_commands(cli_group):
    """Register interactive commands."""
    cli_group.add_command(InteractiveInstallCommand.create_click_command())
