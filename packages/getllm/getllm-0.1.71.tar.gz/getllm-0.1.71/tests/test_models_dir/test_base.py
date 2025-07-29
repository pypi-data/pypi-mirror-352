"""
Tests for the base model manager classes.
"""
import pytest
from unittest.mock import MagicMock, patch

from getllm.models.base import BaseModelManager, ModelManager


class TestBaseModelManager:
    """Test cases for BaseModelManager."""
    
    def test_base_model_manager_abstract_methods(self):
        """Test that BaseModelManager is abstract and can't be instantiated directly."""
        with pytest.raises(TypeError):
            BaseModelManager()
    
    def test_base_model_manager_methods_are_abstract(self):
        """Test that required methods are abstract."""
        assert 'get_available_models' in BaseModelManager.__abstractmethods__
        assert 'install_model' in BaseModelManager.__abstractmethods__
        assert 'list_installed_models' in BaseModelManager.__abstractmethods__


class TestModelManager:
    """Test cases for ModelManager."""
    
    def test_model_manager_initialization(self, mock_huggingface_models, mock_ollama_models):
        """Test that ModelManager initializes correctly."""
        with patch('getllm.models.huggingface.HuggingFaceModelManager') as mock_hf, \
             patch('getllm.models.ollama.OllamaModelManager') as mock_ollama:
            
            # Set up mock return values
            mock_hf.return_value.get_available_models.return_value = mock_huggingface_models["models"]
            mock_ollama.return_value.get_available_models.return_value = mock_ollama_models["models"]
            
            # Initialize the manager
            manager = ModelManager()
            
            # Verify the managers were initialized
            assert hasattr(manager, 'hf_manager')
            assert hasattr(manager, 'ollama_manager')
            
            # Verify the models were loaded
            assert len(manager.models) > 0
    
    def test_get_available_models(self, mock_huggingface_models, mock_ollama_models):
        """Test getting available models from all sources."""
        with patch('getllm.models.huggingface.HuggingFaceModelManager') as mock_hf, \
             patch('getllm.models.ollama.OllamaModelManager') as mock_ollama:
            
            # Set up mock return values
            mock_hf.return_value.get_available_models.return_value = mock_huggingface_models["models"]
            mock_ollama.return_value.get_available_models.return_value = mock_ollama_models["models"]
            
            manager = ModelManager()
            models = manager.get_available_models()
            
            # Should return models from both sources
            assert len(models) == len(mock_huggingface_models["models"]) + len(mock_ollama_models["models"])
    
    def test_install_model_success(self):
        """Test installing a model successfully."""
        with patch('getllm.models.huggingface.HuggingFaceModelManager') as mock_hf, \
             patch('getllm.models.ollama.OllamaModelManager') as mock_ollama:
            
            # Set up mock return values
            mock_ollama.return_value.install_model.return_value = True
            mock_hf.return_value.install_model.return_value = False  # Ollama should be tried first
            
            manager = ModelManager()
            result = manager.install_model("llama2")
            
            assert result is True
            mock_ollama.return_value.install_model.assert_called_once_with("llama2")
    
    def test_install_model_fallback_to_hf(self):
        """Test falling back to Hugging Face when Ollama installation fails."""
        with patch('getllm.models.huggingface.HuggingFaceModelManager') as mock_hf, \
             patch('getllm.models.ollama.OllamaModelManager') as mock_ollama:
            
            # Set up mock return values
            mock_ollama.return_value.install_model.return_value = False
            mock_hf.return_value.install_model.return_value = True
            
            manager = ModelManager()
            result = manager.install_model("llama2")
            
            assert result is True
            mock_ollama.return_value.install_model.assert_called_once_with("llama2")
            mock_hf.return_value.install_model.assert_called_once_with("llama2")
    
    def test_list_installed_models(self):
        """Test listing installed models from all sources."""
        with patch('getllm.models.huggingface.HuggingFaceModelManager') as mock_hf, \
             patch('getllm.models.ollama.OllamaModelManager') as mock_ollama:
            
            # Set up mock return values
            mock_ollama.return_value.list_installed_models.return_value = ["llama2"]
            mock_hf.return_value.list_installed_models.return_value = ["hf-model"]
            
            manager = ModelManager()
            installed = manager.list_installed_models()
            
            assert isinstance(installed, list)
            assert len(installed) == 2  # One from each source
            assert "llama2" in installed
            assert "hf-model" in installed
    
    def test_get_model_info(self):
        """Test getting model information."""
        with patch('getllm.models.huggingface.HuggingFaceModelManager') as mock_hf, \
             patch('getllm.models.ollama.OllamaModelManager') as mock_ollama:
            
            # Set up mock return values
            mock_ollama.return_value.get_model_info.return_value = {"name": "llama2", "source": "ollama"}
            mock_hf.return_value.get_model_info.return_value = None
            
            manager = ModelManager()
            info = manager.get_model_info("llama2")
            
            assert info is not None
            assert info["name"] == "llama2"
            mock_ollama.return_value.get_model_info.assert_called_once_with("llama2")
            mock_hf.return_value.get_model_info.assert_not_called()  # Should stop after Ollama finds it
    
    def test_get_model_info_not_found(self):
        """Test getting model information when the model is not found."""
        with patch('getllm.models.huggingface.HuggingFaceModelManager') as mock_hf, \
             patch('getllm.models.ollama.OllamaModelManager') as mock_ollama:
            
            # Set up mock return values
            mock_ollama.return_value.get_model_info.return_value = None
            mock_hf.return_value.get_model_info.return_value = None
            
            manager = ModelManager()
            info = manager.get_model_info("nonexistent-model")
            
            assert info is None
            mock_ollama.return_value.get_model_info.assert_called_once_with("nonexistent-model")
            mock_hf.return_value.get_model_info.assert_called_once_with("nonexistent-model")
