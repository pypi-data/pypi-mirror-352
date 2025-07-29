from agentsapi.utils.utils import init
init()
from agents import Agent, Runner
import asyncio
async def main():
    # Create a simple agent with instructions
    agent = Agent(
        name="Greeting Assistant",
        instructions="You are a friendly assistant that greets users in their preferred language."
    )

    # Run the agent with a user input
    result = await Runner.run(agent, "Can you greet me in French?")

    # Print the final output
    print(result.final_output)
if __name__ == "__main__":
    asyncio.run(main())