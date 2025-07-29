"""
Tests for the Ollama server module.
"""
import pytest
from unittest.mock import patch, MagicMock, call
from getllm.ollama.server import OllamaServer
from getllm.ollama.exceptions import ServerError, InstallationError

class TestOllamaServer:
    """Test the OllamaServer class."""
    
    @pytest.fixture
    def server(self):
        """Create a server instance for testing."""
        return OllamaServer()
    
    def test_check_ollama_installed_true(self, server, mock_subprocess):
        """Test checking if Ollama is installed (true case)."""
        assert server._check_ollama_installed() is True
    
    def test_check_ollama_installed_false(self, server):
        """Test checking if Ollama is installed (false case)."""
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            assert server._check_ollama_installed() is False
    
    def test_is_running_true(self, server, mock_ollama_running):
        """Test checking if the server is running (true case)."""
        assert server.is_running() is True
    
    def test_is_running_false(self, server, mock_ollama_not_running):
        """Test checking if the server is running (false case)."""
        assert server.is_running() is False
    
    def test_start_already_running(self, server, mock_ollama_running):
        """Test starting the server when it's already running."""
        assert server.start() is True
    
    def test_start_success(self, server, mock_ollama_not_running, mock_subprocess):
        """Test starting the server successfully."""
        with patch.object(server, '_check_ollama_installed', return_value=True):
            # First call to is_running returns False, subsequent calls return True
            with patch.object(server, 'is_running', side_effect=[False, True]):
                assert server.start() is True
                mock_subprocess['Popen'].assert_called_once()
    
    def test_start_install_required(self, server, mock_ollama_not_running, mock_subprocess):
        """Test starting the server when Ollama needs to be installed."""
        with patch.object(server, '_check_ollama_installed', side_effect=[False, True]), \
             patch('getllm.ollama.install.OllamaInstaller') as mock_installer:
            
            mock_installer.return_value.install.return_value = True
            
            # First call to is_running returns False, subsequent calls return True
            with patch.object(server, 'is_running', side_effect=[False, True]):
                assert server.start() is True
                mock_installer.return_value.install.assert_called_once()
    
    def test_start_install_failed(self, server, mock_ollama_not_running):
        """Test starting the server when Ollama installation fails."""
        with patch.object(server, '_check_ollama_installed', return_value=False), \
             patch('getllm.ollama.install.OllamaInstaller') as mock_installer:
            
            mock_installer.return_value.install.return_value = False
            
            assert server.start() is False
    
    def test_stop_running_process(self, server):
        """Test stopping a running server process."""
        # Create a mock process
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        server.ollama_process = mock_process
        
        server.stop()
        
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once_with(timeout=10)
    
    def test_stop_already_stopped(self, server):
        """Test stopping when no process is running."""
        server.ollama_process = None
        server.stop()  # Should not raise an exception
    
    def test_ensure_model_available_installed(self, server):
        """Test ensuring a model is available when it's already installed."""
        with patch.object(server.model_manager, 'is_model_installed', return_value=True):
            assert server.ensure_model_available('codellama:7b') is True
    
    def test_ensure_model_available_install_success(self, server):
        """Test ensuring a model is available with successful installation."""
        with patch.object(server.model_manager, 'is_model_installed', return_value=False), \
             patch.object(server.model_manager, 'install_model', return_value=True):
            assert server.ensure_model_available('codellama:7b') is True
    
    def test_ensure_model_available_install_failed(self, server):
        """Test ensuring a model is available when installation fails."""
        with patch.object(server.model_manager, 'is_model_installed', return_value=False), \
             patch.object(server.model_manager, 'install_model', side_effect=Exception("Install failed")):
            assert server.ensure_model_available('codellama:7b') is False
    
    def test_query_success(self, server, mock_requests):
        """Test querying the server successfully."""
        # Mock the server response
        mock_response = {'response': 'This is a test response'}
        mock_requests['post'].return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value=mock_response)
        )
        
        # Mock the server methods
        with patch.object(server, 'is_running', return_value=True), \
             patch.object(server, 'ensure_model_available', return_value=True):
            
            response = server.query("Test prompt")
            
            assert response == 'This is a test response'
            mock_requests['post'].assert_called_once()
    
    def test_query_server_not_running(self, server):
        """Test querying when the server is not running and cannot be started."""
        with patch.object(server, 'is_running', return_value=False), \
             patch.object(server, 'start', return_value=False):
            
            with pytest.raises(ServerError, match="Failed to start Ollama server"):
                server.query("Test prompt")
    
    def test_query_model_not_available(self, server):
        """Test querying when the model is not available."""
        with patch.object(server, 'is_running', return_value=True), \
             patch.object(server, 'ensure_model_available', return_value=False):
            
            with pytest.raises(ServerError, match="Failed to ensure model"):
                server.query("Test prompt")
    
    def test_chat_success(self, server, mock_requests):
        """Test chat interaction with the server."""
        # Mock the server response
        mock_response = {
            'message': {
                'role': 'assistant',
                'content': 'This is a test response'
            }
        }
        mock_requests['post'].return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value=mock_response)
        )
        
        # Mock the server methods
        with patch.object(server, 'is_running', return_value=True), \
             patch.object(server, 'ensure_model_available', return_value=True):
            
            messages = [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'},
                {'role': 'user', 'content': 'How are you?'}
            ]
            
            response = server.chat(messages)
            
            assert response == 'This is a test response'
            mock_requests['post'].assert_called_once()
    
    def test_context_manager(self):
        """Test using the server as a context manager."""
        with patch('getllm.ollama.server.OllamaServer.start') as mock_start, \
             patch('getllm.ollama.server.OllamaServer.stop') as mock_stop:
            
            with OllamaServer() as server:
                assert server is not None
                mock_start.assert_called_once()
            
            mock_stop.assert_called_once()
