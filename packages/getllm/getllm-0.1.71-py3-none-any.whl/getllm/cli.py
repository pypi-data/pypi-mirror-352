#!/usr/bin/env python3

import argparse
import sys
import os
import re
import tempfile
import platform
from pathlib import Path

# Import from getllm modules
from getllm import models
from getllm.ollama_integration import OllamaIntegration, get_ollama_integration as get_ollama_server

# Create .getllm directory if it doesn't exist
PACKAGE_DIR = os.path.join(os.path.expanduser('~'), '.getllm')
os.makedirs(PACKAGE_DIR, exist_ok=True)

# Configure logging
import logging
import logging.handlers
import datetime

# Create logger
logger = logging.getLogger('getllm')
logger.setLevel(logging.INFO)

# Create log directory if it doesn't exist
LOG_DIR = os.path.join(PACKAGE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Log file with timestamp
DEFAULT_LOG_FILE = os.path.join(LOG_DIR, f'getllm_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Function to configure logging based on debug flag
def configure_logging(debug=False, log_file=None):
    """Configure logging based on debug flag and log file path."""
    if log_file is None:
        log_file = DEFAULT_LOG_FILE
        
    # Set log level based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in logger.handlers[::]:
        logger.removeHandler(handler)
    
    # Create file handler with rotation to keep log files manageable
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level if debug else logging.WARNING)
    
    # Create detailed formatter
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
    )
    file_handler.setFormatter(detailed_formatter)
    
    # Create simpler formatter for console
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Configure root logger to catch all logs
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers from root logger
    for handler in root_logger.handlers[::]:
        root_logger.removeHandler(handler)
    
    # Add a file handler to the root logger
    root_logger.addHandler(file_handler)
    
    logger.debug(f'Logging configured. Debug mode: {debug}, Log file: {log_file}')
    if debug:
        logger.debug('Debug logging is enabled - detailed logs will be shown and saved to file')
    else:
        logger.info('Normal logging mode - only warnings and errors will be shown in console')

# Template functions for code generation
def get_template(prompt, template_type, **kwargs):
    """Get a template for code generation based on the template type."""
    templates = {
        "basic": """Generate Python code for the following task: {prompt}""",
        
        "platform_aware": """Generate Python code for the following task: {prompt}

The code should run on {platform} operating system.
{dependencies}""",
        
        "dependency_aware": """Generate Python code for the following task: {prompt}

Use only the following dependencies: {dependencies}""",
        
        "testable": """Generate Python code for the following task: {prompt}

Include unit tests for the code.
{dependencies}""",
        
        "secure": """Generate secure Python code for the following task: {prompt}

Ensure the code follows security best practices and handles errors properly.
{dependencies}""",
        
        "performance": """Generate high-performance Python code for the following task: {prompt}

Optimize the code for performance.
{dependencies}""",
        
        "pep8": """Generate Python code for the following task: {prompt}

Ensure the code follows PEP 8 style guidelines.
{dependencies}""",
        
        "debug": """Debug the following Python code that has an error:

```python
{code}
```

Error message:
{error_message}

Fix the code to solve the problem and provide the corrected version."""
    }
    
    # Get the template or use basic if not found
    template = templates.get(template_type, templates["basic"])
    
    # Format dependencies if provided
    if "dependencies" in kwargs:
        if kwargs["dependencies"]:
            kwargs["dependencies"] = f"Use the following dependencies: {kwargs['dependencies']}"
        else:
            kwargs["dependencies"] = "Use standard Python libraries."
    else:
        kwargs["dependencies"] = "Use standard Python libraries."
    
    # Format the template with the provided arguments
    return template.format(prompt=prompt, **kwargs)

# Sandbox classes for code execution
class PythonSandbox:
    """Simple implementation of PythonSandbox."""
    def __init__(self):
        pass
    
    def run(self, code):
        """Run Python code in a sandbox."""
        # Create a temporary file to store the code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(code.encode('utf-8'))
            temp_file = f.name
        
        try:
            # Run the code in a separate process
            import subprocess
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            # Return the result
            if result.returncode == 0:
                return {
                    "output": result.stdout,
                    "error": None
                }
            else:
                return {
                    "output": result.stdout,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "output": "",
                "error": str(e)
            }
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file)
            except:
                pass

