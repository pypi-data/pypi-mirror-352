import sys
import os

# Add the src directory to Python path so we can import dof
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from dof.llm import LLMService

# Initialize the service
llm = LLMService()
messages = [
    {"role": "system", "content": "You are a helpful robotics assistant."},
    {"role": "user", "content": "What is a robot?"},
]
response = llm.get_chat_completion(messages)
print(response)
