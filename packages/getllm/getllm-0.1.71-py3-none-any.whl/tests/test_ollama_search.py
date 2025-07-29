import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from getllm.models import (
    get_models,
    update_models_from_ollama
)
from getllm.interactive_cli import choose_model


@patch('getllm.models.get_models')
def test_ollama_search_by_name(mock_get_models):
    """Test searching Ollama models by name."""
    # Setup mocks
    mock_models = [
        {'name': 'llama2:7b', 'size': '7B', 'desc': 'Llama 2 model'},
        {'name': 'codellama:7b', 'size': '7B', 'desc': 'Code Llama model'},
        {'name': 'mistral:7b', 'size': '7B', 'desc': 'Mistral model'}
    ]
    mock_get_models.return_value = mock_models
    
    # Call the function with a filter
    filtered_models = [m for m in mock_models if 'code' in m['name'].lower() or 'code' in m.get('desc', '').lower()]
    
    # Verify results
    assert len(filtered_models) == 1
    assert filtered_models[0]['name'] == 'codellama:7b'
    mock_get_models.assert_called_once()


@patch('getllm.models.get_models')
def test_ollama_search_by_description(mock_get_models):
    """Test searching Ollama models by description."""
    # Setup mocks
    mock_models = [
        {'name': 'llama2:7b', 'size': '7B', 'desc': 'Llama 2 model'},
        {'name': 'codellama:7b', 'size': '7B', 'desc': 'Code Llama model'},
        {'name': 'mistral:7b', 'size': '7B', 'desc': 'Mistral model'}
    ]
    mock_get_models.return_value = mock_models
    
    # Call the function with a filter
    filtered_models = [m for m in mock_models if 'llama' in m['name'].lower() or 'llama' in m.get('desc', '').lower()]
    
    # Verify results
    assert len(filtered_models) == 2
    assert filtered_models[0]['name'] == 'llama2:7b'
    assert filtered_models[1]['name'] == 'codellama:7b'
    mock_get_models.assert_called_once()


@patch('getllm.models.requests.get')
@patch('getllm.models.BeautifulSoup')
@patch('getllm.models.save_models_to_json')
def test_update_models_from_ollama_success(mock_save, mock_soup, mock_get):
    """Test updating models from Ollama website successfully."""
    # Setup mock for requests.get
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Setup mock for BeautifulSoup
    mock_soup_instance = MagicMock()
    
    # Create mock cards
    mock_cards = []
    for i, model_name in enumerate(['llama2', 'codellama', 'mistral']):
        mock_card = MagicMock()
        
        # Mock the name element
        mock_name_elem = MagicMock()
        mock_name_elem.text.strip.return_value = f"{model_name}:7b"
        
        # Mock the description element
        mock_desc_elem = MagicMock()
        mock_desc_elem.text.strip.return_value = f"{model_name.capitalize()} 7B model"
        
        # Setup find method to return the appropriate elements
        mock_card.find.side_effect = lambda tag, **kwargs: {
            'h3': mock_name_elem if tag == 'h3' else None,
            'h2': mock_name_elem if tag == 'h2' else None,
            'p': mock_desc_elem
        }.get(tag, None)
        
        mock_cards.append(mock_card)
    
    # Setup find_all to return the mock cards
    mock_soup_instance.find_all.return_value = mock_cards
    mock_soup.return_value = mock_soup_instance
    
    # Call the function
    update_models_from_ollama()
    
    # Verify results
    mock_get.assert_called_once_with("https://ollama.com/library")
    mock_soup.assert_called_once()
    mock_save.assert_called_once()
    
    # Check that save_models_to_json was called with the correct models
    saved_models = mock_save.call_args[0][0]
    assert len(saved_models) == 3
    assert saved_models[0]['name'] == 'llama2:7b'
    assert saved_models[1]['name'] == 'codellama:7b'
    assert saved_models[2]['name'] == 'mistral:7b'


@patch('getllm.models.requests.get')
@patch('getllm.models.save_models_to_json')
@patch('getllm.models.DEFAULT_MODELS')
def test_update_models_from_ollama_error(mock_default_models, mock_save, mock_get):
    """Test updating models from Ollama website with error."""
    # Setup mock for DEFAULT_MODELS
    mock_default_models.__iter__.return_value = [
        {'name': 'default1', 'size': '7B', 'desc': 'Default model 1'},
        {'name': 'default2', 'size': '7B', 'desc': 'Default model 2'}
    ]
    
    # Setup mock for requests.get to raise exception
    mock_get.side_effect = Exception('Connection error')
    
    # Call the function
    update_models_from_ollama()
    
    # Verify results
    mock_get.assert_called_once()
    mock_save.assert_called_once()
    
    # Check that save_models_to_json was called with the default models
    saved_models = mock_save.call_args[0][0]
    assert len(saved_models) == 2
    assert saved_models[0]['name'] == 'default1'
    assert saved_models[1]['name'] == 'default2'


@patch('questionary.select')
@patch('getllm.models.get_models')
@patch('getllm.ollama_integration.get_ollama_integration')
def test_choose_model_ollama_library(mock_ollama, mock_get_models, mock_select):
    """Test choosing a model from Ollama library."""
    # Setup mocks
    mock_models = [
        {'name': 'llama2:7b', 'size': '7B', 'desc': 'Llama 2 model'},
        {'name': 'codellama:7b', 'size': '7B', 'desc': 'Code Llama model'}
    ]
    mock_get_models.return_value = mock_models
    
    # Setup mock for questionary.select
    mock_select.return_value.ask.side_effect = [
        "Ollama Library (predefined models)",  # Source selection
        "llama2:7b"  # Model selection
    ]
    
    # Setup mock for ollama integration
    mock_ollama_instance = MagicMock()
    mock_ollama_instance.is_ollama_installed = True
    mock_ollama_instance.list_installed_models.return_value = []
    mock_ollama.return_value = mock_ollama_instance
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Call the function
    choose_model("install", mock_callback)
    
    # Verify results
    assert mock_select.call_count == 2
    mock_callback.assert_called_once_with("llama2:7b")


@patch('questionary.select')
@patch('questionary.text')
@patch('getllm.models.get_models')
@patch('getllm.ollama_integration.get_ollama_integration')
def test_choose_model_search(mock_ollama, mock_get_models, mock_text, mock_select):
    """Test choosing a model by searching."""
    # Setup mocks
    mock_models = [
        {'name': 'llama2:7b', 'size': '7B', 'desc': 'Llama 2 model'},
        {'name': 'codellama:7b', 'size': '7B', 'desc': 'Code Llama model'}
    ]
    mock_get_models.return_value = mock_models
    
    # Setup mock for questionary.select and text
    mock_select.return_value.ask.side_effect = [
        "Search by name (all sources)",  # Source selection
        "codellama:7b"  # Model selection
    ]
    mock_text.return_value.ask.return_value = "code"  # Search term
    
    # Setup mock for ollama integration
    mock_ollama_instance = MagicMock()
    mock_ollama_instance.is_ollama_installed = True
    mock_ollama_instance.list_installed_models.return_value = []
    mock_ollama.return_value = mock_ollama_instance
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Call the function
    choose_model("install", mock_callback)
    
    # Verify results
    assert mock_select.call_count == 2
    mock_text.assert_called_once()
    mock_callback.assert_called_once_with("codellama:7b")
