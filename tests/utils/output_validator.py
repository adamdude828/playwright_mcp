"""Output validation utility using Claude's tool use functionality.

This utility provides a simple way to validate test output by asking questions
about it and getting strict yes/no answers using Claude's tool use feature.
"""
import os
from anthropic import Anthropic


class OutputValidator:
    """Validates test output by asking questions and getting yes/no answers."""
    
    def __init__(self):
        # Initialize Anthropic client
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        # Define the tool schema for strict yes/no answers
        self.tools = [{
            "name": "validate_output",
            "description": """Analyze the given test output and question, then return a strict yes/no answer.
            You must ONLY return true or false based on whether the output satisfies the question.
            Do not provide explanations or additional context.""",
            "input_schema": {
                "type": "object",
                "properties": {
                    "output": {
                        "type": "string",
                        "description": "The test output to analyze"
                    },
                    "question": {
                        "type": "string", 
                        "description": "The yes/no question to ask about the output"
                    },
                    "answer": {
                        "type": "boolean",
                        "description": "The answer to the question (true for yes, false for no)"
                    }
                },
                "required": ["output", "question", "answer"]
            }
        }]
        
        # Force the tool to be used
        self.tool_choice = {
            "type": "tool",
            "name": "validate_output"
        }
    
    def validate(self, output: str, question: str) -> bool:
        """Validate test output by asking a yes/no question.
        
        Args:
            output: The test output to analyze
            question: The yes/no question to ask about the output
            
        Returns:
            bool: True if the answer is yes, False if no
        """
        # Call Claude with tool use
        message = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            temperature=0,
            tools=self.tools,
            tool_choice=self.tool_choice,
            messages=[{
                "role": "user",
                "content": (
                    f"Here is some test output to analyze:\n\n{output}\n\n"
                    f"Question: {question}\n\n"
                    "Analyze the output and answer the question with true or false only."
                )
            }]
        )
        
        # Return the boolean answer from the tool call
        return bool(message.content[0].input['answer'])
        