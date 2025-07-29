"""Code generation commands for the CLI."""
from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.syntax import Syntax

from ..commands.base import BaseCommand
from getllm import ModelManager, get_ollama_integration

class GenerateCodeCommand(BaseCommand):
    """Command to generate code using an installed model."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'generate',
            'help': 'Generate code using an installed model',
            'args': [
                {
                    'name': 'prompt',
                    'type': str,
                    'required': True,
                    'help': 'Prompt describing the code to generate'
                }
            ],
            'options': [
                {
                    'param_decls': ['--model', '-m'],
                    'kwargs': {
                        'type': str,
                        'help': 'Model ID to use for generation',
                        'default': None
                    }
                },
                {
                    'param_decls': ['--temperature'],
                    'kwargs': {
                        'type': float,
                        'help': 'Sampling temperature (0.0 to 1.0)',
                        'default': 0.7
                    }
                },
                {
                    'param_decls': ['--max-tokens'],
                    'kwargs': {
                        'type': int,
                        'help': 'Maximum number of tokens to generate',
                        'default': 1000
                    }
                },
                {
                    'param_decls': ['--output', '-o'],
                    'kwargs': {
                        'type': click.Path(dir_okay=False, writable=True),
                        'help': 'Output file path',
                        'default': None
                    }
                },
                {
                    'param_decls': ['--language', '-l'],
                    'kwargs': {
                        'type': str,
                        'help': 'Programming language for syntax highlighting',
                        'default': 'python'
                    }
                }
            ]
        }
    
    def execute(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: int,
        output: Optional[str],
        language: str,
        **kwargs
    ) -> None:
        """Execute the code generation command."""
        console = Console()
        manager = ModelManager()
        
        # If no model specified, try to get the default model
        if not model:
            model = manager.get_default_model()
            if not model:
                console.print("[red]No model specified and no default model set.[/red]")
                console.print("Please specify a model with --model or set a default model.")
                return
        
        # Check if model is installed
        if not manager.is_model_installed(model):
            console.print(f"[yellow]Model {model} is not installed. Installing...[/yellow]")
            try:
                if not manager.install_model(model):
                    console.print(f"[red]Failed to install model {model}[/red]")
                    return
            except Exception as e:
                console.print(f"[red]Error installing model: {str(e)}[/red]")
                return
        
        # Get the Ollama integration
        try:
            ollama = get_ollama_integration()
            
            with console.status(f"[green]Generating code with {model}...[/green]"):
                # Generate the code
                response = ollama.generate(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Extract the generated code
                generated_code = response.get('text', '').strip()
                
                # If output file is specified, save to file
                if output:
                    with open(output, 'w', encoding='utf-8') as f:
                        f.write(generated_code)
                    console.print(f"[green]✓ Code saved to {output}[/green]")
                
                # Display the generated code with syntax highlighting
                console.print("\n[bold]Generated code:[/bold]")
                syntax = Syntax(generated_code, language, theme="monokai", line_numbers=True)
                console.print(syntax)
                
        except Exception as e:
            console.print(f"[red]Error generating code: {str(e)}[/red]")


def register_commands(cli_group: click.Group) -> None:
    """Register code generation commands with the CLI group."""
    commands = [
        GenerateCodeCommand,
    ]
    
    for cmd_class in commands:
        cmd = cmd_class.create_click_command()
        cli_group.add_command(cmd)
