# Declarative Testing Solutions for getLLM

This directory contains various declarative and infrastructure-as-code testing solutions for getLLM that replace traditional Python and Bash tests. These solutions focus on validating the enhanced functionality including Hugging Face model integration, Ollama search with fallback, and model installation workflows.

## Overview of Test Solutions

### 1. Ansible Playbooks (`/tests/ansible/`)

Ansible provides a YAML-based approach to testing infrastructure and application functionality.

```bash
cd tests/ansible
ansible-playbook -i inventory.yml test_getllm.yml
```

### 2. Terraform Test Infrastructure (`/tests/terraform/`)

Terraform configuration that sets up a test environment and validates getLLM functionality.

```bash
cd tests/terraform
terraform init
terraform apply
```

### 3. Goss Declarative Tests (`/tests/goss/`)

Goss tests provide a YAML-based approach to validating getLLM installation, configuration, and functionality.

```bash
cd tests/goss
# Install Goss if not already installed
# curl -fsSL https://goss.rocks/install | sh
goss validate
```

### 4. Robot Framework Test Suite (`/tests/robot/`)

Robot Framework uses a tabular syntax for creating test cases in a more declarative way.

```bash
cd tests/robot
# Install Robot Framework if not already installed
# pip install robotframework
robot getllm_tests.robot
```

### 5. Docker Compose Test Environment (`/tests/docker/`)

Docker Compose configuration that creates an isolated test environment for getLLM.

```bash
cd tests/docker
docker-compose up
```

### 6. Molecule Test Framework (`/tests/molecule/`)

Molecule test suite that sets up a containerized test environment for getLLM.

```bash
cd tests/molecule
# Install Molecule if not already installed
# pip install molecule molecule-docker
molecule test
```

### 7. JSON Schema Validation (`/tests/json_schema/`)

JSON Schema validation for getLLM's configuration and cache files.

```bash
cd tests/json_schema
npm install
npm test
```

### 8. YAML-Based Test Specifications (`/tests/yaml_specs/`)

YAML-based test specifications that define expected behaviors and outcomes for getLLM.

```bash
cd tests/yaml_specs
# Make the runner executable
chmod +x run_yaml_tests.py
./run_yaml_tests.py
```

### 9. TOML-Based Test Manifests (`/tests/toml_manifests/`)

TOML-based test manifests that offer a more readable alternative to YAML and JSON.

```bash
cd tests/toml_manifests
# Install tomli if needed
# pip install tomli
chmod +x run_toml_tests.py
./run_toml_tests.py
```

### 10. Jsonnet Test Configuration (`/tests/jsonnet/`)

Jsonnet-based test configuration for getLLM that extends JSON with features like variables and conditionals.

```bash
cd tests/jsonnet
# Install Jsonnet if not already installed
# pip install jsonnet
jsonnet -V PROJECT_ROOT="$(pwd)/../.." test_config.jsonnet > test_config.json
```

## Features Tested

These declarative tests focus on validating the following features of getLLM:

1. **Hugging Face Model Integration**
   - Verifies that Bielik models are available in the Hugging Face cache
   - Tests the search functionality for Hugging Face models

2. **Ollama Search with Hugging Face Fallback**
   - Tests that searching for "bie" in Ollama triggers a fallback to Hugging Face
   - Validates that Bielik models are found and displayed in the results

3. **Ollama Installation Workflow**
   - Verifies that getLLM offers to install Ollama when it's not found
   - Tests the interactive installation process

4. **Model Selection Interface**
   - Tests the enhanced model selection interface with multiple sources
   - Validates that users can select models from different sources

5. **Direct Code Generation**
   - Tests the code generation capability of getLLM

## Running All Tests

To run all the declarative tests, you can use the following script:

```bash
#!/bin/bash

echo "Running all declarative tests for getLLM..."

# Ansible tests
echo "\n=== Running Ansible tests ==="
cd ansible && ansible-playbook -i inventory.yml test_getllm.yml

# Goss tests
echo "\n=== Running Goss tests ==="
cd ../goss && goss validate

# Robot Framework tests
echo "\n=== Running Robot Framework tests ==="
cd ../robot && robot getllm_tests.robot

# YAML tests
echo "\n=== Running YAML tests ==="
cd ../yaml_specs && python run_yaml_tests.py

# TOML tests
echo "\n=== Running TOML tests ==="
cd ../toml_manifests && python run_toml_tests.py

echo "\nAll tests completed!"
```

## Benefits of Declarative Testing

- **Self-documenting**: The test specifications clearly describe what is being tested
- **Maintainable**: Easier to update as the application evolves
- **Infrastructure as Code**: Tests can be version-controlled alongside the application code
- **Reusable**: Test patterns can be reused across different parts of the application
- **Language-agnostic**: Tests are defined in standard formats (YAML, JSON, TOML) rather than specific programming languages
