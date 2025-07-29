# Terraform configuration dla testu00f3w getLLM

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

# Zmienne u015brodowiskowe
locals {
  mock_mode = "--mock"
  test_dir  = "${path.module}/test_output"
}

# Utworzenie katalogu testowego
resource "local_file" "test_directory" {
  filename = "${local.test_dir}/directory_created"
  content  = "Test directory created at ${timestamp()}"

  provisioner "local-exec" {
    command = "mkdir -p ${local.test_dir}"
  }
}

# Test instalacji getLLM
resource "null_resource" "test_getllm_installation" {
  depends_on = [local_file.test_directory]

  provisioner "local-exec" {
    command = "which getllm || (echo 'getLLM nie jest zainstalowany' > ${local.test_dir}/installation_test.log && exit 1)"
  }
}

# Test wyszukiwania modeli Hugging Face
resource "null_resource" "test_hf_model_search" {
  depends_on = [null_resource.test_getllm_installation]

  provisioner "local-exec" {
    command = <<-EOT
      echo "search-hf" > ${local.test_dir}/input.txt
      echo "bielik" >> ${local.test_dir}/input.txt
      echo "exit" >> ${local.test_dir}/input.txt
      cat ${local.test_dir}/input.txt | getllm ${local.mock_mode} -i > ${local.test_dir}/hf_search_test.log 2>&1
      grep -i "bielik" ${local.test_dir}/hf_search_test.log || (echo "Nie znaleziono modeli Bielik w wyszukiwaniu Hugging Face" >> ${local.test_dir}/hf_search_test.log && exit 1)
    EOT
  }
}

# Test wyszukiwania Ollama z fallbackiem do Hugging Face
resource "null_resource" "test_ollama_search_with_fallback" {
  depends_on = [null_resource.test_hf_model_search]

  provisioner "local-exec" {
    command = <<-EOT
      echo "search-ollama" > ${local.test_dir}/input2.txt
      echo "bie" >> ${local.test_dir}/input2.txt
      echo "exit" >> ${local.test_dir}/input2.txt
      cat ${local.test_dir}/input2.txt | getllm ${local.mock_mode} -i > ${local.test_dir}/ollama_search_test.log 2>&1
      grep "Searching Hugging Face GGUF models" ${local.test_dir}/ollama_search_test.log || (echo "Wyszukiwanie w Ollama nie uruchomiu0142o fallbacku do Hugging Face" >> ${local.test_dir}/ollama_search_test.log && exit 1)
    EOT
  }
}

# Test generowania kodu
resource "null_resource" "test_code_generation" {
  depends_on = [null_resource.test_ollama_search_with_fallback]

  provisioner "local-exec" {
    command = <<-EOT
      getllm ${local.mock_mode} "Write a hello world program in Python" > ${local.test_dir}/code_gen_test.log 2>&1
      grep "print" ${local.test_dir}/code_gen_test.log || (echo "Generowanie kodu nie utworzyu0142o kodu Python" >> ${local.test_dir}/code_gen_test.log && exit 1)
    EOT
  }
}

# Sprawdzenie pliku00f3w cache
resource "null_resource" "test_cache_files" {
  depends_on = [null_resource.test_code_generation]

  provisioner "local-exec" {
    command = <<-EOT
      echo "Sprawdzanie pliku00f3w cache..." > ${local.test_dir}/cache_test.log
      HOME_DIR=$(echo $HOME)
      test -f $HOME_DIR/.getllm/models/huggingface_models.json || (echo "Plik cache Hugging Face nie istnieje" >> ${local.test_dir}/cache_test.log && exit 1)
      test -f $HOME_DIR/.getllm/models/ollama_models.json || (echo "Plik cache Ollama nie istnieje" >> ${local.test_dir}/cache_test.log && exit 1)
      test -f $HOME_DIR/.getllm/models/models_metadata.json || (echo "Plik metadanych nie istnieje" >> ${local.test_dir}/cache_test.log && exit 1)
      grep -i "bielik" $HOME_DIR/.getllm/models/huggingface_models.json || (echo "Nie znaleziono modeli Bielik w cache Hugging Face" >> ${local.test_dir}/cache_test.log && exit 1)
      echo "Wszystkie pliki cache istnieju0105 i zawieraju0105 oczekiwane dane" >> ${local.test_dir}/cache_test.log
    EOT
  }
}

# Podsumowanie testu00f3w
resource "null_resource" "test_summary" {
  depends_on = [null_resource.test_cache_files]

  provisioner "local-exec" {
    command = <<-EOT
      echo "\n=== PODSUMOWANIE TESTu00d3W ===" > ${local.test_dir}/summary.log
      echo "Testy zakou0144czone pomyu015blnie!" >> ${local.test_dir}/summary.log
      echo "Wyniki testu00f3w dostu0119pne w katalogu: ${local.test_dir}" >> ${local.test_dir}/summary.log
      echo "=========================" >> ${local.test_dir}/summary.log
      cat ${local.test_dir}/summary.log
    EOT
  }
}

# Output test results
output "test_results_dir" {
  value = local.test_dir
  description = "Katalog z wynikami testu00f3w"
  depends_on = [null_resource.test_summary]
}
