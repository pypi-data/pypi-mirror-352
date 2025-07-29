"""Command modules for the GetLLM CLI."""
from . import models, server, generate, config, chat, interactive

def register_commands(cli_group):
    """Register all command groups with the CLI.
    
    Args:
        cli_group: The main Click command group
    """
    # Register each command group
    models.register_commands(cli_group)
    server.register_commands(cli_group)
    generate.register_commands(cli_group)
    config.register_commands(cli_group)
    chat.register_commands(cli_group)
    interactive.register_commands(cli_group)
