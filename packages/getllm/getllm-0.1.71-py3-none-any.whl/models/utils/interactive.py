"""
Interactive search utilities for model selection.
"""

import sys
from typing import Optional, List, Dict, Any
from pathlib import Path

# Import from the huggingface module using absolute import to avoid circular imports
from getllm.models.huggingface import search_huggingface_models as hf_search
from getllm.models.ollama import search_ollama_models as ollama_search

def interactive_model_search(query: str = None, check_ollama: bool = True) -> Optional[str]:
    """
    Interactive search for models across different sources.
    
    Args:
        query: The search query (e.g., "llama"). If None, prompts the user.
        check_ollama: Whether to check Ollama models.
        
    Returns:
        The selected model ID or None if cancelled.
    """
    if query is None:
        query = input("Enter search query (e.g., 'llama'): ").strip()
    
    if not query:
        print("No search query provided.")
        return None
    
    print(f"\nSearching for models matching: {query}")
    
    # Search Hugging Face models
    print("\n=== Hugging Face Models ===")
    hf_models = hf_search(query=query, limit=5)
    
    # Search Ollama models if available
    ollama_models = []
    if check_ollama:
        try:
            print("\n=== Ollama Models ===")
            ollama_models = ollama_search(query=query, limit=5)
        except Exception as e:
            print(f"Warning: Could not search Ollama models: {e}")
    
    # Combine and display results
    all_models = []
    
    if hf_models:
        all_models.extend([("HF", model) for model in hf_models])
    if ollama_models:
        all_models.extend([("Ollama", model) for model in ollama_models])
    
    if not all_models:
        print("No models found matching your query.")
        return None
    
    # Display results
    print("\nSearch Results:")
    print("-" * 50)
    for i, (source, model) in enumerate(all_models, 1):
        model_id = model.get('id', model.get('name', 'Unknown'))
        print(f"{i}. [{source}] {model_id}")
    
    # Let user select a model
    while True:
        try:
            choice = input("\nSelect a model number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return None
                
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(all_models):
                selected_source, selected_model = all_models[choice_idx]
                model_id = selected_model.get('id', selected_model.get('name'))
                return f"{selected_source.lower()}:{model_id}"
                
            print("Invalid selection. Please try again.")
            
        except (ValueError, IndexError):
            print("Invalid input. Please enter a valid number or 'q' to quit.")

__all__ = ['interactive_model_search']
