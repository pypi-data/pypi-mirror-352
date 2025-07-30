import unittest
import lumeo

class TestBasic(unittest.TestCase):
    def test_package_import(self):
        """Test that the lumeo package can be imported."""
        self.assertIsNotNone(lumeo)
        self.assertIsNotNone(lumeo.__version__, "Version should be defined")

if __name__ == '__main__':
    unittest.main()
