// Jsonnet test configuration for getLLM
// A declarative approach to defining test cases using Jsonnet

// Define common variables
local project_root = std.extVar('PROJECT_ROOT');
local mock_mode = '--mock';

// Define test cases
local test_cases = [
  {
    id: 'huggingface-model-search',
    name: 'Hugging Face Model Search',
    description: 'Test searching for Bielik models in Hugging Face',
    steps: [
      {
        command: "echo -e 'search-hf\nbielik\nexit' | getllm %s -i" % mock_mode,
        expected_exit_code: 0,
        expected_output_contains: ['bielik', 'Bielik'],
        error_message: 'Failed to find Bielik models in Hugging Face search'
      }
    ]
  },
  {
    id: 'ollama-search-fallback',
    name: 'Ollama Search with Hugging Face Fallback',
    description: "Test Ollama search with fallback to Hugging Face for 'bie' query",
    steps: [
      {
        command: "echo -e 'search-ollama\nbie\nexit' | getllm %s -i" % mock_mode,
        expected_exit_code: 0,
        expected_output_contains: ['Searching Hugging Face GGUF models', 'Found Hugging Face GGUF models'],
        error_message: 'Hugging Face fallback not triggered for Ollama search'
      }
    ]
  },
  {
    id: 'model-installation',
    name: 'Model Installation Workflow',
    description: 'Test the model installation workflow',
    steps: [
      {
        command: "echo -e 'list\nexit' | getllm %s -i" % mock_mode,
        expected_exit_code: 0,
        expected_output_contains: 'available models',
        error_message: 'Available models not listed'
      }
    ]
  },
  {
    id: 'code-generation',
    name: 'Direct Code Generation',
    description: 'Test direct code generation capability',
    steps: [
      {
        command: "getllm %s 'Write a hello world program in Python'" % mock_mode,
        expected_exit_code: 0,
        expected_output_contains: 'print',
        error_message: 'Code generation failed to produce Python code'
      }
    ]
  },
  {
    id: 'ollama-installation',
    name: 'Ollama Installation Prompt',
    description: 'Test that getLLM offers to install Ollama when not found',
    steps: [
      {
        command: "echo -e 'n\nexit' | OLLAMA_PATH=/nonexistent/path getllm %s -i" % mock_mode,
        expected_exit_code: 0,
        expected_output_contains: 'install Ollama',
        error_message: 'Ollama installation prompt not shown'
      }
    ]
  }
];

// Define file validations
local file_validations = [
  {
    path: '~/.getllm/models/huggingface_models.json',
    should_exist: true,
    content_validation: {
      type: 'json_contains',
      pattern: 'bielik',
      case_sensitive: false,
      error_message: 'No Bielik models found in Hugging Face cache'
    }
  },
  {
    path: '~/.getllm/models/ollama_models.json',
    should_exist: true
  },
  {
    path: '~/.getllm/models/models_metadata.json',
    should_exist: true,
    content_validation: {
      type: 'json_property',
      property: 'total_models',
      comparison: 'greater_than',
      value: 0,
      error_message: 'No models found in metadata'
    }
  }
];

// Generate the final test configuration
{
  test_suite: {
    name: 'getLLM Functional Tests',
    description: 'Declarative test configuration for getLLM functionality',
    version: '1.0.0',
    created_at: '2025-05-29'
  },
  environment: {
    PYTHONPATH: project_root,
    MOCK_MODE: mock_mode
  },
  test_cases: test_cases,
  validations: file_validations
}
