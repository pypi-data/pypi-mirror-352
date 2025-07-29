from agents.utils.utils import init

init()

from datetime import date
from pydantic_ai import Agent
from pydantic import BaseModel


class User(BaseModel):
    """Definition of a user"""
    id: int
    name: str
    dob: date


agent = Agent(
    'openai:gpt-4o',
    result_type=User,
    system_prompt='Extract information about the user',
)
result = agent.run_sync('The user with ID 123 is called Samuel, born on Jan 28th 87')
print(result.data)

from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

result_sync = agent.run_sync('What is the capital of Italy?')
print(result_sync.data)


