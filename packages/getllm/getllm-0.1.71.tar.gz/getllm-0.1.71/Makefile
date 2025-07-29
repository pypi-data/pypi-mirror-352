# Makefile for PyLLM

.PHONY: all setup clean test lint format run help venv docker-dev docker-test docker-run docker-clean docker-build docker-publish build publish test-package update-version publish-test build-and-publish

# Default values
PORT ?= 8001
HOST ?= 0.0.0.0

# Default target
all: help

# Create virtual environment if it doesn't exist
venv:
	@test -d venv || python3 -m venv venv

# Setup project
setup: venv
	@echo "Setting up PyLLM..."
	@. venv/bin/activate && pip install -e .
	@. venv/bin/activate && pip install setuptools wheel twine build

# Clean project
clean:
	@echo "Cleaning PyLLM..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

# Run tests
test: setup
	@echo "Testing PyLLM..."
	@. venv/bin/activate && venv/bin/python -m unittest discover

# Run command tests
test-commands: setup
	@echo "Testing PyLLM commands..."
	@chmod +x test_commands.sh
	@./test_commands.sh

# Test installation options
test-installation: setup
	@echo "Testing PyLLM installation options..."
	@chmod +x test_installation_options.sh
	@./test_installation_options.sh

# Test model installation
test-models: setup
	@echo "Testing PyLLM model installation..."
	@chmod +x test_model_installation.sh
	@./test_model_installation.sh

# Run all tests
test-all: test test-commands test-installation test-models
	@echo "All tests completed!"

# Lint code
lint: setup
	@echo "Linting PyLLM..."
	@. venv/bin/activate && flake8 getllm

# Format code
format: setup
	@echo "Formatting PyLLM..."
	@. venv/bin/activate && black getllm

# Run the API server
run: setup
	@echo "Running PyLLM API server on port $(PORT)..."
	@. venv/bin/activate && uvicorn getllm.api:app --host $(HOST) --port $(PORT)

# Run with custom port (for backward compatibility)
run-port: setup
	@echo "Running PyLLM API server on port $(PORT)..."
	@. venv/bin/activate && uvicorn getllm.api:app --host $(HOST) --port $(PORT)

# Docker testing targets
docker-build:
	@echo "Building Docker test images..."
	@cd ../tests && docker-compose -f docker-compose.test-getllm.yml build

docker-test: docker-build
	@echo "Running tests in Docker..."
	@cd ../tests && docker-compose -f docker-compose.test-getllm.yml run getllm-test

docker-test-cli: docker-build
	@echo "Running CLI tests in Docker..."
	@cd ../tests && docker-compose -f docker-compose.test-getllm.yml run getllm-test cli

docker-test-with-ollama: docker-build
	@echo "Running tests with Ollama in Docker..."
	@cd ../tests && docker-compose -f docker-compose.test-getllm.yml run getllm-test-with-ollama

docker-test-ansible: docker-build
	@echo "Running Ansible tests in Docker..."
	@cd ../tests && docker-compose -f docker-compose.test-getllm.yml run ansible-test

docker-interactive: docker-build
	@echo "Starting interactive Docker test environment..."
	@cd ../tests && docker-compose -f docker-compose.test-getllm.yml run --entrypoint /bin/bash getllm-test

docker-clean:
	@echo "Cleaning Docker test environment..."
	@cd ../tests && docker-compose -f docker-compose.test-getllm.yml down -v


# Build package
build: setup
	@echo "Building package using new build script..."
	@. venv/bin/activate && pip install -e . && pip install wheel twine build
	@. venv/bin/activate && python build.py

# Update version
update-version:
	@echo "Updating package version..."
	@python ../scripts/update_version.py

# Publish package to PyPI
publish: setup update-version
	@echo "Building and publishing package to PyPI automatically..."
	@. venv/bin/activate && python build_and_publish.py

# Build and publish in one step (non-interactive)
build-and-publish: setup
	@echo "Building and publishing package to PyPI in one step (non-interactive)..."
	@. venv/bin/activate && python build_and_publish.py

