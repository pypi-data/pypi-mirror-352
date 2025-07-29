from getllm import models
from getllm.models import update_huggingface_models_cache
import logging
import os
import datetime

# Get logger
logger = logging.getLogger('getllm.interactive_cli')

# Ensure we capture all interactive CLI operations in logs
logger.debug('Interactive CLI module loaded')
import questionary
import sys

MENU_OPTIONS = [
    ("List available models", "list"),
    ("Show default model", "default"),
    ("List installed models", "installed"),
    ("Install model (select from list)", "wybierz-model"),
    ("Search Hugging Face models", "search-hf"),
    ("Search ollama models", "search-ollama"),
    ("Set default model (select from list)", "wybierz-default"),
    ("Generate code (interactive)", "generate"),
    ("Update models list from ollama.com", "update"),
    ("Update models list from Hugging Face", "update-hf"),
    ("Test default model", "test"),
    ("Exit", "exit")
]

INTRO = """
GetLLM Interactive Mode
Use arrow keys to navigate, Enter to select, or type a command (e.g., install <model>)
"""

def choose_model(action_desc, callback):
    # First ask the user which source they want to use
    source = questionary.select(
        "Where would you like to get models from?",
        choices=[
            "Ollama Library (predefined models)",
            "Installed Models (local)",
            "Hugging Face Models (online)",
            "Search by name (all sources)"
        ]
    ).ask()
    
    if not source:
        print("Selection cancelled.")
        return
    
    # Get predefined models from models.json
    models_list = models.get_models()
    
    # Get installed models from Ollama
    from getllm.ollama.api import get_ollama_integration
    ollama = get_ollama_integration()
    
    # Only try to get installed models if Ollama is installed
    installed_models = []
    if ollama.is_ollama_installed:
        try:
            installed_models = ollama.list_installed_models()
        except Exception as e:
            print(f"Warning: Could not get installed models: {e}")
    
    # Create a set of predefined model names for quick lookup
    predefined_model_names = {m['name'] for m in models_list}
    
    # Prepare Hugging Face models
    hf_models = []
    try:
        from getllm.models import get_huggingface_models
        hf_models = get_huggingface_models()[:10]  # Get first 10 HF models
    except Exception as e:
        print(f"Warning: Could not get Hugging Face models: {e}")
    
    choices = []
    
    if source == "Search by name (all sources)":
        # Ask for search term
        search_term = questionary.text("Enter the first few letters or name of the model:").ask()
        if not search_term:
            print("Search cancelled.")
            return
        
        search_term = search_term.lower()
        
        # Filter models from all sources based on search term
        filtered_predefined = [m for m in models_list if search_term in m['name'].lower()]
        filtered_installed = [m for m in installed_models if search_term in m.get('name', '').lower()]
        filtered_hf = [m for m in hf_models if search_term in m.get('id', '').lower()]
        
        # Add predefined models that match
        if filtered_predefined:
            choices.append(questionary.Separator("--- Ollama Library Models ---"))
            for m in filtered_predefined:
                choices.append(
                    questionary.Choice(
                        title=f"{m.get('name','-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}",
                        value=m['name']
                    )
                )
        
        # Add installed models that match
        if filtered_installed:
            choices.append(questionary.Separator("--- Installed Models ---"))
            for m in filtered_installed:
                model_name = m.get('name', '')
                size = m.get('size', '')
                choices.append(
                    questionary.Choice(
                        title=f"{model_name:<25} {size}  [Installed model]",
                        value=model_name
                    )
                )
        
        # Add Hugging Face models that match
        if filtered_hf:
            choices.append(questionary.Separator("--- Hugging Face Models ---"))
            for m in filtered_hf:
                model_id = m.get('id', '')
                choices.append(
                    questionary.Choice(
                        title=f"{model_id:<25} [Hugging Face model]",
                        value=model_id
                    )
                )
    
    elif source == "Ollama Library (predefined models)":
        # Show top 10 predefined models
        top_models = models_list[:10]
        for m in top_models:
            choices.append(
                questionary.Choice(
                    title=f"{m.get('name','-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}",
                    value=m['name']
                )
            )
    
    elif source == "Installed Models (local)":
        # Show all installed models
        if installed_models:
            for m in installed_models:
                model_name = m.get('name', '')
                size = m.get('size', '')
                choices.append(
                    questionary.Choice(
                        title=f"{model_name:<25} {size}  [Installed model]",
                        value=model_name
                    )
                )
        else:
            print("No installed models found.")
            return
    
    elif source == "Hugging Face Models (online)":
        # Show top 10 Hugging Face models
        if hf_models:
            for m in hf_models:
                model_id = m.get('id', '')
                choices.append(
                    questionary.Choice(
                        title=f"{model_id:<25} [Hugging Face model]",
                        value=model_id
                    )
                )
        else:
            print("No Hugging Face models found.")
            return
    
    if not choices:
        print("No models found matching your criteria.")
        return
    
    answer = questionary.select(
        f"Select model to {action_desc}:", choices=choices
    ).ask()
    
    if answer:
        callback(answer)
    else:
        print("Selection cancelled.")

