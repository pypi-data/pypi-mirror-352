import unittest
from apexllm.core import hello

class TestCore(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(hello(), "Hello from apexllm!")

if __name__ == '__main__':
    unittest.main() 