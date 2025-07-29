"""
Pytest fixtures and utilities for getllm tests
"""
import pytest
import os
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List, Optional

# Add the parent directory to the path so we can import getllm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"
MODELS_CACHE_DIR = TEST_DATA_DIR / "models"

# Ensure test data directories exist
TEST_DATA_DIR.mkdir(exist_ok=True)
MODELS_CACHE_DIR.mkdir(exist_ok=True)

# Test model data
TEST_HF_MODEL = {
    "id": "test/model-7b",
    "name": "test-model-7b",
    "size": "7B",
    "description": "Test model for unit testing",
    "source": "huggingface",
    "format": "gguf"
}

TEST_OLLAMA_MODEL = {
    "name": "test-ollama-model",
    "size": "7B",
    "description": "Test Ollama model",
    "source": "ollama",
    "format": "gguf"
}

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Create test data files if they don't exist
    hf_models_file = TEST_DATA_DIR / "huggingface_models.json"
    if not hf_models_file.exists():
        with open(hf_models_file, 'w') as f:
            json.dump({"models": [TEST_HF_MODEL]}, f)
    
    ollama_models_file = TEST_DATA_DIR / "ollama_models.json"
    if not ollama_models_file.exists():
        with open(ollama_models_file, 'w') as f:
            json.dump({"models": [TEST_OLLAMA_MODEL]}, f)

@pytest.fixture
def mock_env_vars(monkeypatch, tmp_path):
    """Fixture to set up environment variables for tests."""
    # Create a temporary models directory
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    
    # Set environment variables
    env_vars = {
        "OLLAMA_PATH": "/usr/local/bin/ollama",
        "OLLAMA_MODEL": "llama2",
        "OLLAMA_FALLBACK_MODELS": "llama2,codellama",
        "OLLAMA_TIMEOUT": "120",
        "MODELS_DIR": str(models_dir),
        "DEFAULT_MODEL": "llama2"
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars

@pytest.fixture
def mock_ollama_response():
    """Fixture to provide a mock response from the Ollama API."""
    return {
        "model": "llama2",
        "created_at": "2023-01-01T00:00:00Z",
        "response": "This is a mock response from the Ollama API.",
        "done": True
    }

@pytest.fixture
def mock_ollama_models():
    """Fixture to provide a list of mock Ollama models."""
    return {
        "models": [
            {"name": "llama2", "size": "7B", "description": "Meta's LLaMA 2"},
            {"name": "codellama", "size": "7B", "description": "Code completion model"},
            {"name": "mistral", "size": "7B", "description": "Mistral AI model"}
        ]
    }

@pytest.fixture
def mock_huggingface_models():
    """Fixture to provide a list of mock Hugging Face models."""
    return {
        "models": [
            {
                "id": "TheBloke/Llama-2-7B-Chat-GGUF",
                "name": "llama-2-7b-chat",
                "size": "7B",
                "description": "Llama 2 7B Chat model in GGUF format"
            },
            {
                "id": "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
                "name": "mistral-7b-instruct",
                "size": "7B",
                "description": "Mistral 7B Instruct model in GGUF format"
            }
        ]
    }

@pytest.fixture
def mock_ollama_service(mock_ollama_models):
    """Fixture to provide a mock OllamaService."""
    with patch('getllm.services.ollama_service.OllamaService') as mock:
        instance = mock.return_value
        instance.list_models.return_value = mock_ollama_models["models"]
        instance.get_model_info.return_value = mock_ollama_models["models"][0]
        instance.list_installed_models.return_value = ["llama2"]
        instance.pull_model.return_value = True
        yield instance

@pytest.fixture
def mock_huggingface_service(mock_huggingface_models):
    """Fixture to provide a mock HuggingFaceService."""
    with patch('getllm.services.huggingface_service.HuggingFaceService') as mock:
        instance = mock.return_value
        instance.search_models.return_value = mock_huggingface_models["models"]
        instance.get_model_info.return_value = mock_huggingface_models["models"][0]
        instance.update_models_cache.return_value = True
        yield instance

@pytest.fixture
def temp_models_dir(tmp_path):
    """Fixture to provide a temporary models directory."""
    return tmp_path / "models"

@pytest.fixture
def test_models_metadata():
    """Fixture to provide test models metadata."""
    return {
        "llama2": {
            "name": "llama2",
            "source": "ollama",
            "installed": True,
            "last_used": "2023-01-01T00:00:00Z"
        },
        "TheBloke/Llama-2-7B-Chat-GGUF": {
            "name": "llama-2-7b-chat",
            "source": "huggingface",
            "installed": False,
            "last_used": None
        }
    }
