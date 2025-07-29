from agents import function_tool

from agentsapi.utils.utils import init

init()
from openai import OpenAI

# Initialize the client
client = OpenAI(
)

@function_tool
def web_search(query: str) -> str:
    """
    Search the web for information.

    Args:
        query: The search query

    Returns:
        Search results from the web
    """
    # Use OpenAI's built-in web search
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}],
        tools=[{"type": "web_search"}]
    )


    # Extract the search results from the response
    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        search_results = tool_calls[0].function.arguments
        return f"Web search results for: {query}\n\n{search_results}"
    else:
        return f"No search results found for: {query}"