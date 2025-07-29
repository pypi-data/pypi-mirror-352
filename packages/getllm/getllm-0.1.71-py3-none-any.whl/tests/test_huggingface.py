import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from getllm.models import (
    get_hf_models_cache_path,
    get_huggingface_models,
    search_huggingface_models,
    update_huggingface_models_cache,
    DEFAULT_HF_MODELS
)


@patch('getllm.models.get_hf_models_cache_path')
@patch('os.path.exists')
@patch('builtins.open', new_callable=mock_open)
def test_get_huggingface_models_from_cache(mock_file, mock_exists, mock_cache_path):
    """Test getting Hugging Face models from cache."""
    # Setup mocks
    mock_cache_path.return_value = '/tmp/hf_models.json'
    mock_exists.return_value = True
    mock_file.return_value.read.return_value = json.dumps([
        {'id': 'model1', 'description': 'Description 1'},
        {'id': 'model2', 'description': 'Description 2'}
    ])
    
    # Call the function
    result = get_huggingface_models()
    
    # Verify results
    assert len(result) == 2
    assert result[0]['id'] == 'model1'
    assert result[1]['id'] == 'model2'
    mock_exists.assert_called_once()
    mock_file.assert_called_once()


@patch('getllm.models.get_hf_models_cache_path')
@patch('os.path.exists')
def test_get_huggingface_models_fallback(mock_exists, mock_cache_path):
    """Test getting Hugging Face models fallback to default list."""
    # Setup mocks
    mock_cache_path.return_value = '/tmp/hf_models.json'
    mock_exists.return_value = False
    
    # Call the function
    result = get_huggingface_models()
    
    # Verify results
    assert len(result) > 0
    assert result == DEFAULT_HF_MODELS
    mock_exists.assert_called_once()


@patch('getllm.models.get_huggingface_models')
def test_search_huggingface_models_no_query(mock_get_models):
    """Test searching Hugging Face models without a query."""
    # Setup mocks
    mock_models = [
        {'id': 'model1', 'description': 'Description 1'},
        {'id': 'model2', 'description': 'Description 2'}
    ]
    mock_get_models.return_value = mock_models
    
    # Call the function
    result = search_huggingface_models()
    
    # Verify results
    assert result == mock_models
    mock_get_models.assert_called_once()


@patch('getllm.models.get_huggingface_models')
def test_search_huggingface_models_with_query(mock_get_models):
    """Test searching Hugging Face models with a query."""
    # Setup mocks
    mock_models = [
        {'id': 'model1', 'description': 'Description 1'},
        {'id': 'bielik-model', 'description': 'Bielik model'}
    ]
    mock_get_models.return_value = mock_models
    
    # Call the function
    result = search_huggingface_models('bielik')
    
    # Verify results
    assert len(result) == 1
    assert result[0]['id'] == 'bielik-model'
    mock_get_models.assert_called_once()


@patch('getllm.models.get_huggingface_models')
@patch('getllm.models.requests.get')
@patch('getllm.models.BeautifulSoup')
def test_search_huggingface_models_direct_search(mock_soup, mock_get, mock_get_models):
    """Test searching Hugging Face models with direct search."""
    # Setup mocks for empty local results
    mock_get_models.return_value = []
    
    # Setup mock for requests.get
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Setup mock for BeautifulSoup
    mock_soup_instance = MagicMock()
    mock_card = MagicMock()
    mock_id_elem = MagicMock()
    mock_id_elem.text.strip.return_value = 'direct-model'
    mock_desc_elem = MagicMock()
    mock_desc_elem.text.strip.return_value = 'Direct model description'
    mock_downloads_elem = MagicMock()
    mock_downloads_elem.text.strip.return_value = '1000+'
    
    mock_card.select_one.side_effect = lambda selector: {
        'a.header-link': mock_id_elem,
        'p.description': mock_desc_elem,
        'div.flex.flex-col span.whitespace-nowrap': mock_downloads_elem
    }.get(selector, None)
    
    mock_soup_instance.select.return_value = [mock_card]
    mock_soup.return_value = mock_soup_instance
    
    # Call the function
    result = search_huggingface_models('direct')
    
    # Verify results
    assert len(result) == 1
    assert result[0]['id'] == 'direct-model'
    assert result[0]['description'] == 'Direct model description'
    assert result[0]['downloads'] == '1000+'
    mock_get_models.assert_called_once()
    mock_get.assert_called_once()
    mock_soup.assert_called_once()