# Publish package to TestPyPI
publish-test: build update-version
	@echo "Publishing package to TestPyPI..."
	@. venv/bin/activate && twine check dist/* && twine upload --repository testpypi dist/*

# Publish package to TestPyPI with token
publish-test-token: build
	@echo "Publishing PyLLM package to TestPyPI using token..."
	@echo "Enter your TestPyPI token when prompted"
	@. venv/bin/activate && twine check dist/* && twine upload --non-interactive --repository testpypi dist/*

# Publish using the publish script
publish-script: build
	@echo "Publishing PyLLM package using the publish script..."
	@. venv/bin/activate && python scripts/publish.py

# Publish to TestPyPI using the publish script
publish-script-test: build
	@echo "Publishing PyLLM package to TestPyPI using the publish script..."
	@. venv/bin/activate && python scripts/publish.py --test

# Help
# Update project dependencies and environment
update: venv
	@echo "Updating PyLLM dependencies..."
	@. venv/bin/activate && pip install --upgrade pip setuptools wheel
	@. venv/bin/activate && pip install --upgrade -e .
	@. venv/bin/activate && pip install --upgrade -r requirements-dev.txt 2>/dev/null || echo "No requirements-dev.txt found, skipping..."

# Docker development environment
docker-build:
	@echo "Building development Docker image..."
	docker build -f Dockerfile.dev -t pyllm-dev .

docker-dev: docker-build
	@echo "Starting development container..."
	docker run -it --rm \
		-v $(PWD):/app \
		-p 8001:8001 \
		--name pyllm-dev \
		pyllm-dev

docker-test: docker-build
	@echo "Running tests in Docker..."
	docker run -it --rm \
		-v $(PWD):/app \
		pyllm-dev \
		bash -c "pytest tests/"

docker-run: docker-build
	@echo "Running application in Docker..."
	docker run -it --rm \
		-v $(PWD):/app \
		-p 8001:8001 \
		--name pyllm-run \
		pyllm-dev \
		uvicorn getllm.api:app --host 0.0.0.0 --port 8001

docker-clean:
	@echo "Cleaning Docker resources..."
	docker ps -a -q --filter "name=pyllm-*" | xargs -r docker rm -f 2>/dev/null || true
	docker images -q pyllm-* | xargs -r docker rmi -f 2>/dev/null || true
	docker volume ls -q -f dangling=true | xargs -r docker volume rm 2>/dev/null || true
	@. venv/bin/activate && pip install --upgrade -e ".[test]" 2>/dev/null || echo "No test extras found, skipping..."
	@echo "Dependencies updated successfully!"

help:
	@echo "PyLLM Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  update    - Update project dependencies and environment"
	@echo "  setup     - Set up the project"
	@echo "  clean     - Clean the project"
	@echo "  test      - Run unit tests"
	@echo "  test-commands - Run command tests"
	@echo "  test-installation - Test installation options"
	@echo "  test-models - Test model installation"
	@echo "  test-all   - Run all tests"
	@echo "  lint      - Lint the code"
	@echo "  format    - Format the code with black"
	@echo "  run       - Run the API server"
	@echo "  run-port PORT=8001 - Run the API server on a custom port"
	@echo "  build     - Build the package"
	@echo "  publish   - Publish the package to PyPI (requires .pypirc)"
	@echo "  publish-token - Publish the package to PyPI using a token"
	@echo "  publish-test - Publish the package to TestPyPI (requires .pypirc)"
	@echo "  publish-test-token - Publish the package to TestPyPI using a token"
	@echo "  publish-script - Publish using the publish script"
	@echo "  publish-script-test - Publish to TestPyPI using the publish script"
	@echo "  docker-build      - Build Docker test images"
	@echo "  docker-test       - Run tests in Docker"
	@echo "  docker-interactive - Start interactive Docker test environment"
	@echo "  docker-mock       - Start PyLLM mock service in Docker"
	@echo "  docker-clean      - Clean Docker test environment"
	@echo "  help      - Show this help message"