# Mock implementation for testing without Ollama
class MockOllamaServer:
    """Mock implementation of OllamaServer for testing."""
    def __init__(self, model=None):
        self.model = model or "mock-model"
    
    def query_ollama(self, prompt, template_type=None, **template_args):
        """Mock implementation of query_ollama."""
        if "hello world" in prompt.lower():
            return "print('Hello, World!')"
        elif "binary search tree" in prompt.lower():
            return """
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None
    
    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
        else:
            self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = Node(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = Node(value)
            else:
                self._insert_recursive(node.right, value)
    
    def search(self, value):
        return self._search_recursive(self.root, value)
    
    def _search_recursive(self, node, value):
        if node is None or node.value == value:
            return node
        if value < node.value:
            return self._search_recursive(node.left, value)
        return self._search_recursive(node.right, value)

# Example usage
bst = BinarySearchTree()
bst.insert(5)
bst.insert(3)
bst.insert(7)
bst.insert(2)
bst.insert(4)

print("Searching for 4:", bst.search(4).value if bst.search(4) else "Not found")
print("Searching for 6:", bst.search(6).value if bst.search(6) else "Not found")
"""
        else:
            return f"# Mock code for: {prompt}\nprint('This is mock code generated for testing')\n"
    
    def extract_python_code(self, text):
        """Mock implementation of extract_python_code."""
        return text

# Helper functions
def save_code_to_file(code, filename=None):
    """Save the generated code to a file."""
    if filename is None:
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(PACKAGE_DIR, f"generated_script_{timestamp}.py")
    
    # Ensure the target directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    
    logger.info(f'Saved script to file: {filename}')
    return os.path.abspath(filename)

def execute_code(code, use_docker=False):
    """Execute the generated code and return the result."""
    # Create the sandbox
    sandbox = PythonSandbox()
    
    # Execute the code
    return sandbox.run(code)

def extract_python_code(text):
    """Extract Python code from the response."""
    # If the response already looks like code (no markdown), return it
    if text.strip().startswith("import ") or text.strip().startswith("#") or text.strip().startswith("def ") or text.strip().startswith("class ") or text.strip().startswith("print"):
        return text
        
    # Look for Python code blocks in markdown
    import re
    code_block_pattern = r"```(?:python)?\s*([\s\S]*?)```"
    matches = re.findall(code_block_pattern, text)
    
    if matches:
        # Return the first code block found
        return matches[0].strip()
    
    # If no code blocks found but the text contains "print hello world" or similar
    if "print hello world" in text.lower() or "print(\"hello world\")" in text.lower() or "print('hello world')" in text.lower():
        return "print(\"Hello, World!\")"
    
    # If all else fails, return the original text with a warning
    return """# Could not extract Python code from the model response
# Here's a simple implementation:

print("Hello, World!")

# Original response:
# """ + text

def check_ollama():
    """Check if Ollama is running and return its version."""
    try:
        # Try to connect to the Ollama API
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        if response.status_code == 200:
            return response.json().get("version", "unknown")
        return None
    except Exception:
        return None

def interactive_mode(mock_mode=False):
    """Run in interactive mode, allowing the user to input prompts."""
    from getllm.interactive_cli import interactive_shell
    interactive_shell(mock_mode=mock_mode)

