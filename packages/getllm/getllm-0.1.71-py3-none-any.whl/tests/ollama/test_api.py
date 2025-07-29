"""
Tests for the Ollama API module.
"""
import pytest
from unittest.mock import patch, MagicMock
from getllm.ollama.api import (
    get_ollama_integration,
    start_ollama_server,
    query_ollama,
    chat_ollama,
    list_ollama_models,
    install_ollama_model,
    get_global_server,
    ensure_global_server,
    close_global_server,
)
from getllm.ollama.server import OllamaServer
from getllm.ollama.exceptions import OllamaError, ModelNotFoundError

class TestOllamaAPI:
    """Test the Ollama API functions."""
    
    def test_get_ollama_integration(self):
        """Test getting an Ollama integration instance."""
        server = get_ollama_integration("test-model")
        assert isinstance(server, OllamaServer)
        assert server.model == "test-model"
    
    def test_start_ollama_server_success(self):
        """Test starting the Ollama server successfully."""
        with patch('getllm.ollama.server.OllamaServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.start.return_value = True
            mock_server_class.return_value = mock_server
            
            server = start_ollama_server()
            
            assert server is not None
            mock_server.start.assert_called_once()
    
    def test_start_ollama_server_failure(self):
        """Test handling server start failure."""
        with patch('getllm.ollama.server.OllamaServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.start.return_value = False
            mock_server_class.return_value = mock_server
            
            with pytest.raises(OllamaError, match="Failed to start Ollama server"):
                start_ollama_server()
    
    def test_query_ollama_success(self):
        """Test querying the Ollama API successfully."""
        with patch('getllm.ollama.api.OllamaServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.query.return_value = "Test response"
            mock_server_class.return_value = mock_server
            
            response = query_ollama("Test prompt", "test-model")
            
            assert response == "Test response"
            mock_server.query.assert_called_once_with(
                "Test prompt", 
                model="test-model",
                template_type=None
            )
    
    def test_chat_ollama_success(self):
        """Test chat interaction with the Ollama API."""
        with patch('getllm.ollama.api.OllamaServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.chat.return_value = "Chat response"
            mock_server_class.return_value = mock_server
            
            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
            
            response = chat_ollama(messages, "test-model", temperature=0.7)
            
            assert response == "Chat response"
            mock_server.chat.assert_called_once_with(
                messages,
                model="test-model",
                temperature=0.7
            )
    
    def test_list_ollama_models_success(self):
        """Test listing Ollama models successfully."""
        mock_models = [
            {"name": "codellama:7b", "size": 3823},
            {"name": "phi3:latest", "size": 2048}
        ]
        
        with patch('getllm.ollama.api.OllamaServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.model_manager.list_installed_models.return_value = mock_models
            mock_server_class.return_value = mock_server
            
            models = list_ollama_models()
            
            assert models == mock_models
            mock_server.model_manager.list_installed_models.assert_called_once()
    
    def test_install_ollama_model_success(self):
        """Test installing an Ollama model successfully."""
        with patch('getllm.ollama.api.OllamaServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.model_manager.install_model.return_value = True
            mock_server_class.return_value = mock_server
            
            result = install_ollama_model("codellama:7b")
            
            assert result is True
            mock_server.model_manager.install_model.assert_called_once_with("codellama:7b")
    
    def test_install_ollama_model_not_found(self):
        """Test handling model not found during installation."""
        with patch('getllm.ollama.api.OllamaServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.model_manager.install_model.side_effect = ModelNotFoundError("Model not found")
            mock_server_class.return_value = mock_server
            
            with pytest.raises(ModelNotFoundError, match="Model not found"):
                install_ollama_model("nonexistent-model")
    
    def test_global_server_management(self):
        """Test global server management functions."""
        # Clear any existing global server
        close_global_server()
        
        # First call should create a new server
        with patch('getllm.ollama.server.OllamaServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.is_running.return_value = True
            mock_server.start.return_value = True
            mock_server_class.return_value = mock_server
            
            server1 = get_global_server()
            assert server1 is not None
            mock_server_class.assert_called_once()
            
            # Subsequent calls should return the same instance
            server2 = get_global_server()
            assert server1 is server2
            
            # ensure_global_server should also return the same instance
            server3 = ensure_global_server()
            assert server1 is server3
            
            # close_global_server should clear the instance
            close_global_server()
            
            # Next get_global_server should create a new instance
            with patch('getllm.ollama.server.OllamaServer') as new_mock_server_class:
                new_mock_server = MagicMock()
                new_mock_server.is_running.return_value = True
                new_mock_server.start.return_value = True
                new_mock_server_class.return_value = new_mock_server
                
                new_server = get_global_server()
                assert new_server is not None
                assert new_server is not server1
                new_mock_server_class.assert_called_once()
    
    def test_ensure_global_server_failure(self):
        """Test handling server start failure in ensure_global_server."""
        close_global_server()
        
        with patch('getllm.ollama.server.OllamaServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.is_running.return_value = False
            mock_server.start.return_value = False
            mock_server_class.return_value = mock_server
            
            with pytest.raises(OllamaError, match="Failed to start global Ollama server"):
                ensure_global_server()
