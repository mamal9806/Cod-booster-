import unittest
from config import Config

class ConfigTests(unittest.TestCase):
    def test_valid_defaults(self):
        self.assertEqual(Config().validate().head_size, 32)

    def test_invalid_head_dimensions(self):
        with self.assertRaises(ValueError):
            Config(n_embd=63, n_head=2).validate()

if __name__ == "__main__":
    unittest.main()
