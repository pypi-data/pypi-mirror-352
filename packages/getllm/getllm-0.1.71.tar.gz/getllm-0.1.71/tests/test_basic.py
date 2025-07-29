"""
Basic tests for the getllm package
"""
import unittest
import os
import sys

# Add the parent directory to the path so we can import getllm
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestBasic(unittest.TestCase):
    """Basic tests for the getllm package"""
    
    def test_import(self):
        """Test that the package can be imported"""
        try:
            import getllm
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import getllm package")
    
    def test_version(self):
        """Test that the package has a version"""
        import getllm
        self.assertTrue(hasattr(getllm, '__version__'))
        self.assertIsInstance(getllm.__version__, str)

if __name__ == "__main__":
    unittest.main()
