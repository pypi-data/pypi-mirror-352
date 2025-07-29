import asyncio
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer

import os

os.environ['OPENAI_API_KEY'] = "xxxx"


from autogen.agentchat.contrib.web_surfer import WebSurferAgent
async def main() -> None:
web_researcher = WebSurferAgent(    # Define an agent
    name="WebResearcherAgent",    web_surfer_agent = MultimodalWebSurfer(
    system_message="Search for the latest articles or news on financial wellness programs by major US banks"
                   " (e.g., Chase, Bank of America, Wells Fargo, Citibank). Return relevant article summaries with source links.",        name="MultimodalWebSurfer",
    llm_config={"config_list": [...], "temperature": 0.2}        model_client=OpenAIChatCompletionClient(model="gpt-4o-2024-08-06"),
)    )

    # Define a team
    agent_team = RoundRobinGroupChat([web_surfer_agent], max_turns=3)

    # Run the team and stream messages to the console
    stream = agent_team.run_stream(task="Navigate to the AutoGen readme on GitHub.")
    await Console(stream)
    # Close the browser controlled by the agent
    await web_surfer_agent.close()


asyncio.run(main())

analyst = AssistantAgent(
    name="AnalystAgent",