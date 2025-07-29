#!/usr/bin/env python3
"""
Model Scrapers Integration
Simplified integration of the Ollama and HuggingFace model scrapers
"""

import os
import json
import time
from typing import Dict, List, Any, Optional

# Import the necessary modules
try:
    from .OllamaModelsScraper import OllamaModelsScraper
    from .HuggingFaceModelsScraper import HuggingFaceModelsScraper
    SCRAPERS_AVAILABLE = True
except ImportError:
    SCRAPERS_AVAILABLE = False

# Cache file paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OLLAMA_CACHE = os.path.join(CURRENT_DIR, 'ollama_models.json')
HF_CACHE = os.path.join(CURRENT_DIR, 'hf_models.json')


def scrape_huggingface_models(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Scrape models from HuggingFace using the HuggingFaceModelsScraper
    
    Args:
        limit: Maximum number of models to fetch
        
    Returns:
        List of HuggingFace models
    """
    if not SCRAPERS_AVAILABLE:
        print("HuggingFaceModelsScraper is not available")
        return []
    
    try:
        print("\n🔄 Scraping HuggingFace models...")
        scraper = HuggingFaceModelsScraper()
        
        # Search for text generation models
        models = scraper.search_models(
            task="text-generation",
            limit=limit,
            sort="downloads"
        )
        
        # Process models to match expected format
        processed_models = []
        for model in models:
            processed = {
                'id': model.get('id', model.get('name', '')),
                'name': model.get('name', model.get('id', '')),
                'description': model.get('description', ''),
                'downloads': model.get('downloads', '0'),
                'url': model.get('url', ''),
                'source': 'huggingface',
                'metadata': {
                    'description': model.get('description', ''),
                    'downloads': model.get('downloads', '0'),
                    'url': model.get('url', ''),
                    'source': 'huggingface'
                }
            }
            processed_models.append(processed)
        
        # Save to cache file
        with open(HF_CACHE, 'w', encoding='utf-8') as f:
            json.dump(processed_models, f, indent=2)
        
        print(f"✅ Saved {len(processed_models)} HuggingFace models to cache")
        return processed_models
    except Exception as e:
        print(f"❌ Error scraping HuggingFace models: {e}")
        return []


def scrape_ollama_models(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Scrape models from Ollama using the OllamaModelsScraper
    
    Args:
        limit: Maximum number of models to fetch
        
    Returns:
        List of Ollama models
    """
    if not SCRAPERS_AVAILABLE:
        print("OllamaModelsScraper is not available")
        return []
    
    try:
        print("\n🔄 Scraping Ollama models...")
        scraper = OllamaModelsScraper()
        
        # Scrape models from categories
        models = []
        categories = ["", "chat", "code", "embedding"]
        
        for category in categories:
            print(f"📂 Scraping category: {category or 'all'}")
            category_models = scraper.search_models(category=category)
            models.extend(category_models)
            if len(models) >= limit:
                break
            time.sleep(0.5)  # Reduced rate limiting
        
        # Remove duplicates
        unique_models = []
        seen_names = set()
        for model in models:
            if model['name'] not in seen_names:
                seen_names.add(model['name'])
                unique_models.append(model)
        
        # Limit to the requested number
        models = unique_models[:limit]
        
        # Process models to match expected format
        processed_models = []
        for model in models:
            processed = {
                'name': model.get('name', ''),
                'description': model.get('description', ''),
                'size': model.get('size', 'Unknown'),
                'url': model.get('url', ''),
                'source': 'ollama',
                'metadata': {
                    'description': model.get('description', ''),
                    'pulls': model.get('pulls', '0'),
                    'url': model.get('url', ''),
                    'source': 'ollama'
                }
            }
            processed_models.append(processed)
        
        # Save to cache file
        with open(OLLAMA_CACHE, 'w', encoding='utf-8') as f:
            json.dump(processed_models, f, indent=2)
        
        print(f"✅ Saved {len(processed_models)} Ollama models to cache")
        return processed_models
    except Exception as e:
        print(f"❌ Error scraping Ollama models: {e}")
        return []


def are_scrapers_available() -> bool:
    """
    Check if the model scrapers are available
    
    Returns:
        True if scrapers are available, False otherwise
    """
    return SCRAPERS_AVAILABLE