def main():
    """Main entry point for the getllm CLI."""
    # First check for direct prompts
    direct_prompt = False
    prompt = None
    args_to_parse = sys.argv[1:]
    
    # Check for environment variables
    env_debug = os.environ.get('GETLLM_DEBUG', '').lower() in ('1', 'true', 'yes')
    env_model = os.environ.get('GETLLM_MODEL', None)
    
    # Pre-parse for debug flag to set up logging early
    debug_mode = "--debug" in args_to_parse or env_debug
    
    # Check if the first argument is a command or looks like a prompt
    commands = ["code", "list", "install", "installed", "set-default", "default", "update", "test", "interactive"]
    
    # Special handling for -search command (common user error)
    if len(args_to_parse) >= 2 and args_to_parse[0] == "-search":
        # Convert to proper format
        args_to_parse[0] = "--search"
    
    if len(args_to_parse) > 0 and not args_to_parse[0].startswith('-') and args_to_parse[0] not in commands:
        # This is a direct prompt
        direct_prompt = True
        prompt_parts = []
        options = []
        
        # Separate prompt parts from options
        i = 0
        while i < len(args_to_parse):
            if args_to_parse[i].startswith('-'):
                options.append(args_to_parse[i])
                # If this option takes a value, add it too
                if i + 1 < len(args_to_parse) and not args_to_parse[i+1].startswith('-'):
                    if args_to_parse[i] in ["-m", "--model", "-t", "--template", "-d", "--dependencies"]:
                        options.append(args_to_parse[i+1])
                        i += 1
            else:
                prompt_parts.append(args_to_parse[i])
            i += 1
        
        # Combine prompt parts
        prompt = " ".join(prompt_parts)
        
        # Parse just the options
        args_to_parse = options
    
    # Create the argument parser with a custom formatter that shows global options in help
    class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
        def _format_action(self, action):
            # This is a hack to show global options in the help text
            parts = super()._format_action(action)
            if action.dest in ['mock', 'debug', 'log_file', 'version']:
                parts = parts.replace('optional arguments', 'global arguments')
            return parts

    parser = argparse.ArgumentParser(
        description="getllm CLI - LLM Model Management and Code Generation",
        formatter_class=CustomHelpFormatter
    )
    
    # Global options
    global_group = parser.add_argument_group('global arguments')
    global_group.add_argument("--mock", action="store_true", help="Use mock mode (no Ollama required)")
    global_group.add_argument("--debug", action="store_true", help="Enable debug mode with verbose logging")
    global_group.add_argument("--log-file", help="Specify custom log file path")
    global_group.add_argument("--version", action="store_true", help="Show version information")
    
    # Common options
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("-m", "--model", help="Name of the Ollama model to use")
    parser.add_argument("--search", metavar="QUERY", help="Search for models on Hugging Face matching the query")
    parser.add_argument("-S", "--find-model", dest="search", metavar="QUERY", help="Alias for --search")
    parser.add_argument("--update-hf", action="store_true", help="Update models list from Hugging Face")
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command")
    
    # Code generation command
    code_parser = subparsers.add_parser("code", help="Generate Python code using LLM models")
    code_parser.add_argument("prompt", nargs="+", help="Task to be performed by Python code")
    code_parser.add_argument("-t", "--template", 
                          choices=["basic", "platform_aware", "dependency_aware", "testable", "secure", "performance", "pep8"],
                          default="platform_aware",
                          help="Type of template to use")
    code_parser.add_argument("-d", "--dependencies", help="List of allowed dependencies (only for template=dependency_aware)")
    code_parser.add_argument("-s", "--save", action="store_true", help="Save the generated code to a file")
    code_parser.add_argument("-r", "--run", action="store_true", help="Run the generated code after creation")
    
    # Model management commands
    subparsers.add_parser("list", help="List available models (from models.json)")
    
    parser_install = subparsers.add_parser("install", help="Install a model using Ollama")
    parser_install.add_argument("model", nargs="?", help="Name of the model to install. If not provided, will show available models.")
    
    subparsers.add_parser("installed", help="List installed models (ollama list)")
    
    parser_setdef = subparsers.add_parser("set-default", help="Set the default model")
    parser_setdef.add_argument("model", help="Name of the model to set as default")
    
    subparsers.add_parser("default", help="Show the default model")
    
    # Update command with mock support
    update_parser = subparsers.add_parser("update", help="Update the list of models from ollama.com/library")
    update_parser.add_argument("--mock", action="store_true", help="Run in mock mode (no Ollama required)")
    
    subparsers.add_parser("test", help="Test the default model")
    
    interactive_parser = subparsers.add_parser("interactive", help="Run in interactive mode")
    interactive_parser.add_argument("--mock", action="store_true", help="Run in mock mode (no Ollama required)")
    
    # First check for version flag in the raw arguments
    if "--version" in sys.argv[1:]:
        from getllm import __version__
        print(f"getLLM version {__version__}")
        return 0
        
    # Parse the arguments
    if direct_prompt:
        # For direct prompt, parse only the options
        args = parser.parse_args(args_to_parse)
        args.command = None  # No command when using direct prompt
    else:
        # Normal parsing for commands
        args = parser.parse_args()
        if hasattr(args, 'prompt') and args.command == "code":
            prompt = " ".join(args.prompt)
    
    # Apply environment variables to args if not explicitly set
    if env_debug and not args.debug:
        args.debug = True
        logger.debug('Debug mode enabled via GETLLM_DEBUG environment variable')
    
    if env_model and not args.model:
        args.model = env_model
        logger.debug(f'Using model {args.model} from GETLLM_MODEL environment variable')
    
    # Configure logging based on debug flag
    configure_logging(debug=args.debug, log_file=args.log_file)
    
    # Handle version flag (kept for backward compatibility with direct API calls)
    if hasattr(args, 'version') and args.version:
        from getllm import __version__
        print(f"getLLM version {__version__}")
        return 0
    
    # Handle Hugging Face model search
    if args.search or args.update_hf:
        from getllm.models import update_models_from_huggingface, interactive_model_search
        
        if args.search:
            # Search for models on Hugging Face
            print(f"Searching for models matching '{args.search}' on Hugging Face...")
            
            # If in mock mode, skip Ollama checks entirely
            if args.mock:
                print("\nRunning in mock mode - Ollama checks bypassed")
                selected_model = interactive_model_search(args.search, check_ollama=False)
            else:
                selected_model = interactive_model_search(args.search, check_ollama=True)
            if selected_model:
                # Ask if the user wants to install the model
                import questionary
                install_now = questionary.confirm("Do you want to install this model now?", default=True).ask()
                if install_now:
                    # Check if we're in mock mode
                    if args.mock:
                        print(f"\nUsing mock mode. Model installation is simulated.")
                        print(f"Model '{selected_model}' would be installed in normal mode.")
                    else:
                        from getllm.models import install_model
                        success = install_model(selected_model)
                        
                        if not success:
                            print("\nWould you like to continue in mock mode instead?")
                            continue_mock = questionary.confirm("Continue with mock mode?", default=True).ask()
                            if continue_mock:
                                print(f"\nContinuing in mock mode with model '{selected_model}'")
                                # Set up mock environment
                                os.environ['GETLLM_MOCK_MODEL'] = selected_model
            else:
                print("Search cancelled or no model selected.")
        else:  # args.update_hf
            # Update models from Hugging Face
            print("Updating models from Hugging Face...")
            logger.info("Starting update of models from Hugging Face")
            success = update_models_from_huggingface()
            if success:
                logger.info("Successfully updated models from Hugging Face")
                print("Successfully updated models from Hugging Face.")
            else:
                logger.error("Failed to update models from Hugging Face")
                print("Error updating models from Hugging Face. Check logs for details.")
                if args.debug:
                    print(f"Debug logs are available at: {args.log_file or DEFAULT_LOG_FILE}")
        
        return 0
        
    # Handle interactive mode
    if args.interactive or args.command == "interactive":
        interactive_mode(mock_mode=args.mock)
        return 0
    
    # Handle model management commands
    if args.command in ["list", "install", "installed", "set-default", "default", "update", "test"]:
        if args.command == "list":
            models_list = models.get_models()
            print("\nAvailable models:")
            for m in models_list:
                print(f"  {m.get('name', '-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}")
        elif args.command == "install":
            if not args.model:
                print("No model specified. Available models:")
                models_list = models.get_models()
                for m in models_list:
                    print(f"- {m.get('name', 'unknown')}")
                print("\nTo install a model, run: getllm install <model-name>")
                return 0
            models.install_model(args.model)
        elif args.command == "installed":
            models.list_installed_models()
        elif args.command == "set-default":
            models.set_default_model(args.model)
        elif args.command == "default":
            print("Default model:", models.get_default_model())
        elif args.command == "update":
            models.update_models_from_ollama(mock=args.mock)
        elif args.command == "test":
            default = models.get_default_model()
            print(f"Test default model: {default}")
            if default:
                print("OK: Default model is set.")
            else:
                print("ERROR: Default model is NOT set!")
        return 0
    
    # If we have a prompt, generate code
    if prompt or (hasattr(args, 'command') and args.command == 'code' and not direct_prompt):
        # Get model and template
        model = getattr(args, 'model', None)
        template = getattr(args, 'template', 'platform_aware')
        dependencies = getattr(args, 'dependencies', None)
        save = getattr(args, 'save', False)
        run = getattr(args, 'run', False)
        mock_mode = getattr(args, 'mock', False)
        
        # Check if Ollama is running (unless in mock mode)
        if not mock_mode:
            ollama_version = check_ollama()
            if not ollama_version:
                print("Ollama is not running. Please start Ollama with 'ollama serve' and try again.")
                print("Alternatively, use --mock for testing without Ollama.")
                return 1
        
        # Create OllamaIntegration or MockOllamaServer
        if not mock_mode:
            runner = get_ollama_server(model=model)
            if not runner.check_server_running():
                print("Starting Ollama server...")
                if not runner.start_ollama():
                    print("Failed to start Ollama server. Please make sure Ollama is installed and running.")
                    return 1
        else:
            runner = MockOllamaServer(model=model)
        
        # Prepare template arguments
        template_args = {}
        if dependencies:
            template_args["dependencies"] = dependencies
        
        # Add platform information for platform_aware template
        if template == "platform_aware":
            template_args["platform"] = platform.system()
        
        # Generate code
        print(f"\nGenerating code with model: {runner.model}")
        print(f"Using template: {template}")
        code = runner.query_ollama(prompt, template_type=template, **template_args)
        
        # Extract Python code if needed
        if hasattr(runner, "extract_python_code") and callable(getattr(runner, "extract_python_code")):
            code = runner.extract_python_code(code)
        else:
            code = extract_python_code(code)
        
        # Display the generated code
        if code:
            print("\nGenerated Python code:")
            print("-" * 40)
            print(code)
            print("-" * 40)
        else:
            print("\nNo code was generated. The model might need to be installed.")
            print("Try running 'getllm install <model-name>' first.")
        
        # Save the code if requested
        if save:
            code_file = save_code_to_file(code)
            print(f"\nCode saved to: {code_file}")
        
        # Run the code if requested
        if run:
            print("\nRunning the generated code...")
            result = execute_code(code)
            if result["error"]:
                print(f"Error running code: {result['error']}")
            else:
                print("Code execution result:")
                print(result["output"])
        
        return 0
    
    # If no command or prompt, show help
    parser.print_help()
    return 1

if __name__ == "__main__":
    main()
