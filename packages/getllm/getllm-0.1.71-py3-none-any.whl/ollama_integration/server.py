"""
Ollama server management.
"""

import os
import sys
import time
import logging
import subprocess
import threading
from typing import Optional, Dict, Any, List, Union
import requests

from .exceptions import (
    OllamaError,
    OllamaInstallationError,
    OllamaStartupError,
    ModelError,
    ModelGenerationError
)

logger = logging.getLogger('getllm.ollama.server')

class OllamaServer:
    """Manages the Ollama server process and API interactions."""
    
    def __init__(self, ollama_path: Optional[str] = None, model: Optional[str] = None):
        """Initialize the Ollama server manager.
        
        Args:
            ollama_path: Path to the Ollama executable
            model: Default model to use
        """
        self.ollama_path = ollama_path or os.getenv('OLLAMA_PATH', 'ollama')
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3')
        self.fallback_models = os.getenv(
            'OLLAMA_FALLBACK_MODELS', 
            'llama3,llama-2-7b-chat,phi3,tinyllama'
        ).split(',')
        
        # API endpoints
        self.base_api_url = "http://localhost:11434/api"
        self.generate_api_url = f"{self.base_api_url}/generate"
        self.chat_api_url = f"{self.base_api_url}/chat"
        self.version_api_url = f"{self.base_api_url}/version"
        
        # Process management
        self.ollama_process = None
        self.original_model_specified = model is not None
        
        # Check if Ollama is installed
        self.is_ollama_installed = self._check_ollama_installed()
    
    def _check_ollama_installed(self) -> bool:
        """Check if Ollama is installed on the system.
        
        Returns:
            bool: True if Ollama is installed, False otherwise
        """
        try:
            result = subprocess.run(
                [self.ollama_path, '--version'],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def is_running(self) -> bool:
        """Check if the Ollama server is running.
        
        Returns:
            bool: True if the server is running, False otherwise
        """
        try:
            response = requests.get(self.version_api_url, timeout=5)
            return response.status_code == 200
        except (requests.RequestException, ConnectionError):
            return False
    
    def start(self) -> bool:
        """Start the Ollama server.
        
        Returns:
            bool: True if the server was started successfully, False otherwise
            
        Raises:
            OllamaInstallationError: If Ollama is not installed
            OllamaStartupError: If the server fails to start
        """
        if not self.is_ollama_installed:
            raise OllamaInstallationError("Ollama is not installed on this system")
        
        if self.is_running():
            logger.info("Ollama server is already running")
            return True
            
        try:
            # Start Ollama in a separate process
            self.ollama_process = subprocess.Popen(
                [self.ollama_path, 'serve'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for the server to start
            max_attempts = 30
            for _ in range(max_attempts):
                if self.is_running():
                    logger.info("Ollama server started successfully")
                    return True
                time.sleep(1)
            
            # If we get here, the server didn't start
            error_msg = "Timed out waiting for Ollama server to start"
            if self.ollama_process.stderr:
                error_msg += f": {self.ollama_process.stderr.read()}"
            raise OllamaStartupError(error_msg)
            
        except subprocess.SubprocessError as e:
            error_msg = f"Failed to start Ollama server: {e}"
            logger.error(error_msg)
            raise OllamaStartupError(error_msg) from e
    
    def stop(self) -> bool:
        """Stop the Ollama server if it was started by this instance.
        
        Returns:
            bool: True if the server was stopped successfully, False otherwise
        """
        if self.ollama_process:
            try:
                self.ollama_process.terminate()
                self.ollama_process.wait(timeout=10)
                self.ollama_process = None
                logger.info("Ollama server stopped")
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
                logger.error(f"Error stopping Ollama server: {e}")
                try:
                    self.ollama_process.kill()
                except Exception as kill_error:
                    logger.error(f"Error killing Ollama process: {kill_error}")
                self.ollama_process = None
                return False
        return True
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        **generation_params
    ) -> str:
        """Generate text using the specified model.
        
        Args:
            prompt: The prompt to generate text from
            model: The model to use (defaults to the server's default model)
            **generation_params: Additional parameters for text generation
            
        Returns:
            The generated text
            
        Raises:
            ModelGenerationError: If there's an error generating text
        """
        model = model or self.model
        
        try:
            response = requests.post(
                self.generate_api_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    **generation_params
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get('response', '')
            
        except requests.RequestException as e:
            error_msg = f"Error generating text with model {model}: {e}"
            logger.error(error_msg)
            raise ModelGenerationError(error_msg) from e
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **generation_params
    ) -> str:
        """Generate a chat response using the specified model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: The model to use (defaults to the server's default model)
            **generation_params: Additional parameters for text generation
            
        Returns:
            The generated chat response
            
        Raises:
            ModelGenerationError: If there's an error generating the response
        """
        model = model or self.model
        
        try:
            response = requests.post(
                self.chat_api_url,
                json={
                    "model": model,
                    "messages": messages,
                    **generation_params
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get('message', {}).get('content', '')
            
        except requests.RequestException as e:
            error_msg = f"Error in chat with model {model}: {e}"
            logger.error(error_msg)
            raise ModelGenerationError(error_msg) from e
    
    def get_version(self) -> str:
        """Get the version of the running Ollama server.
        
        Returns:
            The version string
            
        Raises:
            OllamaError: If there's an error getting the version
        """
        try:
            response = requests.get(self.version_api_url, timeout=5)
            response.raise_for_status()
            return response.json().get('version', 'unknown')
        except requests.RequestException as e:
            error_msg = f"Error getting Ollama version: {e}"
            logger.error(error_msg)
            raise OllamaError(error_msg) from e
