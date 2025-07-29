from agents import Agent, Runner, function_tool
from agents.tracing import trace
from agentsapi.utils.utils import init

init()

import asyncio


@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    weather_data = {
        "New York": "72°F, Sunny",
        "London": "65°F, Cloudy",
        "Tokyo": "80°F, Clear",
        "Paris": "70°F, Partly Cloudy"
    }
    return weather_data.get(city, f"Weather data not available for {city}")


async def main():
    # Create a trace for the entire workflow
    with trace(workflow_name="weather_inquiry"):
        agent = Agent(
            name="Weather Assistant",
            instructions="You are a helpful assistant that provides weather information when asked.",
            tools=[get_weather]
        )

        result = await Runner.run(
            agent,
            "What's the weather like in Tokyo and Paris?",
            run_config=RunConfig(
                workflow_name="weather_inquiry",
                trace_include_sensitive_data=True
            )
        )

        print(result.final_output)

        # You can access the trace information
        current_trace = get_current_trace()
        if current_trace:
            print(f"Trace ID: {current_trace.trace_id}")


if __name__ == "__main__":
    from agents import RunConfig
    from agents.tracing import get_current_trace

    asyncio.run(main())
