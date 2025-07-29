#!/usr/bin/env python3
"""
Test script for the model scrapers and unified manager
"""

import os
import sys
import json
from OllamaModelsScraper import OllamaModelsScraper
from HuggingFaceModelsScraper import HuggingFaceModelsScraper
from UnifiedModelsManager import UnifiedModelsManager

# Define paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OLLAMA_OUTPUT = os.path.join(CURRENT_DIR, 'ollama_models.json')
HF_OUTPUT = os.path.join(CURRENT_DIR, 'huggingface_models.json')

def test_ollama_scraper():
    print("\n🔍 Testing Ollama Models Scraper...")
    scraper = OllamaModelsScraper()
    
    # Get models from library
    print("Fetching models from Ollama Library...")
    models = scraper.scrape_all_categories()
    scraper.models = models
    
    # Save to file
    if scraper.models:
        print(f"Found {len(scraper.models)} models")
        scraper.save_to_json(OLLAMA_OUTPUT)
        print(f"Saved to {OLLAMA_OUTPUT}")
        return True
    else:
        print("No models found or error occurred")
        return False

def test_huggingface_scraper():
    print("\n🔍 Testing HuggingFace Models Scraper...")
    scraper = HuggingFaceModelsScraper()
    
    # Get models with GGUF format
    print("Fetching GGUF models from HuggingFace (limit: 20)...")
    try:
        models = scraper.search_models(limit=20, task="text-generation")
        
        # Save to file
        if models:
            result = {
                "models": models,
                "count": len(models),
                "source": "huggingface"
            }
            
            with open(HF_OUTPUT, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
                
            print(f"Found {len(models)} models")
            print(f"Saved to {HF_OUTPUT}")
            return True
        else:
            print("No models found or error occurred")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_unified_manager():
    print("\n🔍 Testing Unified Models Manager...")
    manager = UnifiedModelsManager()
    
    # Load data
    manager.load_data(ollama_file=OLLAMA_OUTPUT, huggingface_file=HF_OUTPUT)
    
    # Combine models
    combined = manager.combine_models()
    print(f"Combined {len(combined)} models")
    
    # Test search
    if combined:
        # Search for Polish models
        print("\nSearching for Polish models:")
        polish_models = manager.search_models(query="polish")
        print(f"Found {len(polish_models)} Polish models")
        
        # Search for code models
        print("\nSearching for code models:")
        code_models = manager.search_models(query="code")
        print(f"Found {len(code_models)} code models")
        
        # Get recommendations
        print("\nGetting recommendations for Polish models:")
        recommendations = manager.get_recommendations("polish")
        # Display top 5 recommendations
        for i, model in enumerate(recommendations[:5], 1):
            print(f"{i}. {model.get('name')} - {model.get('description', '')[:50]}...")
        
        return True
    else:
        print("No models to search")
        return False

def main():
    print("🚀 Testing Model Scrapers and Manager")
    
    # Test Ollama scraper
    ollama_success = test_ollama_scraper()
    
    # Test HuggingFace scraper
    hf_success = test_huggingface_scraper()
    
    # Test unified manager if at least one scraper worked
    if ollama_success or hf_success:
        unified_success = test_unified_manager()
    else:
        print("\n⚠️ Both scrapers failed, skipping unified manager test")
        unified_success = False
    
    # Print summary
    print("\n📋 Test Summary:")
    print(f"Ollama Scraper: {'✅ Success' if ollama_success else '❌ Failed'}")
    print(f"HuggingFace Scraper: {'✅ Success' if hf_success else '❌ Failed'}")
    print(f"Unified Manager: {'✅ Success' if unified_success else '❌ Failed or Skipped'}")

if __name__ == "__main__":
    main()
