import unittest
import os
from drw import ifcontext, extract_context, is_context_positive, transform_context, ContextError

# Set environment variable for testing (replace with your API key or mock)
os.environ["GEMINI_API_KEY"] = "AIzaSyCXejkhJvKMfJWYZ7ZBzEn2xlFgYSJhjmk"

class TestDrwLibrary(unittest.TestCase):
    def test_ifcontext_color(self):
        @ifcontext("The sky is blue", "is talking about color")
        def test_func():
            return "Color detected"
        result = test_func()
        self.assertEqual(result, "Color detected")
    
    def test_ifcontext_no_match(self):
        @ifcontext("The sky is clear", "is talking about color")
        def test_func():
            return "Should not reach here"
        with self.assertRaises(ContextError):
            test_func()
    
    def test_extract_context(self):
        result = extract_context("The sky is blue and red", "colors")
        self.assertIsInstance(result, list)
        self.assertIn("blue", result)
    
    def test_is_context_positive(self):
        result = is_context_positive("I am so happy today!")
        self.assertTrue(result)
    
    def test_transform_context(self):
        result = transform_context("Hey, this is cool!", "make formal")
        self.assertIsInstance(result, str)
        self.assertIn("Dear", result)

if __name__ == "__main__":
    unittest.main()