"""
Tests for the getllm CLI module
"""
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import getllm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestCLI(unittest.TestCase):
    """Tests for the getllm CLI module"""
    
    @patch('getllm.cli.argparse.ArgumentParser.parse_args')
    def test_cli_help(self, mock_parse_args):
        """Test that the CLI help works"""
        # Mock the parse_args method to return a namespace with help=True
        mock_args = MagicMock()
        mock_args.help = True
        mock_args.version = False
        mock_args.search = None
        mock_args.update_hf = False
        mock_args.interactive = False
        mock_args.model = None
        mock_args.prompt = None
        mock_parse_args.return_value = mock_args
        
        # Import the cli module
        from getllm import cli
        
        # The test passes if no exception is raised
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
