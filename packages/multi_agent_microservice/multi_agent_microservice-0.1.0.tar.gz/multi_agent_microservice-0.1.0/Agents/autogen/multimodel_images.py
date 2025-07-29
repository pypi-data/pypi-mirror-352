from agents.utils.utils import init

init()

import asyncio
from pathlib import Path
from autogen_agentchat.messages import MultiModalMessage
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken, Image
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="gpt-4o", seed=42, temperature=0)

    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        model_client=model_client,
    )

   # cancellation_token = CancellationToken()
    message = MultiModalMessage(
        content=["Here is an image:", Image.from_file(Path("img.png"))],
        source="user",
    )
    #response = await assistant.on_messages([message], cancellation_token)
    response = await assistant.run(task=message)
    assistant.run()
    print(response)

asyncio.run(main())