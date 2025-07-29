terraform {
  required_version = ">= 1.0.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.1.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.1.0"
    }
  }
}

# Define test directory
resource "local_file" "test_directory" {
  filename = "${path.module}/test_output/directory_created"
  content  = "Test directory created at ${timestamp()}"

  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/test_output"
  }
}

# Test getLLM installation
resource "null_resource" "test_getllm_installation" {
  depends_on = [local_file.test_directory]

  provisioner "local-exec" {
    command = "which getllm || echo 'getLLM not found' > ${path.module}/test_output/installation_test.log"
  }
}

# Test Hugging Face model search
resource "null_resource" "test_hf_model_search" {
  depends_on = [null_resource.test_getllm_installation]

  provisioner "local-exec" {
    command = <<-EOT
      echo "search-hf" > ${path.module}/test_output/input.txt
      echo "bielik" >> ${path.module}/test_output/input.txt
      echo "exit" >> ${path.module}/test_output/input.txt
      cat ${path.module}/test_output/input.txt | getllm --mock -i > ${path.module}/test_output/hf_search_test.log 2>&1 || echo "Test failed" >> ${path.module}/test_output/hf_search_test.log
    EOT
  }
}

# Test Ollama model search with Hugging Face fallback
resource "null_resource" "test_ollama_search_with_fallback" {
  depends_on = [null_resource.test_hf_model_search]

  provisioner "local-exec" {
    command = <<-EOT
      echo "search-ollama" > ${path.module}/test_output/input2.txt
      echo "bie" >> ${path.module}/test_output/input2.txt
      echo "exit" >> ${path.module}/test_output/input2.txt
      cat ${path.module}/test_output/input2.txt | getllm --mock -i > ${path.module}/test_output/ollama_search_test.log 2>&1 || echo "Test failed" >> ${path.module}/test_output/ollama_search_test.log
    EOT
  }
}

# Validate test results
resource "null_resource" "validate_test_results" {
  depends_on = [null_resource.test_ollama_search_with_fallback]

  provisioner "local-exec" {
    command = <<-EOT
      echo "Validating test results..." > ${path.module}/test_output/validation.log
      
      # Check HF search results
      if grep -q "bielik" ${path.module}/test_output/hf_search_test.log; then
        echo "✅ Hugging Face search test passed" >> ${path.module}/test_output/validation.log
      else
        echo "❌ Hugging Face search test failed" >> ${path.module}/test_output/validation.log
      fi
      
      # Check Ollama search with HF fallback
      if grep -q "Searching Hugging Face GGUF models" ${path.module}/test_output/ollama_search_test.log; then
        echo "✅ Ollama search with fallback test passed" >> ${path.module}/test_output/validation.log
      else
        echo "❌ Ollama search with fallback test failed" >> ${path.module}/test_output/validation.log
      fi
    EOT
  }
}

# Output test results
output "test_results" {
  value = "Test results available in ${path.module}/test_output/"
  depends_on = [null_resource.validate_test_results]
}
