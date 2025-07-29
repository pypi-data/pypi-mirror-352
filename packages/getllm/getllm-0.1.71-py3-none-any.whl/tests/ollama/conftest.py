"""Pytest configuration and fixtures for Ollama integration tests."""
import os
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def mock_requests():
    """Fixture to mock requests module."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('requests.Session') as mock_session:
        
        # Configure mock session
        session = MagicMock()
        session.get.return_value = MagicMock(status_code=200, json=lambda: {'version': '1.0.0'})
        session.post.return_value = MagicMock(status_code=200, json=lambda: {})
        mock_session.return_value = session
        
        # Configure mock get and post
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {'version': '1.0.0'})
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {})
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'session': mock_session
        }

@pytest.fixture
def mock_subprocess():
    """Fixture to mock subprocess module."""
    with patch('subprocess.run') as mock_run, \
         patch('subprocess.Popen') as mock_popen:
        
        # Configure mock run
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=b'ollama version 1.0.0',
            stderr=b''
        )
        
        # Configure mock Popen
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        yield {
            'run': mock_run,
            'Popen': mock_popen,
            'process': mock_process
        }

@pytest.fixture
def mock_platform_linux():
    """Fixture to mock platform.system() to return 'Linux'."""
    with patch('platform.system', return_value='Linux'), \
         patch('shutil.which', return_value='/usr/bin/ollama'):
        yield

@pytest.fixture
def mock_platform_darwin():
    """Fixture to mock platform.system() to return 'Darwin'."""
    with patch('platform.system', return_value='Darwin'), \
         patch('shutil.which', return_value='/usr/local/bin/ollama'):
        yield

@pytest.fixture
def mock_platform_windows():
    """Fixture to mock platform.system() to return 'Windows'."""
    with patch('platform.system', return_value='Windows'), \
         patch('shutil.which', return_value='C:\\Program Files\\Ollama\\ollama.exe'):
        yield

@pytest.fixture
def temp_dir():
    """Fixture to create and clean up a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_ollama_installed():
    """Fixture to mock Ollama as installed."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=b'ollama version 1.0.0',
            stderr=b''
        )
        yield

@pytest.fixture
def mock_ollama_not_installed():
    """Fixture to mock Ollama as not installed."""
    with patch('subprocess.run', side_effect=FileNotFoundError()):
        yield

@pytest.fixture
def mock_ollama_running():
    """Fixture to mock Ollama server as running."""
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {'version': '1.0.0'})
        yield mock_get

@pytest.fixture
def mock_ollama_not_running():
    """Fixture to mock Ollama server as not running."""
    with patch('requests.get', side_effect=ConnectionError()):
        yield

@pytest.fixture
def mock_ollama_models():
    """Fixture to mock Ollama models list."""
    models = {
        'models': [
            {'name': 'codellama:7b', 'size': 3823, 'modified_at': '2023-08-07T12:00:00Z'},
            {'name': 'phi3:latest', 'size': 2048, 'modified_at': '2023-08-07T12:00:00Z'},
            {'name': 'tinyllama:latest', 'size': 512, 'modified_at': '2023-08-07T12:00:00Z'}
        ]
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: models)
        yield mock_get

@pytest.fixture
def mock_ollama_pull_success():
    """Fixture to mock successful model pull."""
    with patch('requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {'status': 'success'})
        yield mock_post