def generate_code_interactive(mock_mode=False):
    """Interactive code generation function"""
    from getllm.cli import get_template, extract_python_code, execute_code, save_code_to_file
    from getllm.ollama import OllamaServer
    import platform
    
    # Mock implementation for testing without Ollama
    if mock_mode:
        from getllm.cli import MockOllamaServer
        runner = MockOllamaServer()
        print("Using mock mode (no Ollama required)")
    else:
        # Get the default model
        model_name = models.get_default_model()
        if not model_name:
            print("No default model set. Please set a default model first.")
            return
            
        # Create an instance of OllamaServer with the default model and check if it's installed
        runner = OllamaServer(model=model_name)
        installed_models = runner.list_models()
        model_installed = any(m.get('name', '').startswith(model_name) for m in installed_models)
        
        if not model_installed:
            print(f"The default model '{model_name}' is not installed.")
            install = questionary.confirm(
                f"Would you like to install '{model_name}' now?", 
                default=True
            ).ask()
            
            if not install or not runner.install_model(model_name):
                print("Please install the model first using 'ollama pull <model_name>' or choose another model.")
                print(f"Available models: {', '.join(m.get('name', 'unknown') for m in installed_models)}")
                return
        
        runner.model = model_name  # Ensure the model name is set correctly
    
    # Get the prompt from the user
    prompt = questionary.text("Enter your code generation prompt:").ask()
    if not prompt:
        print("Cancelled.")
        return
    
    # Choose template
    template_choices = [
        "basic", "platform_aware", "dependency_aware", 
        "testable", "secure", "performance", "pep8"
    ]
    template = questionary.select(
        "Select template:",
        choices=template_choices,
        default="platform_aware"
    ).ask()
    if not template:
        print("Cancelled.")
        return
    
    # Get dependencies if using dependency_aware template
    dependencies = None
    if template == "dependency_aware":
        dependencies = questionary.text(
            "Enter dependencies (comma-separated):"
        ).ask()
    
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
    print("\nGenerated Python code:")
    print("-" * 40)
    print(code)
    print("-" * 40)
    
    # Ask if the user wants to save the code
    save = questionary.confirm("Save the code to a file?", default=False).ask()
    if save:
        code_file = save_code_to_file(code)
        print(f"\nCode saved to: {code_file}")
    
    # Ask if the user wants to run the code
    run = questionary.confirm("Run the generated code?", default=False).ask()
    if run:
        print("\nRunning the generated code...")
        result = execute_code(code)
        if result["error"]:
            print(f"Error running code: {result['error']}")
        else:
            print("Code execution result:")
            print(result["output"])

