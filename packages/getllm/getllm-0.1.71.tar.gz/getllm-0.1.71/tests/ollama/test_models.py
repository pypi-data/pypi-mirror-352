"""
Tests for the Ollama models module.
"""
import pytest
from unittest.mock import patch, MagicMock
from getllm.ollama.models import OllamaModelManager
from getllm.ollama.exceptions import ModelNotFoundError, ModelInstallationError, DiskSpaceError

class TestOllamaModelManager:
    """Test the OllamaModelManager class."""
    
    @pytest.fixture
    def model_manager(self):
        """Create a model manager instance for testing."""
        return OllamaModelManager()
    
    def test_list_installed_models_success(self, model_manager, mock_requests):
        """Test listing installed models successfully."""
        mock_response = {'models': [{'name': 'codellama:7b'}, {'name': 'phi3:latest'}]}
        mock_requests['get'].return_value.json.return_value = mock_response
        
        models = model_manager.list_installed_models()
        
        assert len(models) == 2
        assert models[0]['name'] == 'codellama:7b'
        assert models[1]['name'] == 'phi3:latest'
    
    def test_list_installed_models_failure(self, model_manager, mock_requests):
        """Test handling errors when listing models."""
        mock_requests['get'].side_effect = Exception("API error")
        
        with pytest.raises(Exception, match="Error listing Ollama models"):
            model_manager.list_installed_models()
    
    def test_is_model_installed_true(self, model_manager):
        """Test checking if a model is installed (true case)."""
        with patch.object(model_manager, 'list_installed_models') as mock_list:
            mock_list.return_value = [{'name': 'codellama:7b'}, {'name': 'phi3:latest'}]
            
            assert model_manager.is_model_installed('codellama:7b') is True
    
    def test_is_model_installed_false(self, model_manager):
        """Test checking if a model is installed (false case)."""
        with patch.object(model_manager, 'list_installed_models') as mock_list:
            mock_list.return_value = [{'name': 'phi3:latest'}]
            
            assert model_manager.is_model_installed('codellama:7b') is False
    
    def test_install_model_success(self, model_manager, mock_requests, mock_subprocess):
        """Test installing a model successfully."""
        with patch('getllm.ollama.utils.check_disk_space') as mock_check_space:
            mock_check_space.return_value = (True, 50.0, 20.0)  # Enough space
            
            success = model_manager.install_model('codellama:7b')
            
            assert success is True
            mock_subprocess['run'].assert_called_once()
    
    def test_install_model_insufficient_space(self, model_manager):
        """Test installing a model with insufficient disk space."""
        with patch('getllm.ollama.utils.check_disk_space') as mock_check_space:
            mock_check_space.return_value = (False, 10.0, 20.0)  # Not enough space
            
            with pytest.raises(DiskSpaceError):
                model_manager.install_model('codellama:7b')
    
    def test_install_speakleash_model(self, model_manager, mock_requests, tmp_path):
        """Test installing a SpeakLeash model."""
        import tempfile
        from unittest.mock import mock_open
        
        # Mock the temporary directory and file operations
        with patch('tempfile.TemporaryDirectory') as mock_temp_dir, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('os.path.exists', return_value=True), \
             patch('getllm.ollama.utils.run_command') as mock_run_command:
            
            # Set up the mock temporary directory
            mock_temp_dir.return_value.__enter__.return_value = str(tmp_path)
            
            # Mock successful command execution
            mock_run_command.return_value = (True, "Success")
            
            # Mock the requests.get for file downloads
            mock_response = MagicMock()
            mock_response.iter_content.return_value = [b'file content']
            mock_response.raise_for_status.return_value = None
            
            with patch('requests.get', return_value=mock_response):
                success = model_manager._install_speakleash_model('speakleash/bielik')
                
                assert success is True
                assert mock_file.call_count > 0  # Verify files were written
                mock_run_command.assert_called()  # Verify ollama create was called
    
    def test_get_model_info_found(self, model_manager):
        """Test getting info for an installed model."""
        with patch.object(model_manager, 'list_installed_models') as mock_list:
            mock_list.return_value = [
                {'name': 'codellama:7b', 'size': 3823},
                {'name': 'phi3:latest', 'size': 2048}
            ]
            
            model_info = model_manager.get_model_info('codellama:7b')
            
            assert model_info['name'] == 'codellama:7b'
            assert model_info['size'] == 3823
    
    def test_get_model_info_not_found(self, model_manager):
        """Test getting info for a non-existent model."""
        with patch.object(model_manager, 'list_installed_models') as mock_list:
            mock_list.return_value = [
                {'name': 'phi3:latest', 'size': 2048}
            ]
            
            with pytest.raises(ModelNotFoundError):
                model_manager.get_model_info('codellama:7b')
