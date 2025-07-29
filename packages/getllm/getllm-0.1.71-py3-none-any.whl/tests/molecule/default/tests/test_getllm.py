import os
import pytest

def test_getllm_installed(host):
    """Test that getLLM is installed and accessible."""
    getllm = host.command("which getllm")
    assert getllm.rc == 0, "getLLM is not installed"

def test_huggingface_model_search(host):
    """Test searching for Bielik models in Hugging Face."""
    cmd = "cat /tmp/getllm_test/hf_search_input.txt | getllm --mock -i"
    result = host.command(cmd)
    assert "bielik" in result.stdout.lower() or "Bielik" in result.stdout, \
        "Bielik model not found in Hugging Face search"

def test_ollama_search_with_fallback(host):
    """Test Ollama search with fallback to Hugging Face for 'bie' query."""
    cmd = "cat /tmp/getllm_test/ollama_search_input.txt | getllm --mock -i"
    result = host.command(cmd)
    assert "Searching Hugging Face GGUF models" in result.stdout, \
        "Hugging Face fallback not triggered for Ollama search"

def test_direct_code_generation(host):
    """Test direct code generation capability."""
    cmd = "getllm --mock 'Write a hello world program in Python'"
    result = host.command(cmd)
    assert "print" in result.stdout, "Code generation failed to produce Python code"
