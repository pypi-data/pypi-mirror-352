#!/usr/bin/env python3

"""
TOML Test Runner for getLLM
Executes tests defined in TOML manifests
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Union

try:
    import tomli
except ImportError:
    try:
        import tomllib as tomli
    except ImportError:
        print("Error: Neither tomli nor tomllib found. Please install with: pip install tomli")
        sys.exit(1)


class TomlTestRunner:
    """
    Executes tests defined in TOML manifests
    """
    def __init__(self, manifest_file: str):
        self.manifest_file = manifest_file
        self.project_root = Path(__file__).parent.parent.parent
        self.manifest = self._load_manifest()
        self.env_vars = os.environ.copy()
        self._setup_environment()

    def _load_manifest(self) -> Dict:
        """Load test manifest from TOML file"""
        try:
            with open(self.manifest_file, 'rb') as f:
                return tomli.load(f)
        except Exception as e:
            print(f"Error loading test manifest: {e}")
            sys.exit(1)

    def _setup_environment(self):
        """Set up environment variables for tests"""
        if 'environment' in self.manifest:
            for key, value in self.manifest['environment'].items():
                # Replace variables in the value
                if isinstance(value, str):
                    value = value.replace("${PROJECT_ROOT}", str(self.project_root))
                self.env_vars[key] = value

    def _replace_vars(self, command: str) -> str:
        """Replace variables in command string"""
        for key, value in self.env_vars.items():
            command = command.replace(f"${{{key}}}", str(value))
        return command

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
            expected_output = step.get('expected_output', [])
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

    def run_validations(self) -> bool:
        """Run file and content validations"""
        if 'validations' not in self.manifest:
            return True

        print("\n🔍 Running validations...")
        all_passed = True

        for validation in self.manifest['validations']:
            validation_type = validation.get('type', '')
            path = os.path.expanduser(validation.get('path', ''))
            error_message = validation.get('error_message', f"Validation failed for {path}")

            print(f"  Validating: {path} ({validation_type})")

            if validation_type == 'file_exists':
                if not os.path.exists(path):
                    print(f"❌ {error_message}")
                    all_passed = False
                else:
                    print(f"  ✅ File exists: {path}")

            elif validation_type == 'file_content':
                if not os.path.exists(path):
                    print(f"❌ File does not exist: {path}")
                    all_passed = False
                    continue

                check_type = validation.get('check', '')
                
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        
                    if check_type == 'json_property':
                        # Parse JSON and check property
                        json_data = json.loads(content)
                        property_path = validation.get('property', '')
                        comparison = validation.get('comparison', 'equals')
                        target_value = validation.get('value', None)
                        
                        # Simple property access (no nested paths for now)
                        actual_value = json_data.get(property_path, None)
                        
                        if comparison == 'equals' and actual_value != target_value:
                            print(f"❌ {error_message}")
                            print(f"  Expected: {target_value}, Actual: {actual_value}")
                            all_passed = False
                        elif comparison == 'greater_than' and not (actual_value > target_value):
                            print(f"❌ {error_message}")
                            print(f"  Expected > {target_value}, Actual: {actual_value}")
                            all_passed = False
                        else:
                            print(f"  ✅ Property validation passed: {property_path}")
                            
                    elif check_type == 'json_contains':
                        # Check if JSON contains a pattern
                        pattern = validation.get('pattern', '')
                        case_sensitive = validation.get('case_sensitive', True)
                        
                        if not case_sensitive:
                            pattern = pattern.lower()
                            content = content.lower()
                            
                        if pattern not in content:
                            print(f"❌ {error_message}")
                            all_passed = False
                        else:
                            print(f"  ✅ Content contains pattern: {pattern}")
                            
                except Exception as e:
                    print(f"❌ Error validating file content: {e}")
                    all_passed = False

        if all_passed:
            print("✅ All validations passed")
        return all_passed

    def run_all_tests(self) -> bool:
        """Run all test cases"""
        if 'test_cases' not in self.manifest:
            print("❌ No test cases defined in manifest")
            return False

        all_passed = True
        for test_case in self.manifest['test_cases']:
            if not self.run_test_case(test_case):
                all_passed = False

        # Run validations
        if not self.run_validations():
            all_passed = False

        return all_passed


if __name__ == "__main__":
    manifest_file = sys.argv[1] if len(sys.argv) > 1 else "test_manifest.toml"
    runner = TomlTestRunner(manifest_file)
    success = runner.run_all_tests()

    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
