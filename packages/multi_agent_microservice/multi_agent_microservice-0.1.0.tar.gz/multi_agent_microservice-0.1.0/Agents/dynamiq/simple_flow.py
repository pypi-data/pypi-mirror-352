from dynamiq.nodes.llms.openai import OpenAI
from dynamiq.connections import OpenAI as OpenAIConnection
from dynamiq.prompts import Prompt, Message

from agents.utils.utils import init

# Define the prompt template for translation
prompt_template = """
Translate the following text into English: {{ text }}
"""
init()
import os
key=os.getenv("OPENAI_API_KEY")
# Create a Prompt object with the defined template
prompt = Prompt(messages=[Message(content=prompt_template, role="user")])

# Setup your LLM (Large Language Model) Node
llm = OpenAI(
    id="openai",  # Unique identifier for the node
    connection=OpenAIConnection(api_key=key),  # Connection using API key
    model="gpt-4o",  # Model to be used
    temperature=0.3,  # Sampling temperature for the model
    max_tokens=1000,  # Maximum number of tokens in the output
    prompt=prompt  # Prompt to be used for the model
)

# Run the LLM node with the input data
result = llm.run(
    input_data={
        "text": "Hola Mundo!"  # Text to be translated
    }
)

# Print the result of the translation
print(result.output)