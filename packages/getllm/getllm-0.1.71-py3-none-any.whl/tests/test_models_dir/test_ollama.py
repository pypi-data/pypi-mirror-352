"""
Tests for the OllamaModelManager class.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from getllm.models.ollama import OllamaModelManager


class TestOllamaModelManager:
    """Test cases for OllamaModelManager."""

    def test_get_available_models_from_cache(self, mock_ollama_models, temp_models_dir):
        """Test getting available models from cache."""
        # Create a test cache file
        cache_file = temp_models_dir / "ollama_models.json"
        with open(cache_file, 'w') as f:
            json.dump(mock_ollama_models["models"], f)
        
        manager = OllamaModelManager()
        manager.cache_file = cache_file
        
        models = manager.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert models[0]["name"] == "llama2"
    
    def test_get_available_models_default(self, temp_models_dir):
        """Test getting default models when cache is empty."""
        manager = OllamaModelManager()
        manager.cache_file = temp_models_dir / "nonexistent.json"
        
        models = manager.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert models[0]["source"] == "ollama"
    
    def test_install_model_success(self):
        """Test installing a model successfully."""
        manager = OllamaModelManager()
        
        # Mock the OllamaService
        with patch('getllm.models.ollama.OllamaService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.pull_model.return_value = True
            
            result = manager.install_model("llama2")
            
            assert result is True
            mock_instance.pull_model.assert_called_once_with("llama2")
    
    def test_install_model_failure(self):
        """Test failing to install a model."""
        manager = OllamaModelManager()
        
        # Mock the OllamaService
        with patch('getllm.models.ollama.OllamaService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.pull_model.return_value = False
            
            result = manager.install_model("nonexistent-model")
            
            assert result is False
            mock_instance.pull_model.assert_called_once_with("nonexistent-model")
    
    def test_list_installed_models(self):
        """Test listing installed models."""
        manager = OllamaModelManager()
        
        # Mock the OllamaService
        with patch('getllm.models.ollama.OllamaService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.list_installed_models.return_value = ["llama2", "codellama"]
            
            models = manager.list_installed_models()
            
            assert isinstance(models, list)
            assert len(models) == 2
            assert "llama2" in models
            assert "codellama" in models
    
    def test_get_model_info_found(self, mock_ollama_models):
        """Test getting model information when the model is found."""
        manager = OllamaModelManager()
        
        # Mock the get_available_models method
        with patch.object(manager, 'get_available_models', 
                         return_value=mock_ollama_models["models"]):
            model_info = manager.get_model_info("llama2")
            
            assert model_info is not None
            assert model_info["name"] == "llama2"
    
    def test_get_model_info_not_found(self, mock_ollama_models):
        """Test getting model information when the model is not found."""
        manager = OllamaModelManager()
        
        # Mock the get_available_models method
        with patch.object(manager, 'get_available_models', 
                         return_value=mock_ollama_models["models"]):
            model_info = manager.get_model_info("nonexistent-model")
            
            assert model_info is None
    
    def test_update_models_cache(self, mock_ollama_models, temp_models_dir):
        """Test updating the models cache."""
        manager = OllamaModelManager()
        manager.cache_file = temp_models_dir / "ollama_models.json"
        
        # Mock the OllamaService
        with patch('getllm.models.ollama.OllamaService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.list_models.return_value = mock_ollama_models["models"]
            mock_instance.update_models_cache.return_value = True
            
            result = manager.update_models_cache()
            
            assert result is True
            assert manager.cache_file.exists()
            
            # Verify the cache file content
            with open(manager.cache_file, 'r') as f:
                cached_models = json.load(f)
                assert isinstance(cached_models, list)
                assert len(cached_models) > 0
                assert cached_models[0]["name"] == "llama2"
