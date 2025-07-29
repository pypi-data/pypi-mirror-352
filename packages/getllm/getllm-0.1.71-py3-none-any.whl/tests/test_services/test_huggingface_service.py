"""
Tests for the HuggingFaceService class.
"""
import json
import pytest
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from getllm.services.huggingface_service import HuggingFaceService


class TestHuggingFaceService:
    """Test cases for HuggingFaceService."""

    def test_search_models_no_query(self, mock_huggingface_models):
        """Test searching models without a query."""
        service = HuggingFaceService()
        
        # Mock the API response
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_huggingface_models
            mock_get.return_value = mock_response
            
            models = service.search_models()
            
            assert isinstance(models, list)
            assert len(models) > 0
            assert models[0]["id"] == "TheBloke/Llama-2-7B-Chat-GGUF"
    
    def test_search_models_with_query(self, mock_huggingface_models):
        """Test searching models with a query."""
        service = HuggingFaceService()
        
        # Mock the API response
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_huggingface_models
            mock_get.return_value = mock_response
            
            models = service.search_models(query="llama")
            
            assert isinstance(models, list)
            assert len(models) > 0
            assert "llama" in models[0]["id"].lower() or "llama" in models[0]["name"].lower()
    
    def test_get_model_info_success(self):
        """Test getting model information successfully."""
        service = HuggingFaceService()
        
        # Mock the API response
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "test/model-7b",
                "modelId": "test/model-7b",
                "tags": ["gguf", "llama"],
                "downloads": 1000,
                "lastModified": "2023-01-01T00:00:00.000Z"
            }
            mock_get.return_value = mock_response
            
            model_info = service.get_model_info("test/model-7b")
            
            assert model_info is not None
            assert model_info["id"] == "test/model-7b"
    
    def test_get_model_info_not_found(self):
        """Test getting model information for a non-existent model."""
        service = HuggingFaceService()
        
        # Mock the API response
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            model_info = service.get_model_info("nonexistent/model")
            
            assert model_info is None
    
    def test_update_models_cache_success(self, temp_models_dir):
        """Test updating the models cache successfully."""
        service = HuggingFaceService()
        
        # Mock the API response
        with patch('requests.get') as mock_get, \
             patch('builtins.open', mock_open()) as mock_file:
            
            # Mock the API response with models data
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"modelId": "test/model-1", "downloads": 1000},
                {"modelId": "test/model-2", "downloads": 500}
            ]
            mock_get.return_value = mock_response
            
            result = service.update_models_cache()
            
            assert result is True
            mock_file.assert_called_once()
    
    def test_load_cached_models(self, temp_models_dir):
        """Test loading models from cache."""
        service = HuggingFaceService()
        
        # Create a test cache file
        test_models = [
            {"id": "test/model-1", "downloads": 1000},
            {"id": "test/model-2", "downloads": 500}
        ]
        
        with open(service.cache_file, 'w') as f:
            json.dump(test_models, f)
        
        # Test loading from cache
        models = service._load_cached_models()
        assert isinstance(models, list)
        assert len(models) == 2
        assert models[0]["id"] == "test/model-1"
    
    def test_load_cached_models_invalid_json(self, temp_models_dir):
        """Test loading models from an invalid cache file."""
        service = HuggingFaceService()
        
        # Create an invalid JSON file
        with open(service.cache_file, 'w') as f:
            f.write("invalid json")
        
        # Test loading from invalid cache
        models = service._load_cached_models()
        assert models == []
    
    def test_save_models_to_cache(self, temp_models_dir):
        """Test saving models to cache."""
        service = HuggingFaceService()
        
        test_models = [
            {"id": "test/model-1", "downloads": 1000},
            {"id": "test/model-2", "downloads": 500}
        ]
        
        # Test saving to cache
        result = service._save_models_to_cache(test_models)
        
        assert result is True
        assert service.cache_file.exists()
        
        # Verify the content
        with open(service.cache_file, 'r') as f:
            saved_models = json.load(f)
            assert len(saved_models) == 2
            assert saved_models[0]["id"] == "test/model-1"
