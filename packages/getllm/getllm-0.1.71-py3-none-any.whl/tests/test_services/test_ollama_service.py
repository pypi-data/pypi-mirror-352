"""
Tests for the OllamaService class.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from getllm.services.ollama_service import OllamaService


class TestOllamaService:
    """Test cases for OllamaService."""

    def test_list_models(self, mock_ollama_models):
        """Test listing available models."""
        service = OllamaService()
        
        # Mock subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_ollama_models["models"])
        
        with patch('subprocess.run', return_value=mock_result) as mock_run:
            models = service.list_models()
            
            assert isinstance(models, list)
            assert len(models) > 0
            assert models[0]["name"] == "llama2"
            mock_run.assert_called_once()
    
    def test_get_model_info(self):
        """Test getting model information."""
        service = OllamaService()
        
        # Mock subprocess.run for model info
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "name": "llama2",
            "size": "7B",
            "description": "Meta's LLaMA 2"
        })
        
        with patch('subprocess.run', return_value=mock_result) as mock_run:
            model_info = service.get_model_info("llama2")
            
            assert model_info is not None
            assert model_info["name"] == "llama2"
            mock_run.assert_called_once()
    
    def test_pull_model_success(self):
        """Test successfully pulling a model."""
        service = OllamaService()
        
        # Mock successful subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            result = service.pull_model("llama2")
            assert result is True
    
    def test_pull_model_failure(self):
        """Test failing to pull a model."""
        service = OllamaService()
        
        # Mock failed subprocess.run
        with patch('subprocess.run', side_effect=Exception("Pull failed")):
            result = service.pull_model("nonexistent-model")
            assert result is False
    
    def test_list_installed_models(self):
        """Test listing installed models."""
        service = OllamaService()
        
        # Mock subprocess.run for list command
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps([
            {"name": "llama2"},
            {"name": "codellama"}
        ])
        
        with patch('subprocess.run', return_value=mock_result) as mock_run:
            models = service.list_installed_models()
            
            assert isinstance(models, list)
            assert len(models) == 2
            assert "llama2" in models
            mock_run.assert_called_once()
    
    def test_update_models_cache(self, temp_models_dir):
        """Test updating the models cache."""
        service = OllamaService()
        
        # Mock subprocess.run for list --all command
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps([
            {"name": "llama2"},
            {"name": "codellama"}
        ])
        
        with patch('subprocess.run', return_value=mock_result):
            result = service.update_models_cache()
            
            assert result is True
            cache_file = service.cache_file
            assert cache_file.exists()
            
            # Verify cache file content
            with open(cache_file, 'r') as f:
                cached_models = json.load(f)
                assert isinstance(cached_models, list)
                assert len(cached_models) == 2
    
    def test_load_cached_models(self, temp_models_dir):
        """Test loading models from cache."""
        service = OllamaService()
        
        # Create a test cache file
        test_models = [
            {"name": "cached-model-1", "size": "7B"},
            {"name": "cached-model-2", "size": "13B"}
        ]
        
        with open(service.cache_file, 'w') as f:
            json.dump(test_models, f)
        
        # Test loading from cache
        models = service._load_cached_models()
        assert isinstance(models, list)
        assert len(models) == 2
        assert models[0]["name"] == "cached-model-1"
