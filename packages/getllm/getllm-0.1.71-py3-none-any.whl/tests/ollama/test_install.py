"""
Tests for the Ollama installation module.
"""
import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from getllm.ollama.install import OllamaInstaller, ensure_ollama_installed
from getllm.ollama.exceptions import InstallationError

class TestOllamaInstaller:
    """Test the OllamaInstaller class."""
    
    @pytest.fixture
    def installer(self):
        """Create an installer instance for testing."""
        return OllamaInstaller()
    
    def test_is_installed_true(self, installer, mock_subprocess):
        """Test checking if Ollama is installed (true case)."""
        assert installer.is_installed() is True
    
    def test_is_installed_false(self, installer):
        """Test checking if Ollama is installed (false case)."""
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            assert installer.is_installed() is False
    
    @pytest.mark.parametrize("system,expected_method", [
        ('Linux', 'install_linux'),
        ('Darwin', 'install_macos'),
        ('Windows', 'install_windows'),
    ])
    def test_install_auto_platform(self, installer, system, expected_method, mock_subprocess):
        """Test auto-installation on different platforms."""
        with patch('platform.system', return_value=system), \
             patch(f'getllm.ollama.install.OllamaInstaller.{expected_method}') as mock_method:
            
            mock_method.return_value = True
            
            result = installer.install('auto')
            
            assert result is True
            mock_method.assert_called_once()
    
    def test_install_auto_fallback_to_docker(self, installer, mock_subprocess):
        """Test auto-installation falls back to Docker on unsupported platform."""
        with patch('platform.system', return_value='UnsupportedOS'), \
             patch('getllm.ollama.install.OllamaInstaller.install_docker') as mock_docker:
            
            mock_docker.return_value = True
            
            result = installer.install('auto')
            
            assert result is True
            mock_docker.assert_called_once()
    
    def test_install_linux_success(self, installer, mock_subprocess):
        """Test Linux installation successfully."""
        with patch('shutil.which', return_value='/usr/bin/curl'), \
             patch('getllm.ollama.utils.run_command') as mock_run_command:
            
            mock_run_command.return_value = (True, "Installation successful")
            
            result = installer.install_linux()
            
            assert result is True
            assert mock_run_command.call_count >= 1
    
    def test_install_linux_install_curl(self, installer):
        """Test Linux installation when curl needs to be installed."""
        with patch('shutil.which', side_effect=[None, '/usr/bin/curl']), \
             patch('getllm.ollama.utils.run_command') as mock_run_command:
            
            mock_run_command.return_value = (True, "Installation successful")
            
            result = installer.install_linux()
            
            assert result is True
            assert mock_run_command.call_count >= 2  # Install curl, then install Ollama
    
    def test_install_macos_success(self, installer, mock_subprocess):
        """Test macOS installation successfully."""
        with patch('shutil.which', return_value='/usr/local/bin/brew'), \
             patch('getllm.ollama.utils.run_command') as mock_run_command:
            
            mock_run_command.return_value = (True, "Installation successful")
            
            result = installer.install_macos()
            
            assert result is True
            mock_run_command.assert_called_once_with("brew install ollama")
    
    def test_install_macos_install_homebrew(self, installer):
        """Test macOS installation when Homebrew needs to be installed."""
        with patch('shutil.which', side_effect=[None, '/usr/local/bin/brew']), \
             patch('getllm.ollama.utils.run_command') as mock_run_command:
            
            mock_run_command.return_value = (True, "Installation successful")
            
            result = installer.install_macos()
            
            assert result is True
            assert mock_run_command.call_count == 2  # Install Homebrew, then install Ollama
    
    def test_install_windows_success(self, installer, mock_subprocess):
        """Test Windows installation successfully."""
        with patch('subprocess.run') as mock_run, \
             patch('getllm.ollama.utils.run_command') as mock_run_command:
            
            mock_run.return_value = MagicMock(returncode=0)
            mock_run_command.return_value = (True, "Installation successful")
            
            result = installer.install_windows()
            
            assert result is True
            mock_run_command.assert_called_once_with("winget install ollama.ollama", shell=True)
    
    def test_install_windows_no_winget(self, installer):
        """Test Windows installation when winget is not available."""
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            with pytest.raises(InstallationError, match="winget is required"):
                installer.install_windows()
    
    def test_install_docker_success(self, installer, mock_subprocess):
        """Test Docker installation successfully."""
        with patch('subprocess.run') as mock_run, \
             patch('getllm.ollama.utils.run_command') as mock_run_command:
            
            mock_run.return_value = MagicMock(returncode=0)
            mock_run_command.return_value = (True, "Success")
            
            result = installer.install_docker()
            
            assert result is True
            assert mock_run_command.call_count >= 2  # pull, volume create, run
    
    def test_install_docker_not_installed(self, installer):
        """Test Docker installation when Docker is not installed."""
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            with pytest.raises(InstallationError, match="Docker is not installed"):
                installer.install_docker()
    
    def test_install_bexy_not_implemented(self, installer):
        """Test Bexy installation (not implemented)."""
        with pytest.warns(UserWarning, match="Bexy sandbox installation is not fully implemented"):
            result = installer.install_bexy()
            assert result is False


def test_ensure_ollama_installed_already_installed():
    """Test ensure_ollama_installed when Ollama is already installed."""
    with patch('getllm.ollama.install.OllamaInstaller') as mock_installer_class:
        mock_installer = MagicMock()
        mock_installer.is_installed.return_value = True
        mock_installer_class.return_value = mock_installer
        
        result = ensure_ollama_installed()
        
        assert result is True
        mock_installer.install.assert_not_called()


def test_ensure_ollama_installed_install_success():
    """Test ensure_ollama_installed when installation is needed and succeeds."""
    with patch('getllm.ollama.install.OllamaInstaller') as mock_installer_class:
        mock_installer = MagicMock()
        mock_installer.is_installed.return_value = False
        mock_installer.install.return_value = True
        mock_installer_class.return_value = mock_installer
        
        result = ensure_ollama_installed()
        
        assert result is True
        mock_installer.install.assert_called_once()


def test_ensure_ollama_installed_install_failure():
    """Test ensure_ollama_installed when installation fails."""
    with patch('getllm.ollama.install.OllamaInstaller') as mock_installer_class:
        mock_installer = MagicMock()
        mock_installer.is_installed.return_value = False
        mock_installer.install.return_value = False
        mock_installer_class.return_value = mock_installer
        
        result = ensure_ollama_installed()
        
        assert result is False
        mock_installer.install.assert_called_once()
