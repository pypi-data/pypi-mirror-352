"""Configuration management commands for the CLI."""
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.table import Table

from ..commands.base import BaseCommand

# Default configuration file path
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.getllm')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

# Default configuration
DEFAULT_CONFIG = {
    "default_model": None,
    "log_level": "INFO",
    "model_cache_dir": os.path.join(CONFIG_DIR, "models"),
    "ollama_url": "http://localhost:11434"
}

class ConfigCommand(BaseCommand):
    """Base class for configuration commands."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = self._load_config()
    
    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        os.makedirs(CONFIG_DIR, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from file."""
        self._ensure_config_dir()
        
        if not os.path.exists(CONFIG_FILE):
            return DEFAULT_CONFIG.copy()
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Ensure all default keys exist
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG.copy()
    
    def _save_config(self) -> None:
        """Save the configuration to file."""
        self._ensure_config_dir()
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)


class ConfigGetCommand(ConfigCommand):
    """Get a configuration value."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'get',
            'help': 'Get a configuration value',
            'args': [
                {
                    'name': 'key',
                    'type': str,
                    'required': True,
                    'help': 'Configuration key to get'
                }
            ]
        }
    
    def execute(self, key: str, **kwargs) -> None:
        """Execute the config get command."""
        console = Console()
        
        if key not in self.config:
            console.print(f"[red]Unknown configuration key: {key}[/red]")
            return
        
        console.print(f"{key} = {self.config[key]}")


class ConfigSetCommand(ConfigCommand):
    """Set a configuration value."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'set',
            'help': 'Set a configuration value',
            'args': [
                {
                    'name': 'key',
                    'type': click.Choice(list(DEFAULT_CONFIG.keys())),
                    'required': True,
                    'help': 'Configuration key to set'
                },
                {
                    'name': 'value',
                    'type': str,
                    'required': True,
                    'help': 'Value to set'
                }
            ]
        }
    
    def execute(self, key: str, value: str, **kwargs) -> None:
        """Execute the config set command."""
        console = Console()
        
        # Convert value to appropriate type based on default
        default_value = DEFAULT_CONFIG[key]
        if isinstance(default_value, bool):
            value = value.lower() in ('true', '1', 'yes', 'y')
        elif isinstance(default_value, int):
            try:
                value = int(value)
            except ValueError:
                console.print(f"[red]Invalid value for {key}: must be an integer[/red]")
                return
        elif isinstance(default_value, float):
            try:
                value = float(value)
            except ValueError:
                console.print(f"[red]Invalid value for {key}: must be a number[/red]")
                return
        
        self.config[key] = value
        self._save_config()
        console.print(f"[green]✓ Set {key} = {value}[/green]")


class ConfigListCommand(ConfigCommand):
    """List all configuration values."""
    
    @classmethod
    def get_command_config(cls) -> Dict[str, Any]:
        return {
            'name': 'list',
            'help': 'List all configuration values',
            'options': []
        }
    
    def execute(self, **kwargs) -> None:
        """Execute the config list command."""
        console = Console()
        
        table = Table(title="Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Default", style="magenta")
        
        for key, value in sorted(self.config.items()):
            default_value = DEFAULT_CONFIG.get(key, "")
            table.add_row(
                key,
                str(value),
                str(default_value) if default_value != value else ""
            )
        
        console.print(table)


def register_commands(cli_group: click.Group) -> None:
    """Register configuration commands with the CLI group."""
    config_group = click.Group('config', help='Manage configuration')
    
    commands = [
        ConfigGetCommand,
        ConfigSetCommand,
        ConfigListCommand,
    ]
    
    for cmd_class in commands:
        cmd = cmd_class.create_click_command()
        config_group.add_command(cmd)
    
    cli_group.add_command(config_group)
