"""Base command class for CLI commands."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

import click

class BaseCommand(ABC):
    """Base class for CLI commands."""
    
    def __init__(self, debug: bool = False, log_file: Optional[str] = None):
        """Initialize the command with common options.
        
        Args:
            debug: Enable debug logging
            log_file: Path to log file
        """
        self.debug = debug
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self) -> None:
        """Set up logging configuration."""
        from ..utils.logging import configure_logging
        configure_logging(debug=self.debug, log_file=self.log_file)
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the command.
        
        Args:
            **kwargs: Command-specific arguments
            
        Returns:
            Command execution result
        """
        pass
    
    @classmethod
    def create_click_command(cls) -> click.Command:
        """Create a Click command from this class.
        
        Returns:
            click.Command: Configured Click command
        """
        @click.pass_context
        def callback(ctx, **kwargs):
            """Click command callback."""
            # Create command instance with common options
            command = cls(
                debug=kwargs.pop('debug', False),
                log_file=kwargs.pop('log_file', None)
            )
            # Execute the command with remaining kwargs
            return command.execute(**kwargs)
            
        # Get command configuration
        cmd_config = cls.get_command_config()
        
        # Create Click command
        cmd = click.Command(
            name=cmd_config['name'],
            help=cmd_config.get('help', ''),
            callback=callback
        )
        
        # Add common options
        cmd.params.extend([
            click.Option(
                ['--debug'],
                is_flag=True,
                help='Enable debug logging'
            ),
            click.Option(
                ['--log-file'],
                type=click.Path(dir_okay=False, writable=True),
                help='Path to log file'
            )
        ])
        
        # Add command-specific options
        for option in cmd_config.get('options', []):
            cmd.params.append(click.Option(option['param_decls'], **option['kwargs']))
            
        return cmd
    
    @classmethod
    @abstractmethod
    def get_command_config(cls) -> Dict[str, Any]:
        """Get command configuration for Click.
        
        Returns:
            Dict containing command configuration
            
        Example:
            {
                'name': 'my-command',
                'help': 'Command help text',
                'options': [
                    {
                        'param_decls': ['--option1', '-o'],
                        'kwargs': {
                            'type': str,
                            'help': 'Option help text',
                            'required': True
                        }
                    }
                ]
            }
        """
        pass
