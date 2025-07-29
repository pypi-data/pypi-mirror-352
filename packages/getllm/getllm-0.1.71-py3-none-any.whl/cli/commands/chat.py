"""Interactive chat commands for the CLI."""
from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from ..commands.base import BaseCommand
from ..utils import display_model_info
from getllm import ModelManager, get_models

class ChatCommand(BaseCommand):
    """Command to start an interactive chat with a model."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'chat',
            'help': 'Start an interactive chat with a model',
            'options': [
                {
                    'param_decls': ['--model', '-m'],
                    'kwargs': {
                        'type': str,
                        'help': 'Model ID to chat with (e.g., ollama/llama2)',
                        'required': False
                    }
                },
                {
                    'param_decls': ['--temperature'],
                    'kwargs': {
                        'type': float,
                        'default': 0.7,
                        'help': 'Sampling temperature (0-2)',
                        'show_default': True
                    }
                },
                {
                    'param_decls': ['--max-tokens'],
                    'kwargs': {
                        'type': int,
                        'default': 1000,
                        'help': 'Maximum number of tokens to generate',
                        'show_default': True
                    }
                }
            ]
        }
    
    def _print_help(self) -> None:
        """Print chat help information."""
        console = Console()
        help_text = """
[bold]Chat Commands:[/bold]
  /help     - Show this help message
  /exit     - Exit the chat
  /clear    - Clear the chat history
  /model    - Show current model info
  /models   - List available models
  /switch   - Switch to a different model
        """
        console.print(Panel(help_text, title="Chat Help", border_style="blue"))
    
    def _print_welcome(self, model_id: str) -> None:
        """Print welcome message with model info."""
        console = Console()
        console.print(f"[bold green]Starting chat with {model_id}[/bold green]")
        console.print("Type /help for available commands\n")
    
    def _select_model(self) -> Optional[str]:
        """Interactively select a model from available models."""
        console = Console()
        models = get_models()
        
        if not models:
            console.print("[yellow]No models available. Install a model first.[/yellow]")
            return None
        
        # Filter to only installed models for chat
        manager = ModelManager()
        installed_models = [m for m in models if manager.is_model_installed(m.id)]
        
        if not installed_models:
            console.print("[yellow]No models installed. Install a model first.[/yellow]")
            return None
        
        # If only one model is available, use it
        if len(installed_models) == 1:
            return installed_models[0].id
        
        # Show model selection
        console.print("\n[bold]Available Models:[/bold]")
        for i, model in enumerate(installed_models, 1):
            console.print(f"  [cyan]{i}.[/cyan] {model.id} - {model.name}")
        
        while True:
            try:
                choice = Prompt.ask("\nSelect a model (number or ID)")
                
                # Try to parse as number
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(installed_models):
                        return installed_models[idx].id
                except ValueError:
                    # Not a number, try to match by ID
                    for model in installed_models:
                        if model.id.lower() == choice.lower():
                            return model.id
                
                console.print("[red]Invalid selection. Please try again.[/red]")
                
            except (KeyboardInterrupt, EOFError):
                return None
    
    def execute(
        self, 
        model: Optional[str], 
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> None:
        """Execute the chat command."""
        console = Console()
        manager = ModelManager()
        
        # If no model specified, show selection
        if not model:
            model = self._select_model()
            if not model:
                return
        
        # Verify model is installed
        if not manager.is_model_installed(model):
            console.print(f"[yellow]Model {model} is not installed. Installing now...[/yellow]")
            if not manager.install_model(model):
                console.print(f"[red]Failed to install model {model}[/red]")
                return
        
        self._print_welcome(model)
        
        # Initialize chat history
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold]You[/bold]")
                
                # Handle commands
                if user_input.startswith('/'):
                    cmd = user_input[1:].lower().split()[0] if user_input[1:] else ""
                    
                    if cmd == 'exit':
                        console.print("\n[green]Goodbye![/green]")
                        break
                        
                    elif cmd == 'help':
                        self._print_help()
                        continue
                        
                    elif cmd == 'clear':
                        messages = messages[:1]  # Keep system message
                        console.print("\n[green]Chat history cleared.[/green]")
                        continue
                        
                    elif cmd == 'model':
                        display_model_info(model)
                        continue
                        
                    elif cmd == 'models':
                        from ..utils import display_models
                        display_models(
                            models=get_models(),
                            installed_only=True
                        )
                        continue
                        
                    elif cmd == 'switch':
                        new_model = self._select_model()
                        if new_model and new_model != model:
                            model = new_model
                            console.print(f"\n[green]Switched to model: {model}[/green]")
                            # Keep the conversation history but update the model
                            continue
                        continue
                        
                    else:
                        console.print(f"[yellow]Unknown command: /{cmd}. Type /help for available commands.[/yellow]")
                        continue
                
                # Add user message to history
                messages.append({"role": "user", "content": user_input})
                
                # Get model response
                with console.status("Thinking..."):
                    try:
                        response = manager.generate(
                            model_id=model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        
                        # Display response
                        console.print("\n[bold]Assistant:[/bold]")
                        console.print(Markdown(response))
                        
                        # Add assistant response to history
                        messages.append({"role": "assistant", "content": response})
                        
                    except Exception as e:
                        console.print(f"[red]Error generating response: {str(e)}[/red]")
                        # Remove the last user message if there was an error
                        if messages and messages[-1]["role"] == "user":
                            messages.pop()
            
            except KeyboardInterrupt:
                console.print("\n[green]\nUse /exit to quit or /help for commands[/green]")
            except EOFError:
                console.print("\n[green]Goodbye![/green]")
                break


def register_commands(cli_group: click.Group) -> None:
    """Register chat-related commands with the CLI group."""
    chat_group = click.Group('chat', help='Interactive chat with models')
    
    # Register chat commands
    commands = [
        ChatCommand,
    ]
    
    for cmd_class in commands:
        cmd = cmd_class.create_click_command()
        chat_group.add_command(cmd)
    
    cli_group.add_command(chat_group)
