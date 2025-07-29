from agents import Agent, Runner

from agentsapi.utils.utils import init

init()

import asyncio
# Create specialized language agents
spanish_agent = Agent(
    name="spanish_agent",
    instructions="You are a helpful assistant that only speaks Spanish. Always respond in Spanish, regardless of the language of the question."
)
french_agent = Agent(
    name="french_agent",
    instructions="You are a helpful assistant that only speaks French. Always respond in French, regardless of the language of the question."
)
# Create a triage agent that can hand off to specialized agents
triage_agent = Agent(
    name="language_triage",
    instructions="""You are a language detection assistant. 
    Your job is to determine what language the user wants a response in.
    If they want Spanish, hand off to the spanish_agent.
    If they want French, hand off to the french_agent.
    If they don't specify a language or want English, respond directly in English.""",
    handoffs=[spanish_agent, french_agent]  # Add the specialized agents as handoffs
)
async def main():
    # Test with different language requests
    queries = [
        "Can you tell me about the Eiffel Tower in French?",
        "¿Puedes hablarme sobre el clima en Madrid?",
        "Tell me about the history of New York."
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        result = await Runner.run(triage_agent, query)
        print(f"Response: {result.final_output}")
if __name__ == "__main__":
    asyncio.run(main())