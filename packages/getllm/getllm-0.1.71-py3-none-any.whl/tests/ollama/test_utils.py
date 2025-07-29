"""Tests for the Ollama utility functions."""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

# Import the module to test
from getllm.ollama import utils

class TestUtils:
    """Test utility functions."""
    
    def test_get_package_dir(self, tmp_path):
        """Test getting the package directory."""
        with patch('pathlib.Path.home', return_value=tmp_path):
            package_dir = utils.get_package_dir()
            assert package_dir == tmp_path / '.getllm'
            assert package_dir.exists()
    
    def test_check_disk_space(self):
        """Test disk space checking."""
        with patch('shutil.disk_usage') as mock_disk_usage:
            # Mock 50GB free, 20GB required
            mock_disk_usage.return_value = (100 * 1024**3, 50 * 1024**3, 50 * 1024**3)
            
            has_space, available_gb, required_gb = utils.check_disk_space(required_space_gb=20)
            
            assert has_space is True
            assert available_gb == 50.0
            assert required_gb == 20.0
    
    def test_check_disk_space_insufficient(self):
        """Test disk space checking with insufficient space."""
        with patch('shutil.disk_usage') as mock_disk_usage:
            # Mock 10GB free, 20GB required
            mock_disk_usage.return_value = (100 * 1024**3, 90 * 1024**3, 10 * 1024**3)
            
            has_space, available_gb, required_gb = utils.check_disk_space(required_space_gb=20)
            
            assert has_space is False
            assert available_gb == 10.0
            assert required_gb == 20.0
    
    def test_run_command_success(self):
        """Test running a command successfully."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = type('', (), {
                'returncode': 0,
                'stdout': 'success',
                'stderr': ''
            })()
            
            success, output = utils.run_command("echo test")
            
            assert success is True
            assert output == 'success'
    
    def test_run_command_failure(self):
        """Test running a command that fails."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1,
                cmd="echo test",
                stderr="error",
                output="output"
            )
            
            success, output = utils.run_command("echo test")
            
            assert success is False
            assert "error" in output
    
    @pytest.mark.parametrize("system,expected", [
        ('Linux', True),
        ('Darwin', False),
        ('Windows', False),
    ])
    def test_is_linux(self, system, expected):
        """Test OS detection for Linux."""
        with patch('platform.system', return_value=system):
            assert utils.is_linux() == expected
    
    @pytest.mark.parametrize("system,expected", [
        ('Darwin', True),
        ('Linux', False),
        ('Windows', False),
    ])
    def test_is_macos(self, system, expected):
        """Test OS detection for macOS."""
        with patch('platform.system', return_value=system):
            assert utils.is_macos() == expected
    
    @pytest.mark.parametrize("system,expected", [
        ('Windows', True),
        ('Linux', False),
        ('Darwin', False),
    ])
    def test_is_windows(self, system, expected):
        """Test OS detection for Windows."""
        with patch('platform.system', return_value=system):
            assert utils.is_windows() == expected
    
    def test_extract_python_code_from_markdown(self):
        """Test extracting Python code from markdown."""
        markdown = """
        Here's some Python code:
        
        ```python
        def hello():
            return "Hello, World!"
        ```
        
        And some more text.
        """
        
        result = utils.extract_python_code(markdown)
        expected = 'def hello():\n    return "Hello, World!"'
        
        assert result.strip() == expected
    
    def test_extract_python_code_from_plain_text(self):
        """Test extracting Python code from plain text."""
        text = """
        This is some text.
        
        def hello():
            return "Hello, World!"
            
        And more text.
        """
        
        result = utils.extract_python_code(text)
        expected = 'def hello():\n    return "Hello, World!"'
        
        assert result.strip() == expected
    
    def test_extract_python_code_no_code(self):
        """Test extracting Python code when there is no code."""
        text = "This is just some regular text with no code."
        result = utils.extract_python_code(text)
        assert result == text
