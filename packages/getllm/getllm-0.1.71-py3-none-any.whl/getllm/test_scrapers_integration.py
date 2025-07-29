#!/usr/bin/env python3
"""
Test script for the integrated model scrapers
"""

import os
import sys
import json

# Import the model scrapers
from getllm.scrapers.ollama_scraper import OllamaModelsScraper
from getllm.scrapers.huggingface_scraper import HuggingFaceModelsScraper
from getllm.scrapers.unified_models_manager import UnifiedModelsManager

# Import the integration modules
from getllm.scrapers import scrape_huggingface_models, scrape_ollama_models, are_scrapers_available

# Import the models functions
from getllm.models import update_huggingface_models_cache, update_models_from_ollama, update_models_metadata
from getllm.models import load_huggingface_models_from_cache, load_ollama_models_from_cache


def test_direct_scrapers():
    print("\n🔍 Testing Direct Scraper Access...")
    
    if not are_scrapers_available():
        print("❌ Scrapers are not available")
        return False
    
    # Test Ollama scraper
    print("Testing OllamaModelsScraper...")
    ollama_scraper = OllamaModelsScraper()
    ollama_models = ollama_scraper.search_models(query="code", category="")
    print(f"Found {len(ollama_models)} Ollama models matching 'code'")
    
    # Test HuggingFace scraper
    print("\nTesting HuggingFaceModelsScraper...")
    hf_scraper = HuggingFaceModelsScraper()
    hf_models = hf_scraper.search_models(query="gguf", limit=5)
    print(f"Found {len(hf_models)} HuggingFace models matching 'gguf'")
    
    return True


def test_integration_layer():
    print("\n🔍 Testing Integration Layer...")
    
    # Test Hugging Face integration
    print("Testing HuggingFace integration...")
    hf_models = scrape_huggingface_models(limit=10)
    print(f"Scraped {len(hf_models)} HuggingFace models")
    
    # Test Ollama integration
    print("\nTesting Ollama integration...")
    ollama_models = scrape_ollama_models(limit=10)
    print(f"Scraped {len(ollama_models)} Ollama models")
    
    return len(hf_models) > 0 or len(ollama_models) > 0


def test_models_integration():
    print("\n🔍 Testing Models Integration...")
    
    # Test Hugging Face cache update
    print("Testing update_huggingface_models_cache...")
    hf_success = update_huggingface_models_cache(limit=10)
    print(f"HuggingFace cache update: {'✅ Success' if hf_success else '❌ Failed'}")
    
    # Test Ollama models update
    print("\nTesting update_models_from_ollama...")
    ollama_models = update_models_from_ollama(limit=10)
    ollama_success = len(ollama_models) > 0
    print(f"Ollama models update: {'✅ Success' if ollama_success else '❌ Failed'}")
    
    # Test models metadata update
    print("\nTesting update_models_metadata...")
    metadata_success = update_models_metadata()
    print(f"Models metadata update: {'✅ Success' if metadata_success else '❌ Failed'}")
    
    return hf_success or ollama_success or metadata_success


def main():
    print("🚀 Testing Model Scrapers Integration")
    
    # Test direct scrapers
    direct_success = test_direct_scrapers()
    
    # Test integration layer
    integration_success = test_integration_layer()
    
    # Test models integration
    models_success = test_models_integration()
    
    # Print summary
    print("\n📋 Test Summary:")
    print(f"Direct Scrapers: {'✅ Success' if direct_success else '❌ Failed'}")
    print(f"Integration Layer: {'✅ Success' if integration_success else '❌ Failed'}")
    print(f"Models Integration: {'✅ Success' if models_success else '❌ Failed'}")


if __name__ == "__main__":
    main()
