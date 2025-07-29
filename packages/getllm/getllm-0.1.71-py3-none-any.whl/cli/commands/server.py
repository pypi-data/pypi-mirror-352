"""Server management CLI commands."""
from typing import Any, Dict

import click
from rich.console import Console

from ..commands.base import BaseCommand
from getllm.ollama_integration.server import OllamaServer

class StartServerCommand(BaseCommand):
    """Command to start the Ollama server."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'start',
            'help': 'Start the Ollama server',
            'options': [
                {
                    'param_decls': ['--port'],
                    'kwargs': {
                        'type': int,
                        'default': 11434,
                        'help': 'Port to run the server on'
                    }
                },
                {
                    'param_decls': ['--host'],
                    'kwargs': {
                        'type': str,
                        'default': '127.0.0.1',
                        'help': 'Host to bind the server to'
                    }
                }
            ]
        }
    
    def execute(self, port: int, host: str, **kwargs) -> None:
        """Execute the start server command."""
        console = Console()
        
        try:
            with console.status("[green]Starting Ollama server...[/green]"):
                server = OllamaServer()
                server.start(host=host, port=port)
                
            console.print(f"[green]✓ Ollama server started on {host}:{port}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to start Ollama server: {str(e)}[/red]")


class StopServerCommand(BaseCommand):
    """Command to stop the Ollama server."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'stop',
            'help': 'Stop the Ollama server',
            'options': []
        }
    
    def execute(self, **kwargs) -> None:
        """Execute the stop server command."""
        console = Console()
        
        try:
            with console.status("[green]Stopping Ollama server...[/green]"):
                server = OllamaServer()
                server.stop()
                
            console.print("[green]✓ Ollama server stopped[/green]")
        except Exception as e:
            console.print(f"[red]Failed to stop Ollama server: {str(e)}[/red]")


class ServerStatusCommand(BaseCommand):
    """Command to check server status."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'status',
            'help': 'Check Ollama server status',
            'options': []
        }
    
    def execute(self, **kwargs) -> None:
        """Execute the server status command."""
        console = Console()
        server = OllamaServer()
        
        try:
            if server.is_running():
                console.print("[green]✓ Ollama server is running[/green]")
                console.print(f"  - URL: {server.base_url}")
            else:
                console.print("[yellow]Ollama server is not running[/yellow]")
        except Exception as e:
            console.print(f"[red]Error checking server status: {str(e)}[/red]")


def register_commands(cli_group: click.Group) -> None:
    """Register server-related commands with the CLI group."""
    server_group = click.Group('server', help='Manage Ollama server')
    
    commands = [
        StartServerCommand,
        StopServerCommand,
        ServerStatusCommand,
    ]
    
    for cmd_class in commands:
        cmd = cmd_class.create_click_command()
        server_group.add_command(cmd)
    
    cli_group.add_command(server_group)
