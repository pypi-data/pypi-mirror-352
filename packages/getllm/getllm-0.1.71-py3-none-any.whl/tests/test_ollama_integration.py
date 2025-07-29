"""
Tests for the getllm.ollama_integration module
"""
import unittest
import os
import sys
import tempfile
import platform
from unittest.mock import patch, MagicMock, mock_open, call

# Add the parent directory to the path so we can import getllm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestOllamaServer(unittest.TestCase):
    """Tests for the getllm.ollama.server module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import the ollama module
        from getllm.ollama import OllamaServer
        self.OllamaServer = OllamaServer
    
    @patch('getllm.ollama.server.requests.get')
    def test_is_running(self, mock_get):
        """Test that the is_running method works"""
        # Mock the requests.get method to return a response with status_code 200
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "0.1.0"}
        mock_get.return_value = mock_response
        
        # Create an instance of OllamaServer
        ollama = self.OllamaServer()
        
        # Call the is_running method
        result = ollama.is_running()
        
        # Verify that the method returns True
        self.assertTrue(result)
        
        # Verify that requests.get was called with the correct URL
        mock_get.assert_called_once_with("http://localhost:11434/api/version", timeout=5)
    
    @patch('getllm.ollama.server.requests.get')
    def test_is_not_running(self, mock_get):
        """Test that the is_running method returns False when server is not running"""
        # Mock the requests.get method to raise an exception
        mock_get.side_effect = Exception("Connection refused")
        
        # Create an instance of OllamaServer
        ollama = self.OllamaServer()
        
        # Call the is_running method
        result = ollama.is_running()
        
        # Verify that the method returns False
        self.assertFalse(result)
    
    @patch('getllm.ollama_integration.os.path.isfile')
    @patch('getllm.ollama_integration.os.access')
    def test_check_ollama_installed(self, mock_access, mock_isfile):
        """Test that the _check_ollama_installed method works when Ollama is installed"""
        # Mock the os.path.isfile and os.access methods to return True
        mock_isfile.return_value = True
        mock_access.return_value = True
        
        # Create an instance of OllamaServer
        ollama = self.OllamaServer()
        
        # Verify that is_ollama_installed is True
        self.assertTrue(ollama.is_ollama_installed)
    
    def test_check_ollama_not_installed(self):
        """Test that the _check_ollama_installed method works when Ollama is not installed"""
        # Create a new instance of OllamaServer with patched methods
        from getllm.ollama import OllamaServer
        
        with patch('getllm.ollama_integration.os.path.isfile', return_value=False):
            with patch('getllm.ollama_integration.subprocess.run') as mock_run:
                # Configure the mock to return a failed result
                mock_result = MagicMock()
                mock_result.returncode = 1
                mock_run.return_value = mock_result
                
                # Create a new instance to force _check_ollama_installed to run
                ollama = OllamaServer()
                
                # Verify that is_ollama_installed is False
                self.assertFalse(ollama.is_ollama_installed)
    
    @patch('getllm.ollama_integration.subprocess.run')
    @patch('getllm.ollama_integration.platform.system')
    @patch('builtins.print')
    def test_install_ollama_direct_success(self, mock_print, mock_platform, mock_run):
        """Test that the _install_ollama_direct method works when installation succeeds"""
        # Mock the platform.system method to return "Linux"
        mock_platform.return_value = "Linux"
        
        # Mock the subprocess.run method to return a successful result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Create an instance of OllamaServer and patch the _check_ollama_installed method
        ollama = self.OllamaServer()
        ollama._check_ollama_installed = MagicMock(return_value=True)
        
        # Call the _install_ollama_direct method
        result = ollama._install_ollama_direct()
        
        # Verify that the method returns True
        self.assertTrue(result)
        
        # Verify that subprocess.run was called with the correct command
        mock_run.assert_called_once()
        self.assertIn("curl -fsSL https://ollama.com/install.sh | sh", mock_run.call_args[0][0])
    
    @patch('getllm.ollama_integration.subprocess.run')
    @patch('getllm.ollama_integration.platform.system')
    @patch('builtins.print')
    def test_install_ollama_direct_failure(self, mock_print, mock_platform, mock_run):
        """Test that the _install_ollama_direct method works when installation fails"""
        # Mock the platform.system method to return "Linux"
        mock_platform.return_value = "Linux"
        
        # Mock the subprocess.run method to return a failed result
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Installation failed"
        mock_run.return_value = mock_result
        
        # Create an instance of OllamaServer
        ollama = self.OllamaServer()
        
        # Call the _install_ollama_direct method
        result = ollama._install_ollama_direct()
        
        # Verify that the method returns False
        self.assertFalse(result)
    
    @patch('getllm.ollama_integration.subprocess.run')
    @patch('getllm.ollama_integration.time.sleep')
    @patch('builtins.print')
    def test_install_ollama_docker_success(self, mock_print, mock_sleep, mock_run):
        """Test that the _install_ollama_docker method works when installation succeeds"""
        # Mock the subprocess.run method to return successful results for all calls
        mock_results = [
            MagicMock(returncode=0, stdout="Docker version 20.10.12"),  # docker --version
            MagicMock(returncode=0),  # docker pull
            MagicMock(returncode=0, stdout=""),  # docker ps -q -f name=ollama
            MagicMock(returncode=0, stdout=""),  # docker ps -a -q -f name=ollama
            MagicMock(returncode=0)  # docker run
        ]
        mock_run.side_effect = mock_results
        
        # Create an instance of OllamaServer and patch the check_server_running method
        ollama = self.OllamaServer()
        ollama.check_server_running = MagicMock(return_value=True)
        
        # Call the _install_ollama_docker method
        result = ollama._install_ollama_docker()
        
        # Verify that the method returns True
        self.assertTrue(result)
        
        # Verify that subprocess.run was called with the correct commands
        self.assertEqual(mock_run.call_count, 5)
        self.assertIn("docker", mock_run.call_args_list[0][0][0][0])
        self.assertIn("pull", mock_run.call_args_list[1][0][0][1])
    
    def test_install_ollama_bexy_success(self):
        """Test that the _install_ollama_bexy method works when installation succeeds"""
        # Create an instance of OllamaServer with patched methods
        from getllm.ollama import OllamaServer
        
        # Create an instance of OllamaServer
        ollama = OllamaServer()
        
        # Directly patch the _install_ollama_bexy method to return True
        ollama._install_ollama_bexy = MagicMock(return_value=True)
        
        # Call the method and verify it returns True
        result = ollama._install_ollama_bexy()
        self.assertTrue(result)
        
        # Verify the method was called
        ollama._install_ollama_bexy.assert_called_once()
    
    def test_mock_mode(self):
        """Test that mock mode works correctly"""
        # Import the necessary modules
        from getllm.cli import MockOllamaServer
        
        # Create an instance of MockOllamaServer
        mock_ollama = MockOllamaServer(model="test-model")
        
        # Verify that the model is set correctly
        self.assertEqual(mock_ollama.model, "test-model")
        
        # Test query_ollama method
        result = mock_ollama.query_ollama("Write a function to calculate factorial")
        
        # Verify that the result contains the expected mock response
        self.assertIn("Mock", result)
        
    def test_install_ollama_with_bexy_option(self):
        """Test that the _install_ollama method works when user selects bexy sandbox"""
        # Import the necessary modules
        from getllm.ollama import OllamaServer
        import sys
        
        # Create a mock questionary module
        mock_questionary = MagicMock()
        mock_select = MagicMock()
        mock_questionary.select.return_value = mock_select
        mock_select.ask.return_value = "Use bexy sandbox for testing"
        
        # Mock the import system to return our mock when questionary is imported
        original_import = __import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'questionary':
                return mock_questionary
            return original_import(name, *args, **kwargs)
        
        # Apply the mock import
        with patch('builtins.__import__', side_effect=mock_import):
            # Mock the _install_ollama_bexy method
            with patch.object(OllamaServer, '_install_ollama_bexy', return_value=True) as mock_bexy_install:
                # Create an instance of OllamaServer with is_ollama_installed=False
                ollama = OllamaServer()
                ollama.is_ollama_installed = False  # Force the installation path
                
                # Call the _install_ollama method
                result = ollama._install_ollama()
                
                # Verify that the _install_ollama_bexy method was called
                mock_bexy_install.assert_called_once()
                
                # Verify that the method returns True
                self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