@patch('getllm.models.get_huggingface_models')
@patch('getllm.models.requests.get')
def test_search_huggingface_models_direct_search_error(mock_get, mock_get_models):
    """Test searching Hugging Face models with direct search error."""
    # Setup mocks for filtered local results
    mock_models = [
        {'id': 'local-bielik', 'description': 'Local Bielik model'}
    ]
    mock_get_models.return_value = mock_models
    
    # Setup mock for requests.get to raise exception
    mock_get.side_effect = Exception('401 Unauthorized')
    
    # Call the function
    result = search_huggingface_models('bielik')
    
    # Verify results - should return the filtered local results
    assert len(result) == 1
    assert result[0]['id'] == 'local-bielik'
    mock_get_models.assert_called_once()
    mock_get.assert_called_once()


@patch('getllm.models.requests.get')
@patch('getllm.models.BeautifulSoup')
@patch('builtins.open', new_callable=mock_open)
@patch('os.makedirs')
def test_update_huggingface_models_cache_success(mock_makedirs, mock_file, mock_soup, mock_get):
    """Test updating Hugging Face models cache successfully."""
    # Setup mock for requests.get
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Setup mock for BeautifulSoup
    mock_soup_instance = MagicMock()
    mock_card = MagicMock()
    mock_id_elem = MagicMock()
    mock_id_elem.text.strip.return_value = 'updated-model'
    mock_desc_elem = MagicMock()
    mock_desc_elem.text.strip.return_value = 'Updated model description'
    mock_downloads_elem = MagicMock()
    mock_downloads_elem.text.strip.return_value = '5000+'
    mock_updated_elem = MagicMock()
    mock_updated_elem.text.strip.return_value = '2 days ago'
    
    mock_card.select_one.side_effect = lambda selector: {
        'a.header-link': mock_id_elem,
        'p.description': mock_desc_elem,
        'div.flex.flex-col span.whitespace-nowrap': mock_downloads_elem,
        'div.metadata time': mock_updated_elem
    }.get(selector, None)
    
    mock_soup_instance.select.return_value = [mock_card]
    mock_soup.return_value = mock_soup_instance
    
    # Call the function
    result = update_huggingface_models_cache()
    
    # Verify results
    assert result is True
    mock_get.assert_called_once()
    mock_soup.assert_called_once()
    mock_makedirs.assert_called_once()
    mock_file.assert_called_once()
    # Check that json.dump was called with the models
    json_dump_call = mock_file.return_value.__enter__.return_value.write.call_args[0][0]
    assert 'updated-model' in json_dump_call


@patch('getllm.models.requests.get')
@patch('builtins.open', new_callable=mock_open)
@patch('os.makedirs')
def test_update_huggingface_models_cache_error(mock_makedirs, mock_file, mock_get):
    """Test updating Hugging Face models cache with error."""
    # Setup mock for requests.get to raise exception for all attempts
    mock_get.side_effect = Exception('401 Unauthorized')
    
    # Call the function
    result = update_huggingface_models_cache()
    
    # Verify results
    assert result is False
    assert mock_get.call_count > 0  # Should have tried multiple URLs
    mock_makedirs.assert_called_once()
    mock_file.assert_called_once()
    # Check that json.dump was called with the DEFAULT_HF_MODELS
    json_dump_call = mock_file.return_value.__enter__.return_value.write.call_args[0][0]
    assert 'DEFAULT_HF_MODELS' not in json_dump_call  # The actual models, not the variable name
    for model in DEFAULT_HF_MODELS:
        assert model['id'] in json_dump_call
