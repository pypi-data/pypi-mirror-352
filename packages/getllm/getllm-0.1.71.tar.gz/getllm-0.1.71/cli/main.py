"""Main CLI entry point for GetLLM."""
import click
from rich.console import Console

# Import command modules
from .commands import models, server, generate, config, chat

# Create main CLI group
@click.group()
@click.version_option()
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
@click.option('--log-file', type=click.Path(dir_okay=False, writable=True), 
              help='Path to log file')
@click.pass_context
def cli(ctx: click.Context, debug: bool, log_file: str) -> None:
    """GetLLM - Command line interface for managing LLM models and generating code.
    
    This CLI provides commands for managing LLM models, interacting with the Ollama server,
    and generating code using installed models.
    """
    # Ensure context.obj exists and is a dict
    ctx.ensure_object(dict)
    
    # Store common options in context
    ctx.obj['debug'] = debug
    ctx.obj['log_file'] = log_file
    
    # Set up logging
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Log command execution
    if debug:
        console = Console()
        console.print(f"[debug] Executing command: {ctx.command_path}")


def main() -> None:
    """Entry point for the CLI."""
    # Register command groups
    models.register_commands(cli)      # Model management commands
    server.register_commands(cli)      # Server management commands
    generate.register_commands(cli)    # Code generation commands
    config.register_commands(cli)      # Configuration management commands
    chat.register_commands(cli)        # Interactive chat commands
    
    # Run the CLI
    cli(obj={})


if __name__ == "__main__":
    main()
