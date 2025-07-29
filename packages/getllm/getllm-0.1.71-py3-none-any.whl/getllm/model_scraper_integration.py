#!/usr/bin/env python3
"""
Model Scraper Integration
Integrates the OllamaModelsScraper and HuggingFaceModelsScraper with getllm
"""

import os
import json
import time
from typing import Dict, List, Any, Optional

# Import scrapers
from .OllamaModelsScraper import OllamaModelsScraper
from .HuggingFaceModelsScraper import HuggingFaceModelsScraper
from .UnifiedModelsManager import UnifiedModelsManager

# Cache file paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OLLAMA_CACHE = os.path.join(CURRENT_DIR, 'ollama_models.json')
HF_CACHE = os.path.join(CURRENT_DIR, 'hf_models.json')
METADATA_CACHE = os.path.join(CURRENT_DIR, 'models_metadata.json')


def update_ollama_models_cache(limit: int = 100, detailed: bool = False) -> List[Dict[str, Any]]:
    """
    Update the Ollama models cache file using the OllamaModelsScraper
    
    Args:
        limit: Maximum number of models to fetch
        detailed: Whether to fetch detailed information for each model
        
    Returns:
        List of Ollama models
    """
    print("\n🔄 Updating Ollama models cache...")
    try:
        scraper = OllamaModelsScraper()
        
        # Limit the number of models to scrape to save time
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
        
        # Save to cache file
        result = {
            "models": models,
            "count": len(models),
            "source": "ollama",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(OLLAMA_CACHE, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Saved {len(models)} Ollama models to cache")
        return models
    except Exception as e:
        print(f"❌ Error updating Ollama models cache: {e}")
        return []


def update_huggingface_models_cache(limit: int = 100, ollama_compatible: bool = True) -> List[Dict[str, Any]]:
    """
    Update the Hugging Face models cache file using the HuggingFaceModelsScraper
    
    Args:
        limit: Maximum number of models to fetch
        ollama_compatible: Whether to only fetch models compatible with Ollama
        
    Returns:
        List of Hugging Face models
    """
    print("\n🔄 Updating Hugging Face models cache...")
    try:
        scraper = HuggingFaceModelsScraper()
        
        # Search for text generation models compatible with Ollama
        models = scraper.search_models(
            task="text-generation",
            limit=limit,
            sort="downloads"
        )
        
        # Filter for Ollama compatibility if requested
        if ollama_compatible:
            models = [model for model in models if model.get('ollama_compatible', False)]
        
        # Save to cache file
        result = {
            "models": models,
            "count": len(models),
            "source": "huggingface",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(HF_CACHE, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Saved {len(models)} Hugging Face models to cache")
        return models
    except Exception as e:
        print(f"❌ Error updating Hugging Face models cache: {e}")
        return []


def update_models_metadata():
    """
    Update the combined models metadata file using the UnifiedModelsManager
    """
    print("\n🔄 Updating models metadata...")
    try:
        manager = UnifiedModelsManager()
        manager.load_data(ollama_file=OLLAMA_CACHE, huggingface_file=HF_CACHE)
        combined = manager.combine_models()
        
        # Create metadata with recommendations
        metadata = {
            "total_models": len(combined),
            "ollama_models": len([m for m in combined if m['source'] == 'ollama']),
            "huggingface_models": len([m for m in combined if m['source'] == 'huggingface']),
            "local_ready": len([m for m in combined if m.get('local_ready', False)]),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "recommendations": {
                "general": manager.get_recommendations("general")[:10],
                "chat": manager.get_recommendations("chat")[:10],
                "coding": manager.get_recommendations("code")[:10],
                "polish": manager.get_recommendations("polish")[:10]
            }
        }
        
        with open(METADATA_CACHE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Updated metadata for {len(combined)} models")
        return metadata
    except Exception as e:
        print(f"❌ Error updating models metadata: {e}")
        return {}


def update_all_model_caches(ollama_limit: int = 50, hf_limit: int = 100):
    """
    Update all model cache files
    
    Args:
        ollama_limit: Maximum number of Ollama models to fetch
        hf_limit: Maximum number of Hugging Face models to fetch
    """
    print("🚀 Starting model cache update...")
    
    # Update Ollama models cache
    ollama_models = update_ollama_models_cache(limit=ollama_limit)
    
    # Update Hugging Face models cache
    hf_models = update_huggingface_models_cache(limit=hf_limit)
    
    # Update combined metadata if at least one cache was updated
    if ollama_models or hf_models:
        update_models_metadata()
    
    print("✅ Model cache update completed")


def search_models(query: str, source: str = "all", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for models across all sources
    
    Args:
        query: Search query
        source: Source to search ("all", "ollama", or "huggingface")
        limit: Maximum number of results to return
        
    Returns:
        List of matching models
    """
    try:
        manager = UnifiedModelsManager()
        manager.load_data(ollama_file=OLLAMA_CACHE, huggingface_file=HF_CACHE)
        combined = manager.combine_models()
        
        results = manager.search_models(query=query, source=source)
        return results[:limit]
    except Exception as e:
        print(f"❌ Error searching models: {e}")
        return []


if __name__ == "__main__":
    update_all_model_caches()
