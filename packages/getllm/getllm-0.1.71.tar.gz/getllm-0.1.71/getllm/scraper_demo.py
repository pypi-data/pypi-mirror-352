#!/usr/bin/env python3
"""
Demo script for using the model scrapers with getllm
"""

import os
import json
import time

# Import the scrapers directly
from OllamaModelsScraper import OllamaModelsScraper
from HuggingFaceModelsScraper import HuggingFaceModelsScraper

# Cache file paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OLLAMA_CACHE = os.path.join(CURRENT_DIR, 'ollama_models.json')
HF_CACHE = os.path.join(CURRENT_DIR, 'hf_models.json')
METADATA_CACHE = os.path.join(CURRENT_DIR, 'models_metadata.json')


def scrape_ollama_models(limit=20):
    """
    Scrape models from Ollama and save to cache file
    
    Args:
        limit: Maximum number of models to fetch
        
    Returns:
        List of Ollama models
    """
    print("\nud83dudd04 Scraping Ollama models...")
    try:
        scraper = OllamaModelsScraper()
        
        # Scrape models from categories
        models = []
        categories = ["", "chat", "code", "embedding"]
        
        for category in categories:
            print(f"ud83dudcc2 Scraping category: {category or 'all'}")
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
        
        print(f"u2705 Saved {len(models)} Ollama models to cache")
        return models
    except Exception as e:
        print(f"u274c Error scraping Ollama models: {e}")
        return []


def scrape_huggingface_models(limit=20):
    """
    Scrape models from HuggingFace and save to cache file
    
    Args:
        limit: Maximum number of models to fetch
        
    Returns:
        List of HuggingFace models
    """
    print("\nud83dudd04 Scraping HuggingFace models...")
    try:
        scraper = HuggingFaceModelsScraper()
        
        # Search for text generation models
        models = scraper.search_models(
            task="text-generation",
            limit=limit,
            sort="downloads"
        )
        
        # Save to cache file
        result = {
            "models": models,
            "count": len(models),
            "source": "huggingface",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(HF_CACHE, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print(f"u2705 Saved {len(models)} HuggingFace models to cache")
        return models
    except Exception as e:
        print(f"u274c Error scraping HuggingFace models: {e}")
        return []


def create_combined_metadata():
    """
    Create a combined metadata file from both cache files
    
    Returns:
        True if successful, False otherwise
    """
    print("\nud83dudd04 Creating combined metadata...")
    try:
        # Load Ollama models
        ollama_models = []
        if os.path.exists(OLLAMA_CACHE):
            try:
                with open(OLLAMA_CACHE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'models' in data:
                        ollama_models = data['models']
                    else:
                        ollama_models = data
            except Exception as e:
                print(f"Error loading Ollama cache: {e}")
        
        # Load HuggingFace models
        hf_models = []
        if os.path.exists(HF_CACHE):
            try:
                with open(HF_CACHE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'models' in data:
                        hf_models = data['models']
                    else:
                        hf_models = data
            except Exception as e:
                print(f"Error loading HuggingFace cache: {e}")
        
        # Create metadata
        metadata = {
            "total_models": len(ollama_models) + len(hf_models),
            "ollama_models": len(ollama_models),
            "huggingface_models": len(hf_models),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sources": {
                "ollama": {
                    "count": len(ollama_models),
                    "models": ollama_models
                },
                "huggingface": {
                    "count": len(hf_models),
                    "models": hf_models
                }
            }
        }
        
        # Save metadata
        with open(METADATA_CACHE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"u2705 Created metadata with {metadata['total_models']} total models")
        return True
    except Exception as e:
        print(f"u274c Error creating metadata: {e}")
        return False


def main():
    """
    Main function to demonstrate the model scrapers
    """
    print("ud83dude80 Model Scrapers Demo")
    
    # Scrape Ollama models
    ollama_models = scrape_ollama_models(limit=20)
    
    # Scrape HuggingFace models
    hf_models = scrape_huggingface_models(limit=20)
    
    # Create combined metadata
    if ollama_models or hf_models:
        create_combined_metadata()
    
    print("\nud83dudccb Summary:")
    print(f"Ollama models: {len(ollama_models)}")
    print(f"HuggingFace models: {len(hf_models)}")
    print("\nThe model data has been saved to:")
    print(f"- Ollama cache: {OLLAMA_CACHE}")
    print(f"- HuggingFace cache: {HF_CACHE}")
    print(f"- Combined metadata: {METADATA_CACHE}")
    print("\nYou can now use these cache files with the getllm model management functions.")


if __name__ == "__main__":
    main()
