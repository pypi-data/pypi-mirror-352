"""
Constants and default values for the models module.
"""

# Default models that come pre-configured with the package
DEFAULT_MODELS = [
    {"name": "tinyllama:1.1b", "size": "1.1B", "desc": "TinyLlama 1.1B - fast, small model"},
    {"name": "codellama:7b", "size": "7B", "desc": "CodeLlama 7B - coding, Meta"},
    {"name": "wizardcoder:7b-python", "size": "7B", "desc": "WizardCoder 7B Python"},
    {"name": "deepseek-coder:6.7b", "size": "6.7B", "desc": "DeepSeek Coder 6.7B"},
    {"name": "mistral:7b", "size": "7B", "desc": "Mistral 7B"},
    {"name": "llama2:7b", "size": "7B", "desc": "Llama 2 7B"},
    {"name": "llama2:13b", "size": "13B", "desc": "Llama 2 13B"}
]

# Hardcoded list of popular Hugging Face GGUF models
DEFAULT_HF_MODELS = [
    {
        'id': 'TheBloke/Llama-2-7B-Chat-GGUF',
        'name': 'Llama-2-7B-Chat',
        'size': '7B',
        'description': 'Llama 2 7B Chat model from Meta, quantized to GGUF format',
        'downloads': 1000000,
        'likes': 5000,
        'tags': ['llama', 'chat', 'gguf', '7b']
    },
    {
        'id': 'TheBloke/Mistral-7B-Instruct-v0.1-GGUF',
        'name': 'Mistral-7B-Instruct',
        'size': '7B',
        'description': 'Mistral 7B Instruct model, quantized to GGUF format',
        'downloads': 800000,
        'likes': 4500,
        'tags': ['mistral', 'instruct', 'gguf', '7b']
    },
    # Add more default models as needed
]

# Cache file names
HF_MODELS_CACHE = 'hf_models.json'
OLLAMA_MODELS_CACHE = 'ollama_models.json'
MODELS_METADATA = 'models_metadata.json'

# Default paths
def get_models_dir():
    """Get the path to the models directory."""
    import os
    return os.path.join(os.path.expanduser('~'), '.getllm', 'models')

def get_hf_models_cache_path():
    """Get the path to the Hugging Face models cache file."""
    return os.path.join(get_models_dir(), HF_MODELS_CACHE)

def get_ollama_models_cache_path():
    """Get the path to the Ollama models cache file."""
    return os.path.join(get_models_dir(), OLLAMA_MODELS_CACHE)

def get_models_metadata_path():
    """Get the path to the models metadata file."""
    return os.path.join(get_models_dir(), MODELS_METADATA)
