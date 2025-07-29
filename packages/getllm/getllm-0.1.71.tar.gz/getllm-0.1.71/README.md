# getllm

![getllm-interactive.png](getllm-interactive.png)

## PyLama Ecosystem Navigation

| Project | Description | Links |
|---------|-------------|-------|
| **GetLLM** | LLM model management and code generation | [GitHub](https://github.com/py-lama/getllm) · [PyPI](https://pypi.org/project/getllm/) · [Docs](https://py-lama.github.io/getllm/) |
| **DevLama** | Python code generation with Ollama | [GitHub](https://github.com/py-lama/devlama) · [Docs](https://py-lama.github.io/devlama/) |
| **LogLama** | Centralized logging and environment management | [GitHub](https://github.com/py-lama/loglama) · [PyPI](https://pypi.org/project/loglama/) · [Docs](https://py-lama.github.io/loglama/) |
| **APILama** | API service for code generation | [GitHub](https://github.com/py-lama/apilama) · [Docs](https://py-lama.github.io/apilama/) |
| **BEXY** | Sandbox for executing generated code | [GitHub](https://github.com/py-lama/bexy) · [Docs](https://py-lama.github.io/bexy/) |
| **JSLama** | JavaScript code generation | [GitHub](https://github.com/py-lama/jslama) · [NPM](https://www.npmjs.com/package/jslama) · [Docs](https://py-lama.github.io/jslama/) |
| **JSBox** | JavaScript sandbox for executing code | [GitHub](https://github.com/py-lama/jsbox) · [NPM](https://www.npmjs.com/package/jsbox) · [Docs](https://py-lama.github.io/jsbox/) |
| **SheLLama** | Shell command generation | [GitHub](https://github.com/py-lama/shellama) · [PyPI](https://pypi.org/project/shellama/) · [Docs](https://py-lama.github.io/shellama/) |
| **WebLama** | Web application generation | [GitHub](https://github.com/py-lama/weblama) · [Docs](https://py-lama.github.io/weblama/) |

## Author

**Tom Sapletta** — DevOps Engineer & Systems Architect

- 💻 15+ years in DevOps, Software Development, and Systems Architecture
- 🏢 Founder & CEO at Telemonit (Portigen - edge computing power solutions)
- 🌍 Based in Germany | Open to remote collaboration
- 📚 Passionate about edge computing, hypermodularization, and automated SDLC

[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)](https://github.com/tom-sapletta-com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white)](https://linkedin.com/in/tom-sapletta-com)
[![ORCID](https://img.shields.io/badge/ORCID-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0000-6327-2810)
[![Portfolio](https://img.shields.io/badge/Portfolio-000000?style=flat&logo=about.me&logoColor=white)](https://www.digitname.com/)

## Support This Project

If you find this project useful, please consider supporting it:

- [GitHub Sponsors](https://github.com/sponsors/tom-sapletta-com)
- [Open Collective](https://opencollective.com/tom-sapletta-com)
- [PayPal](https://www.paypal.me/softreck/10.00)
- [Donate via Softreck](https://donate.softreck.dev)

---

getllm is a Python package for managing LLM models with Ollama integration and generating Python code. It allows you to install, list, set the default model, update the model list, and generate code using LLM models. GetLLM is part of the PyLama ecosystem and integrates with LogLama as the primary service for centralized logging and environment management.

![slides.svg](slides.svg)

## Features

- **Code Generation**: Generate Python code using LLM models
- **Model Management**: Install, list, and select models
- **Hugging Face Integration**: Search and install models from Hugging Face
- **Automatic Model Installation**: Automatically install models when they are not found
- **Multiple Ollama Installation Options**:
  - Direct installation using official script
  - Docker-based installation
  - Bexy sandbox for testing
  - Mock mode for development without Ollama
- **Fallback Mechanisms**: Use fallback models when the requested model is not available
- **Environment Configuration**: Configure Ollama through environment variables
- **Special Model Handling**: Special installation process for SpeakLeash Bielik models
- **Mock Mode**: Support for mock mode without requiring Ollama
- **Interactive Mode**: Interactive CLI for model selection and code generation
- **Template System**: Generate code with awareness of platform, dependencies, and more
- **Code Execution**: Execute generated code directly

## LogLama Integration

PyLLM integrates with LogLama as the primary service in the PyLama ecosystem. This integration provides:

- **Centralized Environment Management**: Environment variables are loaded from the central `.env` file in the `devlama` directory
- **Shared Configuration**: Model configurations are shared across all PyLama components
- **Dependency Management**: Dependencies are validated and installed by LogLama
- **Service Orchestration**: Services are started in the correct order using LogLama CLI
- **Centralized Logging**: All PyLLM operations are logged to the central LogLama system
- **Structured Logging**: Logs include component context for better filtering and analysis
- **Health Monitoring**: LogLama monitors PyLLM service health and availability

---

## General Diagram (Mermaid)
```mermaid
graph TD
    A[User] -->|CLI/Interactive| B[getllm/cli.py]
    B --> C[models.py]
    B --> D[interactive_cli.py]
    C --> E[LogLama Central .env]
    C --> F[Ollama API]
    D --> B
    G[LogLama] --> E
```

---

## ASCII Diagram: CLI Command Flow
```
User
    |
    v
+-----------------+
|   getllm CLI     |
+-----------------+
    |
    v
+-----------------+
|   models.py     |
+-----------------+
    |
+-----------------+
| LogLama Central |
|    .env File    |
+-----------------+
    |
+-----------------+
|  Ollama API     |
+-----------------+
```

---

## Usage

### Basic Usage

```bash
# Start interactive mode
getllm -i

# List available models
getllm list

# Install a model
getllm install codellama:7b

# Set default model
getllm set-default codellama:7b

# Search for models on Hugging Face
getllm --search bielik

# Update models list from Hugging Face
getllm --update-hf
```


### Model Management

```bash
# List available models
getllm list

# Install a model
getllm install codellama:7b

# List installed models
getllm installed

# Set default model
getllm set-default codellama:7b

# Show default model
getllm default

# Update models list from Ollama
getllm update
```

### Hugging Face Integration

The Hugging Face integration allows you to search for and install models directly from Hugging Face:

```bash
# Search for models on Hugging Face
getllm --search bielik

# Update models list from Hugging Face
getllm --update-hf
```

## Testing

For comprehensive testing instructions, please see [TEST.md](TEST.md).

The TEST.md file includes:
- Docker-based testing environment setup
- Local testing instructions
- Troubleshooting common test issues
- Continuous integration information

## Known Issues

### Ollama Dependency Error

When running `getllm --search` or other commands that interact with Ollama, you might encounter this error:

```
Error installing model: [Errno 2] No such file or directory: 'ollama'
```

This happens because getllm requires the Ollama binary to be installed and available in your PATH.

#### Solutions:

1. **Install Ollama**: Follow the instructions at [ollama.com](https://ollama.com) to install Ollama on your system.

2. **Use Mock Mode**: If you can't install Ollama, use the mock mode:
   ```bash
   getllm --mock --search llama
   ```

3. **Use Docker Testing Environment**: Use our Docker testing environment which includes Ollama:
   ```bash
   make docker-test-with-ollama
   ```

### Other Known Issues

- **Direct Code Generation**: The direct code generation functionality (e.g., `getllm "create a function"`) is currently experiencing timeout issues with the Ollama API. Use the interactive mode (`getllm -i`) for code generation in the meantime.

- **Timeout Errors**: When using direct code generation, you might encounter timeout errors like `ReadTimeoutError: HTTPConnectionPool(host='localhost', port=11434): Read timed out`. This indicates that the Ollama server is not responding in time, which could be due to:
  - The model is too large for your system's resources
  - The Ollama server is busy with other requests
  - The prompt requires too much processing time

- **Workaround**: For now, the recommended approach is to use the interactive mode (`getllm -i`), which provides a more stable interface for code generation and model management.

### Interactive Mode

```bash
# Start interactive mode
getllm -i

# Start interactive mode with mock implementation
getllm -i --mock
```

---

## Installation

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .  # This is important! Always install in development mode before starting
```

> **IMPORTANT**: Always run `pip install -e .` before starting the project to ensure all dependencies are properly installed and the package is available in development mode.

---

## Using the Makefile

PyLLM includes a Makefile to simplify common development tasks:

```bash
# Set up the project (creates a virtual environment and installs dependencies)
make setup

# Run the API server (default port 8001)
make run

# Run the API server on a custom port
make run PORT=8080

# The run-port command is also available for backward compatibility
make run-port PORT=8080

# Run tests
make test

# Format code with black
make format

# Lint code with flake8
make lint

# Clean up project (remove __pycache__, etc.)
make clean

# Show all available commands
make help
```

---

## Key Files

- `getllm/cli.py` – main CLI
- `getllm/interactive_cli.py` – interactive shell with menu and cursor selection
- `getllm/models.py` – model logic, .env/env.example handling, Ollama integration
- `.env`/`env.example` – environment config and default model

---

## Example Usage

Search polish moel bielik in huggingface
```bash
getllm --search bielik
```
from huggingface 

```bash
Searching for models matching 'bielik' on Hugging Face...
Searching for models matching 'bielik' on Hugging Face...
? Select a model to install: (Use arrow keys)
 » speakleash/Bielik-11B-v2.3-Instruct-FP8            Unknown    Downloads: 26,103 |
   speakleash/Bielik-11B-v2.3-Instruct-GGUF           Unknown    Downloads: 2,203 |
   speakleash/Bielik-4.5B-v3.0-Instruct-GGUF          Unknown    Downloads: 967 |
   speakleash/Bielik-7B-Instruct-v0.1-GGUF            Unknown    Downloads: 712 |
   speakleash/Bielik-1.5B-v3.0-Instruct-GGUF          Unknown    Downloads: 423 |
   bartowski/Bielik-11B-v2.2-Instruct-GGUF            Unknown    Downloads: 382 |
   gaianet/Bielik-4.5B-v3.0-Instruct-GGUF             Unknown    Downloads: 338 |
   second-state/Bielik-1.5B-v3.0-Instruct-GGUF        Unknown    Downloads: 314 |
   second-state/Bielik-4.5B-v3.0-Instruct-GGUF        Unknown    Downloads: 306 |
   DevQuasar/speakleash.Bielik-4.5B-v3.0-Instruct-GGUF Unknown    Downloads: 219 |
   DevQuasar/speakleash.Bielik-1.5B-v3.0-Instruct-GGUF Unknown    Downloads: 219 |
   gaianet/Bielik-11B-v2.3-Instruct-GGUF              Unknown    Downloads: 173 |
   tensorblock/Bielik-11B-v2.2-Instruct-GGUF          Unknown    Downloads: 168 |
   speakleash/Bielik-11B-v2.2-Instruct-GGUF           Unknown    Downloads: 162 |
   mradermacher/Bielik-11B-v2-i1-GGUF                 Unknown    Downloads: 147 |
   gaianet/Bielik-1.5B-v3.0-Instruct-GGUF             Unknown    Downloads: 145 |
   QuantFactory/Bielik-7B-v0.1-GGUF                   Unknown    Downloads: 135 |
   second-state/Bielik-11B-v2.3-Instruct-GGUF         Unknown    Downloads: 125 |
   RichardErkhov/speakleash_-_Bielik-11B-v2.1-Instruct-gguf Unknown    Downloads: 113 |
   mradermacher/Bielik-7B-v0.1-GGUF                   Unknown    Downloads: 94 |
   Cancel
```

on local environment
```bash
Searching for models matching 'bielik' on Hugging Face...
Searching for models matching 'bielik' on Hugging Face...
? Select a model to install: speakleash/Bielik-1.5B-v3.0-Instruct-GGUF          Unknown    Downloads: 423 | 
? Do you want to install this model now? Yes

Detected SpeakLeash Bielik model: speakleash/Bielik-1.5B-v3.0-Instruct-GGUF
Starting special installation process...

Found existing Bielik model installation: bielik-custom-1747866289:latest
Using existing model instead of downloading again.
Increased API timeout to 120 seconds for Bielik model.
Updated .env file with model settings: ~/getllm/.env
```    

### List available models
```bash
getllm list
```

### Install a model
```bash
getllm install deepseek-coder:6.7b
```

### Set default model
```bash
getllm set-default deepseek-coder:6.7b
```

### Show default model
```bash
getllm default
```

### Update model list from Ollama
```bash
getllm update
```

### Run interactive mode (menu, cursor selection)
```bash
getllm -i
```

---

## set_default_model function flow (Mermaid)
```mermaid
flowchart TD
    S[Start] --> C{Does .env exist?}
    C -- Yes --> R[Update OLLAMA_MODEL in .env]
    C -- No --> K[Copy env.example to .env]
    K --> R
    R --> E[End]
```

---

## Interactive mode - menu (ASCII)
```
+--------------------------------+
|  getllm - interactive mode       |
+--------------------------------+
| > List available models         |
|   Show default model           |
|   List installed models        |
|   Install model                |
|   Set default model            |
|   Update model list            |
|   Test default model           |
|   Exit                         |
+--------------------------------+
  (navigation: arrow keys + Enter)
```

---

## Installation

```bash
pip install getllm
```

## Usage

### Basic Model Management

```python
from getllm import get_models, get_default_model, set_default_model, install_model

# Get available models
models = get_models()
for model in models:
    print(f"{model['name']} - {model.get('desc', '')}")

# Get the current default model
default_model = get_default_model()
print(f"Current default model: {default_model}")

# Set a new default model
set_default_model("codellama:7b")

# Install a model
install_model("deepseek-coder:6.7b")
```

### Direct Ollama Integration

```python
from getllm import OllamaServer

# Start the Ollama server if it's not already running
ollama = OllamaServer()

# Or create an OllamaServer instance with a specific model
ollama = OllamaServer(model="codellama:7b")

# Check if the model is available
if ollama.check_model_availability():
    print(f"Model {ollama.model} is available")
else:
    print(f"Model {ollama.model} is not available")

    # Install the model
    if ollama.install_model(ollama.model):
        print(f"Successfully installed {ollama.model}")

# List installed models
installed_models = ollama.list_installed_models()
for model in installed_models:
    print(f"Installed model: {model['name']}")
```

## Ollama Installation Options

GetLLM now offers multiple ways to install and use Ollama:

### 1. Direct Installation (Recommended)

Installs Ollama directly on your system using the official installation script:

```bash
# When prompted during model search or installation
$ getllm --search bielik
# Select 'Install Ollama directly (recommended)' when prompted
```

### 2. Docker-based Installation

Installs and runs Ollama in a Docker container:

```bash
# When prompted during model search or installation
$ getllm --search bielik
# Select 'Install Ollama using Docker' when prompted
```

Requires Docker to be installed on your system.

### 3. Bexy Sandbox

Runs Ollama in a sandboxed environment using the bexy package:

```bash
# When prompted during model search or installation
$ getllm --search bielik
# Select 'Use bexy sandbox for testing' when prompted
```

Requires the bexy package to be available in your project.

### 4. Mock Mode

Run getllm without Ollama for testing and development:

```bash
# Use the --mock flag with any command
$ getllm --mock --search bielik
$ getllm --mock code 'Write a function to calculate factorial'

# Or select 'Continue in mock mode' when prompted during installation
```

## Testing

GetLLM includes several test suites to ensure all features work correctly:

```bash
# Run unit tests
make test

# Test command-line functionality
make test-commands

# Test installation options
make test-installation

# Test model installation
make test-models

# Run all tests
make test-all
```

## Environment Variables

The package uses the following environment variables for Ollama integration:

- `OLLAMA_PATH`: Path to the Ollama executable (default: 'ollama')
- `OLLAMA_MODEL`: Default model to use (default: 'codellama:7b')
- `OLLAMA_FALLBACK_MODELS`: Comma-separated list of fallback models (default: 'codellama:7b,phi3:latest,tinyllama:latest')
- `OLLAMA_AUTO_SELECT_MODEL`: Whether to automatically select an available model if the requested model is not found (default: 'true')
- `OLLAMA_AUTO_INSTALL_MODEL`: Whether to automatically install a model when it's not found (default: 'true')
- `OLLAMA_TIMEOUT`: API timeout in seconds (default: '30')

These variables can be set in a .env file in the project root directory or in the system environment.

## License
This project is licensed under the Apache 2.0 License (see LICENSE file).