def interactive_shell(mock_mode=False):
    logger.info('Starting interactive shell session')
    logger.debug(f'Interactive shell mode: {"mock" if mock_mode else "normal"}')
    
    print(INTRO)
    if mock_mode:
        print("Running in mock mode (no Ollama required)")
        logger.debug('Mock mode enabled - Ollama checks will be bypassed')
    
    while True:
        answer = questionary.select(
            "Select an action from the menu:",
            choices=[questionary.Choice(title=desc, value=cmd) for desc, cmd in MENU_OPTIONS]
        ).ask()
        if not answer:
            print("Cancelled or exiting menu.")
            break
        cmd = answer
        args = cmd.split()
        if args[0] == "exit" or args[0] == "quit": 
            print("Exiting interactive mode.")
            break
        elif args[0] == "list":
            models_list = models.get_models()
            print("\nAvailable models:")
            for m in models_list:
                print(f"  {m.get('name', '-'):<25} {m.get('size','') or m.get('size_b','')}  {m.get('desc','')}")
        elif args[0] == "install" and len(args) > 1:
            models.install_model(args[1])
        elif args[0] == "installed":
            models.list_installed_models()
        elif args[0] == "set-default" and len(args) > 1:
            models.set_default_model(args[1])
        elif args[0] == "default":
            print("Default model:", models.get_default_model())
        elif args[0] == "update":
            # Update models from Ollama
            print("Updating models from Ollama...")
            try:
                logger.debug('Starting update of Ollama models')
                from getllm.models import update_models_from_ollama
                success = update_models_from_ollama()
                
                if success:
                    logger.info('Successfully updated models from Ollama')
                    print("Successfully updated models from Ollama.")
                else:
                    logger.error('Failed to update models from Ollama')
                    print("Error updating models from Ollama. Check logs for details.")
            except Exception as e:
                logger.error(f'Error during Ollama models update: {e}', exc_info=True)
                print(f"Error updating models from Ollama: {e}")
                print("Check logs for more details or run with --debug flag for verbose output.")
        elif args[0] == "test":
            default = models.get_default_model()
            print(f"Test default model: {default}")
            if default:
                print("OK: Default model is set.")
            else:
                print("ERROR: Default model is NOT set!")
        elif args[0] == "wybierz-model":
            choose_model("install", models.install_model)
        elif args[0] == "wybierz-default":
            choose_model("set as default", models.set_default_model)
        elif args[0] == "search-hf":
            # Search for models on Hugging Face
            from getllm.models import search_huggingface_models, DEFAULT_HF_MODELS
            query = questionary.text("Enter search term for Hugging Face models:").ask()
            if query:
                print(f"Searching for models matching '{query}' on Hugging Face...")
                # Get models from the search function (which now handles fallbacks internally)
                models_list = search_huggingface_models(query)
                
                if not models_list:
                    print(f"No models found matching '{query}'.")
                else:
                    # Create choices for the questionary select
                    choices = []
                    for m in models_list:
                        # Handle different model formats
                        model_id = m.get('id', m.get('name', ''))
                        model_desc = m.get('description', m.get('desc', ''))
                        
                        choices.append(questionary.Choice(
                            title=f"{model_id} - {model_desc}",
                            value=model_id
                        ))
                    
                    # Add a cancel option
                    choices.append(questionary.Choice(title="Cancel", value="__CANCEL__"))
                    
                    # Ask the user to select a model
                    selected_model = questionary.select(
                        "Select a model to install:",
                        choices=choices
                    ).ask()
                    
                    # If user selected Cancel, return early
                    if selected_model and selected_model != "__CANCEL__":
                        # Ask if the user wants to install the model
                        install_now = questionary.confirm("Do you want to install this model now?", default=True).ask()
                        if install_now:
                            models.install_model(selected_model)
        
        elif args[0] == "search-ollama":
            # Search for models on Ollama
            query = questionary.text("Enter search term for ollama models:").ask()
            if not query:
                print("Search cancelled.")
                continue
                
            print(f"Searching for models matching '{query}'...")
            
            # Get the OllamaModelManager instance
            from getllm.models.ollama import OllamaModelManager
            from getllm.models import search_huggingface_models
            
            ollama_manager = OllamaModelManager()
            
            # Search for models in both Ollama and Hugging Face
            logger.debug(f'Searching for Ollama models matching query: {query}')
            ollama_models = ollama_manager.search_models(query=query, limit=20)
            logger.debug(f'Found {len(ollama_models)} Ollama models matching query')
            
            if not ollama_models:
                logger.debug(f'No Ollama models found, searching Hugging Face for query: {query}')
                hf_models = search_huggingface_models(query=query, limit=20)
                logger.debug(f'Found {len(hf_models)} Hugging Face models matching query')
            else:
                hf_models = []
            
            if not ollama_models and not hf_models:
                print(f"No models found matching '{query}' in either Ollama library or Hugging Face.")
                continue
                
            # Create choices for the questionary select
            choices = []
            
            # Add Ollama models first
            if ollama_models:
                choices.append(questionary.Separator("--- Ollama Models ---"))
                for model in ollama_models:
                    model_name = model.get('name', 'Unknown')
                    model_size = model.get('size', model.get('size_b', ''))
                    model_desc = model.get('description', model.get('desc', 'No description'))
                    choices.append(questionary.Choice(
                        title=f"{model_name:<30} {str(model_size):<10} {model_desc}",
                        value=model_name
                    ))
            
            # Add Hugging Face models if no Ollama models were found
            if not ollama_models and hf_models:
                choices.append(questionary.Separator("--- Hugging Face GGUF Models ---"))
                for model in hf_models:
                    model_id = model.get('id', model.get('name', 'Unknown'))
                    model_size = model.get('size', '')
                    model_desc = model.get('description', model.get('desc', 'No description'))
                    choices.append(questionary.Choice(
                        title=f"{model_id:<30} {str(model_size):<10} [HuggingFace] {model_desc}",
                        value=model_id
                    ))
            
            # Add a cancel option
            choices.append(questionary.Separator("-" * 50))
            choices.append(questionary.Choice(title="Cancel", value="__CANCEL__"))
            
            # Ask the user to select a model
            selected_model = questionary.select(
                "Select a model to install:",
                choices=choices
            ).ask()
            
            # Handle the user's selection
            if selected_model and selected_model != "__CANCEL__":
                install_now = questionary.confirm(
                    f"Do you want to install '{selected_model}' now?", 
                    default=True
                ).ask()
                if install_now:
                    models.install_model(selected_model)
        elif args[0] == "update-hf":
            # Update models from Hugging Face
            print("Updating models from Hugging Face...")
            try:
                logger.debug('Starting update of Hugging Face models')
                # First update the cache
                cache_updated = update_huggingface_models_cache()
                logger.debug(f'Cache update result: {cache_updated}')
                
                # Then update the models list using the function from models.py
                from getllm.models import update_models_metadata
                success = update_models_metadata()
                
                if success:
                    logger.info('Successfully updated models from Hugging Face')
                    print("Successfully updated models from Hugging Face.")
                else:
                    logger.error('Failed to update models from Hugging Face')
                    print("Error updating models from Hugging Face. Check logs for details.")
            except Exception as e:
                logger.error(f'Error during Hugging Face models update: {e}', exc_info=True)
                print(f"Error updating models from Hugging Face: {e}")
                print("Check logs for more details or run with --debug flag for verbose output.")
        elif args[0] == "generate":
            generate_code_interactive(mock_mode=mock_mode)
        else:
            print("Unknown command. Available: list, install <model>, installed, set-default <model>, default, update, update-hf, test, wybierz-model, search-hf, wybierz-default, generate, exit")

if __name__ == "__main__":
    # Check if mock mode is requested
    mock_mode = "--mock" in sys.argv
    interactive_shell(mock_mode=mock_mode)
