"""
Tests for the HuggingFaceModelManager class.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from getllm.models.huggingface import HuggingFaceModelManager


class TestHuggingFaceModelManager:
    """Test cases for HuggingFaceModelManager."""

    def test_get_available_models_from_cache(self, mock_huggingface_models, temp_models_dir):
        """Test getting available models from cache."""
        # Create a test cache file
        cache_file = temp_models_dir / "huggingface_models.json"
        with open(cache_file, 'w') as f:
            json.dump(mock_huggingface_models["models"], f)
        
        manager = HuggingFaceModelManager()
        manager.cache_file = cache_file
        
        models = manager.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert models[0]["id"] == "TheBloke/Llama-2-7B-Chat-GGUF"
    
    def test_get_available_models_default(self, temp_models_dir):
        """Test getting default models when cache is empty."""
        manager = HuggingFaceModelManager()
        manager.cache_file = temp_models_dir / "nonexistent.json"
        
        models = manager.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert models[0]["source"] == "huggingface"
    
    def test_install_model(self):
        """Test installing a model (placeholder implementation)."""
        manager = HuggingFaceModelManager()
        
        # This is a placeholder test since the actual implementation is not complete
        result = manager.install_model("test/model")
        
        assert result is False  # As per current implementation
    
    def test_list_installed_models(self):
        """Test listing installed models (placeholder implementation)."""
        manager = HuggingFaceModelManager()
        
        # This is a placeholder test since the actual implementation is not complete
        models = manager.list_installed_models()
        
        assert isinstance(models, list)
    
    def test_search_models(self, mock_huggingface_models):
        """Test searching for models."""
        manager = HuggingFaceModelManager()
        
        # Mock the get_available_models method
        with patch.object(manager, 'get_available_models', 
                         return_value=mock_huggingface_models["models"]):
            # Test search with a query
            models = manager.search_models("llama")
            assert len(models) > 0
            assert "llama" in models[0]["id"].lower() or "llama" in models[0]["name"].lower()
            
            # Test search with no query
            models = manager.search_models()
            assert len(models) > 0
    
    def test_get_model_info_found(self, mock_huggingface_models):
        """Test getting model information when the model is found."""
        manager = HuggingFaceModelManager()
        
        # Mock the get_available_models method
        with patch.object(manager, 'get_available_models', 
                         return_value=mock_huggingface_models["models"]):
            model_info = manager.get_model_info("TheBloke/Llama-2-7B-Chat-GGUF")
            
            assert model_info is not None
            assert model_info["id"] == "TheBloke/Llama-2-7B-Chat-GGUF"
    
    def test_get_model_info_not_found(self, mock_huggingface_models):
        """Test getting model information when the model is not found."""
        manager = HuggingFaceModelManager()
        
        # Mock the get_available_models method
        with patch.object(manager, 'get_available_models', 
                         return_value=mock_huggingface_models["models"]):
            model_info = manager.get_model_info("nonexistent/model")
            
            assert model_info is None
    
    def test_update_models_cache(self, mock_huggingface_models, temp_models_dir):
        """Test updating the models cache."""
        manager = HuggingFaceModelManager()
        manager.cache_file = temp_models_dir / "huggingface_models.json"
        
        # Mock the HuggingFaceService
        with patch('getllm.models.huggingface.HuggingFaceService') as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.search_models.return_value = mock_huggingface_models["models"]
            mock_instance.update_models_cache.return_value = True
            
            result = manager.update_models_cache()
            
            assert result is True
            assert manager.cache_file.exists()
            
            # Verify the cache file content
            with open(manager.cache_file, 'r') as f:
                cached_models = json.load(f)
                assert isinstance(cached_models, list)
                assert len(cached_models) > 0
                assert cached_models[0]["id"] == "TheBloke/Llama-2-7B-Chat-GGUF"
