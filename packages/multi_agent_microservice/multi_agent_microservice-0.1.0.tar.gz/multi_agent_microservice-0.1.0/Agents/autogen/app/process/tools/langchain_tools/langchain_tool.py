# app/process/tools/langchain_tools.py
from langchain_core.tools import tool, Tool

from typing import Annotated
from pydantic import BaseModel, Field

class AppToolInput(BaseModel):
    query: Annotated[str, Field(description="The query to process.")]


def app_tool(query: AppToolInput) -> str:
    """An example LangChain tool that processes a query."""
    return f"Processed query: {query.query}"

langchain_tool = Tool(
    name="app_tool",
    func=app_tool,
    description="An example LangChain tool that processes a query.",
    args_schema=AppToolInput,
)
# Wrap the function in a LangChain Tool object
# langchain_tool = Tool(
#     name="langchain_tool",
#     func=langchain_example_tool,
#     description="A LangChain tool that processes a query."
# )