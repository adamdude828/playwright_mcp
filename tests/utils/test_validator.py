"""Test script for OutputValidator class."""
import os
from output_validator import OutputValidator


def main():
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-api-key'")
        return
    
    # Create test output similar to what we see from the MCP CLI
    test_output = """
╭──────────────────────────────────────────────────────────────────────────────╮
│                                Tool Response                                 │
│                                                                              │
│ [{'type': 'text', 'text': "{'session_id': 'chromium_4380506544', 'page_id':  │
│ 'page_4386223552', 'created_session': True, 'created_page': True, 'isError': │
│ False}"}]                                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
"""
    
    # Create validator instance
    validator = OutputValidator()
    
    # Test some validation questions
    questions = [
        "Does the output contain a session_id?",
        "Does the output indicate an error occurred?",
        "Is created_session set to True?",
        "Does the output contain a page_id?",
    ]
    
    print("Testing OutputValidator with sample MCP CLI output:")
    print("-" * 80)
    print(test_output)
    print("-" * 80)
    print("\nValidation Results:")
    
    for question in questions:
        try:
            result = validator.validate(test_output, question)
            print(f"\nQ: {question}")
            print(f"Raw answer: {result}")
            print(f"Boolean result: {bool(result)}")
        except Exception as e:
            print(f"\nError validating question: {question}")
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 