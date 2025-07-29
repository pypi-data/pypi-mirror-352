import os
import google.generativeai as genai

# Configure Gemini API (expects API key in environment variable)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize Gemini 1.5 Flash model
model = genai.GenerativeModel("gemini-1.5-flash")

class ContextError(Exception):
    """Custom exception for context-related errors."""
    pass

def query_llm(prompt):
    """
    Queries the Gemini 1.5 Flash model with the given prompt.
    Returns a dictionary with 'result' and 'details' based on the response.
    """
    try:
        response = model.generate_content(prompt)
        # Process response based on expected context
        if "Does" in prompt and "match the context" in prompt:
            # For ifcontext: expect a boolean-like response
            result = "yes" in response.text.lower() or "true" in response.text.lower()
            details = response.text
        elif "Extract" in prompt:
            # For extract_context: expect a list or text to parse
            result = response.text.split(",") if "," in response.text else [response.text]
            result = [item.strip() for item in result if item.strip()]
            details = f"Extracted: {result}"
        elif "Is the sentiment" in prompt:
            # For is_context_positive: expect a boolean-like response
            result = "positive" in response.text.lower()
            details = response.text
        elif "Transform" in prompt:
            # For transform_context: expect transformed text
            result = response.text.strip()
            details = "Transformed text"
        else:
            result = False
            details = "Unknown prompt type"
        return {"result": result, "details": details}
    except Exception as e:
        raise ContextError(f"LLM query failed: {str(e)}")

def ifcontext(variable, context_query):
    """
    Decorator-like function that checks if variable matches context_query using LLM.
    If true, executes the provided function.
    
    Example:
        @ifcontext("The sky is blue", "is talking about color")
        def my_function():
            print("This is about colors!")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            prompt = f"Does '{variable}' match the context: {context_query}?"
            llm_response = query_llm(prompt)
            if llm_response["result"]:
                return func(*args, **kwargs)
            else:
                raise ContextError(f"Context check failed: {llm_response['details']}")
        return wrapper
    return decorator

def extract_context(variable, context_type):
    """
    Extracts specific information from variable based on context_type.
    
    Example:
        result = extract_context("The sky is blue", "colors")
        # Returns: ['blue']
    """
    prompt = f"Extract {context_type} from '{variable}'"
    llm_response = query_llm(prompt)
    return llm_response["result"]

def is_context_positive(variable):
    """
    Checks if the sentiment of the variable is positive.
    
    Example:
        result = is_context_positive("I am so happy today!")
        # Returns: True
    """
    prompt = f"Is the sentiment of '{variable}' positive?"
    llm_response = query_llm(prompt)
    return llm_response["result"]

def transform_context(variable, transformation):
    """
    Transforms the variable's content based on the specified transformation.
    
    Example:
        result = transform_context("Hey, this is cool!", "make formal")
        # Returns: "Dear, this is excellent!"
    """
    prompt = f"Transform '{variable}' to {transformation}"
    llm_response = query_llm(prompt)
    return llm_response["result"]