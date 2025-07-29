"""
Public API functions for Ollama integration.
"""
import os
import logging
from typing import Optional, List, Dict, Any

from .server import OllamaServer
from .exceptions import OllamaError, ModelNotFoundError

logger = logging.getLogger('getllm.ollama.api')

# Global server instance for convenience
_global_server = None

def get_ollama_server(model: str = None) -> OllamaServer:
    """
    Get an OllamaServer instance with the specified model.
    
    Args:
        model: Optional model name to use
        
    Returns:
        An OllamaServer instance
    """
    return OllamaServer(model=model)

# For backward compatibility
get_ollama_integration = get_ollama_server

def start_ollama_server() -> OllamaServer:
    """
    Start the Ollama server and return an OllamaServer instance.
    
    Returns:
        An OllamaServer instance with the server started
    """
    server = OllamaServer()
    if not server.start():
        raise OllamaError("Failed to start Ollama server")
    return server

def query_ollama(
    prompt: str, 
    model: str = None, 
    template_type: str = None,
    **template_args
) -> str:
    """
    Generate a response using Ollama.
    
    Args:
        prompt: The prompt to send to the model
        model: The model to use (defaults to environment variable or default)
        template_type: Type of template to use
        **template_args: Additional template arguments
        
    Returns:
        The generated text
        
    Raises:
        OllamaError: If there's an error generating the response
    """
    with OllamaServer(model=model) as server:
        return server.query(prompt, model=model, template_type=template_type, **template_args)

def chat_ollama(
    messages: List[Dict[str, str]],
    model: str = None,
    **kwargs
) -> str:
    """
    Have a chat conversation with the model.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: The model to use (defaults to environment variable or default)
        **kwargs: Additional parameters for the API call
        
    Returns:
        The model's response
        
    Raises:
        OllamaError: If there's an error during the chat
    """
    with OllamaServer(model=model) as server:
        return server.chat(messages, model=model, **kwargs)

def list_ollama_models() -> List[Dict[str, Any]]:
    """
    List all installed Ollama models.
    
    Returns:
        A list of dictionaries containing model information
        
    Raises:
        OllamaError: If there's an error listing the models
    """
    with OllamaServer() as server:
        return server.model_manager.list_installed_models()

def install_ollama_model(model_name: str) -> bool:
    """
    Install an Ollama model.
    
    Args:
        model_name: Name of the model to install
        
    Returns:
        bool: True if installation was successful
        
    Raises:
        ModelNotFoundError: If the model is not found
        OllamaError: If there's an error installing the model
    """
    with OllamaServer() as server:
        return server.model_manager.install_model(model_name)

def get_global_server() -> OllamaServer:
    """
    Get or create a global Ollama server instance.
    
    Returns:
        The global OllamaServer instance
    """
    global _global_server
    if _global_server is None:
        _global_server = OllamaServer()
        if not _global_server.start():
            raise OllamaError("Failed to start global Ollama server")
    return _global_server

def ensure_global_server() -> OllamaServer:
    """
    Ensure the global Ollama server is running.
    
    Returns:
        The global OllamaServer instance
        
    Raises:
        OllamaError: If the server cannot be started
    """
    server = get_global_server()
    if not server.is_running() and not server.start():
        raise OllamaError("Failed to start global Ollama server")
    return server

def close_global_server() -> None:
    """
    Close the global Ollama server if it's running.
    """
    global _global_server
    if _global_server is not None:
        _global_server.stop()
        _global_server = None
