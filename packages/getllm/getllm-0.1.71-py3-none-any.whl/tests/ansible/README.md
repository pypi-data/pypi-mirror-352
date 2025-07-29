# getllm End-to-End Tests with Ansible

This directory contains Ansible playbooks for end-to-end testing of the getllm tool. These tests verify that the integration between Hugging Face and Ollama works correctly in a real environment.

## Requirements

- Ansible installed on your system
- Python 3.6 or higher
- getllm package installed

## Running the Tests

To run the end-to-end tests, use the following command from the getllm directory:

```bash
ansible-playbook tests/ansible/test_getllm.yml -v
```

The `-v` flag increases verbosity to see more details about the test execution.

## Test Coverage

The end-to-end tests cover the following functionality:

1. Listing available models
2. Searching for Hugging Face models (including Bielik models)
3. Searching for Ollama models
4. Generating code directly from the command line

## Mock Mode

By default, the tests run in mock mode to avoid requiring Ollama to be installed. If you want to run the tests against a real Ollama installation, modify the `mock_mode` variable in the playbook to an empty string:

```yaml
vars:
  mock_mode: ""  # Remove --mock flag to use real Ollama
```

## Troubleshooting

If the tests fail, check the following:

1. Make sure getllm-cli is executable
2. Verify that the path to getllm-cli in the playbook is correct
3. Check if the required Python packages are installed
4. If not using mock mode, ensure Ollama is installed and running
