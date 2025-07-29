#!/usr/bin/env python3

"""
YAML Test Runner for getLLM
Executes tests defined in YAML specifications
"""

import os
import sys
import yaml
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any, Union


class YamlTestRunner:
    """
    Executes tests defined in YAML specifications
    """
    def __init__(self, spec_file: str):
        self.spec_file = spec_file
        self.project_root = Path(__file__).parent.parent.parent
        self.specs = self._load_specs()
        self.env_vars = os.environ.copy()
        self._setup_environment()

    def _load_specs(self) -> Dict:
        """Load test specifications from YAML file"""
        try:
            with open(self.spec_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading test specifications: {e}")
            sys.exit(1)

    def _setup_environment(self):
        """Set up environment variables for tests"""
        if 'setup' in self.specs and 'environment' in self.specs['setup']:
            for env_var in self.specs['setup']['environment']:
                for key, value in env_var.items():
                    # Replace variables in the value
                    if isinstance(value, str):
                        value = value.replace("${PROJECT_ROOT}", str(self.project_root))
                    self.env_vars[key] = value

    def _replace_vars(self, command: str) -> str:
        """Replace variables in command string"""
        for key, value in self.env_vars.items():
            command = command.replace(f"${{{key}}}", str(value))
        return command

    def run_prerequisites(self) -> bool:
        """Run prerequisite checks"""
        if 'setup' not in self.specs or 'prerequisites' not in self.specs['setup']:
            return True

        print("\n🔍 Running prerequisites...")
        for prereq in self.specs['setup']['prerequisites']:
            command = self._replace_vars(prereq['command'])
            expected_exit_code = prereq.get('expected_exit_code', 0)
            error_message = prereq.get('error_message', f"Prerequisite failed: {command}")

            print(f"  Running: {command}")
            result = subprocess.run(command, shell=True, env=self.env_vars,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != expected_exit_code:
                print(f"❌ {error_message}")
                print(f"  Exit code: {result.returncode} (expected {expected_exit_code})")
                print(f"  Error: {result.stderr.decode('utf-8')}")
                return False

        print("✅ All prerequisites passed")
        return True

    def run_test_case(self, test_case: Dict) -> bool:
        """Run a single test case"""
        test_id = test_case.get('id', 'unknown')
        test_name = test_case.get('name', 'Unnamed test')
        description = test_case.get('description', '')

        print(f"\n🧪 Running test: {test_name} [{test_id}]")
        if description:
            print(f"  Description: {description}")

        if 'steps' not in test_case:
            print("❌ No steps defined for this test")
            return False

        for i, step in enumerate(test_case['steps']):
            command = self._replace_vars(step['command'])
            expected_exit_code = step.get('expected_exit_code', 0)
            expected_output = step.get('expected_output_contains', [])
            if isinstance(expected_output, str):
                expected_output = [expected_output]
            error_message = step.get('error_message', f"Step failed: {command}")

            print(f"  Step {i+1}: {command}")
            result = subprocess.run(command, shell=True, env=self.env_vars,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Check exit code
            if result.returncode != expected_exit_code:
                print(f"❌ {error_message}")
                print(f"  Exit code: {result.returncode} (expected {expected_exit_code})")
                print(f"  Error: {result.stderr.decode('utf-8')}")
                return False

            # Check output
            output = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
            for expected in expected_output:
                if expected not in output:
                    print(f"❌ {error_message}")
                    print(f"  Expected output not found: '{expected}'")
                    return False

        print(f"✅ Test passed: {test_name}")
        return True

    def validate_files(self) -> bool:
        """Validate files according to specifications"""
        if 'validations' not in self.specs or 'model_cache_files' not in self.specs['validations']:
            return True

        print("\n🔍 Validating files...")
        all_valid = True

        for file_spec in self.specs['validations']['model_cache_files']:
            path = os.path.expanduser(file_spec['path'])
            should_exist = file_spec.get('should_exist', True)
            print(f"  Checking: {path}")

            if os.path.exists(path):
                if not should_exist:
                    print(f"❌ File exists but should not: {path}")
                    all_valid = False
                    continue

                # Content validation if specified
                if 'content_validation' in file_spec:
                    validation = file_spec['content_validation']
                    try:
                        with open(path, 'r') as f:
                            content = json.load(f)

                        # Simple JSON path implementation
                        if 'json_path' in validation:
                            json_path = validation['json_path']
                            if json_path.startswith('$[?(@'):
                                # Handle filter expression for Bielik models
                                if 'bielik' in json_path:
                                    if isinstance(content, list):
                                        results = [m for m in content 
                                                  if ('name' in m and 'bielik' in m['name'].lower()) or 
                                                     ('id' in m and 'bielik' in m['id'].lower())]
                                    elif 'models' in content and isinstance(content['models'], list):
                                        results = [m for m in content['models'] 
                                                  if ('name' in m and 'bielik' in m['name'].lower()) or 
                                                     ('id' in m and 'bielik' in m['id'].lower())]
                                    else:
                                        results = []
                            elif json_path == '$.total_models':
                                results = content.get('total_models', 0) if isinstance(content, dict) else 0
                            else:
                                results = None

                            # Validation checks
                            if 'should_not_be_empty' in validation and validation['should_not_be_empty']:
                                if not results:
                                    error_msg = validation.get('error_message', f"Empty results for {json_path}")
                                    print(f"❌ {error_msg}")
                                    all_valid = False
                                else:
                                    print(f"  ✅ Found {len(results) if isinstance(results, list) else results} results")

                            if 'should_be_greater_than' in validation:
                                min_value = validation['should_be_greater_than']
                                value = len(results) if isinstance(results, list) else results
                                if value <= min_value:
                                    error_msg = validation.get('error_message', 
                                                              f"Value {value} not greater than {min_value}")
                                    print(f"❌ {error_msg}")
                                    all_valid = False
                                else:
                                    print(f"  ✅ Value {value} is greater than {min_value}")

                    except Exception as e:
                        print(f"❌ Error validating file content: {e}")
                        all_valid = False
            else:
                if should_exist:
                    print(f"❌ File does not exist: {path}")
                    all_valid = False
                else:
                    print(f"  ✅ File correctly does not exist")

        if all_valid:
            print("✅ All file validations passed")
        return all_valid

    def run_all_tests(self) -> bool:
        """Run all test cases"""
        if not self.run_prerequisites():
            return False

        if 'test_cases' not in self.specs:
            print("❌ No test cases defined in specifications")
            return False

        all_passed = True
        for test_case in self.specs['test_cases']:
            if not self.run_test_case(test_case):
                all_passed = False

        # Run file validations
        if not self.validate_files():
            all_passed = False

        return all_passed


if __name__ == "__main__":
    spec_file = sys.argv[1] if len(sys.argv) > 1 else "test_specifications.yaml"
    runner = YamlTestRunner(spec_file)
    success = runner.run_all_tests()

    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
