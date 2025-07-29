drw
A Python library for context-aware operations using Google's Gemini 1.5 Flash model.
Installation
pip install drw

Setup
Set your Gemini API key as an environment variable:
export GEMINI_API_KEY='your-api-key-here'  # On Windows: set GEMINI_API_KEY=your-api-key-here

Get your API key from Google AI Studio.
Usage
from drw import ifcontext, extract_context, is_context_positive, transform_context

# Check if text is about colors
@ifcontext("The sky is blue", "is talking about color")
def my_function():
    print("This is about colors!")

my_function()  # Prints: This is about colors! (if Gemini confirms color context)

# Extract colors
colors = extract_context("The sky is blue and red", "colors")
print(colors)  # Prints: ['blue', 'red'] (or similar, based on Gemini response)

# Check sentiment
is_positive = is_context_positive("I am so happy today!")
print(is_positive)  # Prints: True (if Gemini detects positive sentiment)

# Transform text
formal_text = transform_context("Hey, this is cool!", "make formal")
print(formal_text)  # Prints: Dear, this is excellent! (or similar, based on Gemini)

License
MIT License
