from typing import Any, Dict, List
from app.utils import init

init()
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient


async def get_stock_data(symbol: str) -> Dict[str, Any]:
    """Get stock market data for a given symbol"""
    return {"price": 180.25, "volume": 1000000, "pe_ratio": 65.4, "market_cap": "700B"}


async def get_news(query: str) -> List[Dict[str, str]]:
    """Get recent news articles about a company"""
    return [
        {
            "title": "Tesla Expands Cybertruck Production",
            "date": "2024-03-20",
            "summary": "Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.",
        },
        {
            "title": "Tesla FSD Beta Shows Promise",
            "date": "2024-03-19",
            "summary": "Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.",
        },
        {
            "title": "Model Y Dominates Global EV Sales",
            "date": "2024-03-18",
            "summary": "Tesla's Model Y becomes best-selling electric vehicle worldwide, capturing significant market share.",
        },
    ]

model_client = OpenAIChatCompletionClient(
    model="gpt-4o",
    # api_key="YOUR_API_KEY",
)

planner = AssistantAgent(
    "planner",
    model_client=model_client,
    handoffs=["financial_analyst", "news_analyst", "writer"],
    system_message="""You are a research planning coordinator.
    Coordinate market research by delegating to specialized agents:
    - Financial Analyst: For stock data analysis
    - News Analyst: For news gathering and analysis
    - Writer: For compiling final report
    Always send your plan first, then handoff to appropriate agent.
    Always handoff to a single agent at a time.
    Use TERMINATE when research is complete.""",
)

financial_analyst = AssistantAgent(
    "financial_analyst",
    model_client=model_client,
    handoffs=["planner"],
    tools=[get_stock_data],
    system_message="""You are a financial analyst.
    Analyze stock market data using the get_stock_data tool.
    Provide insights on financial metrics.
    Always handoff back to planner when analysis is complete.""",
)

news_analyst = AssistantAgent(
    "news_analyst",
    model_client=model_client,
    handoffs=["planner"],
    tools=[get_news],
    system_message="""You are a news analyst.
    Gather and analyze relevant news using the get_news tool.
    Summarize key market insights from news.
    Always handoff back to planner when analysis is complete.""",
)

writer = AssistantAgent(
    "writer",
    model_client=model_client,
    handoffs=["planner"],
    system_message="""You are a financial report writer.
    Compile research findings into clear, concise reports.
    Always handoff back to planner when writing is complete.""",
)

# Define termination condition
text_termination = TextMentionTermination("TERMINATE")
termination = text_termination

research_team = Swarm(
    participants=[planner, financial_analyst, news_analyst, writer], termination_condition=termination
)

task = "Conduct market research for TSLA stock"


async def run_team_stream() -> None:
    await Console(research_team.run_stream(task=task))


# Use asyncio.run(...) if you are running this in a script.
#await run_team_stream()
import asyncio
asyncio.run(run_team_stream())

"""
/Users/welcome/anaconda3/envs/autogen_0_4/bin/python /Users/welcome/Library/Mobile Documents/com~apple~CloudDocs/Sai_Workspace/lang_server_app/DeepDive_GenAI/autogen_src_new/python/packages/autogen-studio/app/teams/swarm_workflow_team_2.py 
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_client" in AssistantAgentConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_context" in AssistantAgentConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_client_stream" in AssistantAgentConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_client" in SocietyOfMindAgentConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_client" in MagenticOneGroupChatConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_client" in SelectorGroupChatConfig has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_capabilities" in BaseOpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_info" in BaseOpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_capabilities" in OpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_info" in OpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_capabilities" in AzureOpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/_internal/_fields.py:132: UserWarning: Field "model_info" in AzureOpenAIClientConfigurationConfigModel has conflict with protected namespace "model_".

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.
  warnings.warn(
---------- user ----------
Conduct market research for TSLA stock
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/autogen_agentchat/agents/_assistant_agent.py:416: UserWarning: Both tool_calls and content are present in the message. This is unexpected. content will be ignored, tool_calls will be used.
  model_result = await self._model_client.create(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `HandoffMessage` with value `HandoffMessage(source='pl..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `HandoffMessage` with value `HandoffMessage(source='pl..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `HandoffMessage` with value `HandoffMessage(source='pl..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `HandoffMessage` with value `HandoffMessage(source='pl..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `HandoffMessage` with value `HandoffMessage(source='pl..., type='HandoffMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- planner ----------
[FunctionCall(id='call_QL9BHiwdfoKJ2IZIUVMa6agT', arguments='{}', name='transfer_to_financial_analyst')]
---------- planner ----------
[FunctionExecutionResult(content='Transferred to financial_analyst, adopting the role of financial_analyst immediately.', call_id='call_QL9BHiwdfoKJ2IZIUVMa6agT')]
---------- planner ----------
Transferred to financial_analyst, adopting the role of financial_analyst immediately.
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `ToolCallSummaryMessage` with value `ToolCallSummaryMessage(so...ToolCallSummaryMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- financial_analyst ----------
[FunctionCall(id='call_U52JmYQ75UpY1vbq6ERGHyUf', arguments='{"symbol":"TSLA"}', name='get_stock_data')]
---------- financial_analyst ----------
[FunctionExecutionResult(content="{'price': 180.25, 'volume': 1000000, 'pe_ratio': 65.4, 'market_cap': '700B'}", call_id='call_U52JmYQ75UpY1vbq6ERGHyUf')]
---------- financial_analyst ----------
{'price': 180.25, 'volume': 1000000, 'pe_ratio': 65.4, 'market_cap': '700B'}
---------- financial_analyst ----------
[FunctionCall(id='call_jMgtnW4RHxpjA2Jcnnu4dcKR', arguments='{}', name='transfer_to_planner')]
---------- financial_analyst ----------
[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_jMgtnW4RHxpjA2Jcnnu4dcKR')]
---------- financial_analyst ----------
Transferred to planner, adopting the role of planner immediately.
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `HandoffMessage` with value `HandoffMessage(source='fi..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `HandoffMessage` with value `HandoffMessage(source='fi..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `HandoffMessage` with value `HandoffMessage(source='fi..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `HandoffMessage` with value `HandoffMessage(source='fi..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `HandoffMessage` with value `HandoffMessage(source='fi..., type='HandoffMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- planner ----------
[FunctionCall(id='call_IXlyVyxsHt0Xq1LDmygXqArd', arguments='{}', name='transfer_to_news_analyst')]
---------- planner ----------
[FunctionExecutionResult(content='Transferred to news_analyst, adopting the role of news_analyst immediately.', call_id='call_IXlyVyxsHt0Xq1LDmygXqArd')]
---------- planner ----------
Transferred to news_analyst, adopting the role of news_analyst immediately.
---------- news_analyst ----------
[FunctionCall(id='call_8iFvCYdpI0LCIHbYbsXcIxru', arguments='{"query":"TSLA stock market insights"}', name='get_news')]
---------- news_analyst ----------
[FunctionExecutionResult(content='[{\'title\': \'Tesla Expands Cybertruck Production\', \'date\': \'2024-03-20\', \'summary\': \'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.\'}, {\'title\': \'Tesla FSD Beta Shows Promise\', \'date\': \'2024-03-19\', \'summary\': \'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.\'}, {\'title\': \'Model Y Dominates Global EV Sales\', \'date\': \'2024-03-18\', \'summary\': "Tesla\'s Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]', call_id='call_8iFvCYdpI0LCIHbYbsXcIxru')]
---------- news_analyst ----------
[{'title': 'Tesla Expands Cybertruck Production', 'date': '2024-03-20', 'summary': 'Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.'}, {'title': 'Tesla FSD Beta Shows Promise', 'date': '2024-03-19', 'summary': 'Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.'}, {'title': 'Model Y Dominates Global EV Sales', 'date': '2024-03-18', 'summary': "Tesla's Model Y becomes best-selling electric vehicle worldwide, capturing significant market share."}]
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `HandoffMessage` with value `HandoffMessage(source='ne..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `HandoffMessage` with value `HandoffMessage(source='ne..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `HandoffMessage` with value `HandoffMessage(source='ne..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `HandoffMessage` with value `HandoffMessage(source='ne..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `HandoffMessage` with value `HandoffMessage(source='ne..., type='HandoffMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- news_analyst ----------
[FunctionCall(id='call_B5jwLsXUHl08b70gE4tdkL3Q', arguments='{}', name='transfer_to_planner')]
---------- news_analyst ----------
[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_B5jwLsXUHl08b70gE4tdkL3Q')]
---------- news_analyst ----------
Transferred to planner, adopting the role of planner immediately.
---------- planner ----------
[FunctionCall(id='call_a6kYyDDr3Cr4s6at5djaEx4M', arguments='{}', name='transfer_to_writer')]
---------- planner ----------
[FunctionExecutionResult(content='Transferred to writer, adopting the role of writer immediately.', call_id='call_a6kYyDDr3Cr4s6at5djaEx4M')]
---------- planner ----------
Transferred to writer, adopting the role of writer immediately.
---------- writer ----------
### Tesla (TSLA) Stock Market Research Report

#### Financial Overview:
- **Current Price:** $180.25
- **Volume:** 1,000,000 shares
- **Price-to-Earnings (P/E) Ratio:** 65.4
- **Market Capitalization:** $700 Billion

#### Recent News and Developments:

1. **Tesla Expands Cybertruck Production (March 20, 2024):**
   - Tesla has increased the manufacturing capacity for the Cybertruck at their Gigafactory in Texas. This move comes as the company aims to fulfill the strong market demand for the innovative vehicle. This expansion is likely to support the company's growth and revenue in the coming quarters.

2. **Tesla Full Self-Driving (FSD) Beta Shows Promise (March 19, 2024):**
   - The latest version of Tesla's Full Self-Driving Beta program has shown significant improvements, especially in urban navigation and safety features. This advancement could further enhance Tesla's brand as a leader in automotive technology, potentially leading to higher customer adoption and increased sales.

3. **Model Y Dominates Global EV Sales (March 18, 2024):**
   - Tesla's Model Y has emerged as the best-selling electric vehicle worldwide. The vehicle's strong sales performance is boosting Tesla's market share and reinforcing its position as a dominant player in the electric vehicle market.

#### Analysis:
Tesla's current market activities and enhancements in their offerings underscore an optimistic outlook for the company's stock. The increase in manufacturing capabilities and technological advancements positions Tesla to potentially capture more market share and improve financial performance. Investors may find Tesla appealing due to its continued innovation in electric vehicles and self-driving technologies, although the high P/E ratio suggests that the stock is priced with future growth expectations in mind.

#### Recommendations:
Given the current market trends and Tesla's strategic expansions and innovations, investors should consider evaluating their portfolios with regard to potential Tesla stock acquisition, depending on their risk tolerance and investment objectives.

---

This report compiles insights based on recent financial data and market news for Tesla (TSLA). For detailed investment decisions, consulting with a financial advisor is recommended.
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `TextMessage` with value `TextMessage(source='write...d.", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `TextMessage` with value `TextMessage(source='write...d.", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `TextMessage` with value `TextMessage(source='write...d.", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `TextMessage` with value `TextMessage(source='write...d.", type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `TextMessage` with value `TextMessage(source='write...d.", type='TextMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `HandoffMessage` with value `HandoffMessage(source='wr..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `HandoffMessage` with value `HandoffMessage(source='wr..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `HandoffMessage` with value `HandoffMessage(source='wr..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `HandoffMessage` with value `HandoffMessage(source='wr..., type='HandoffMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `HandoffMessage` with value `HandoffMessage(source='wr..., type='HandoffMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- writer ----------
[FunctionCall(id='call_hd1sn7lsYSvNMeABbQbKaZsS', arguments='{}', name='transfer_to_planner')]
---------- writer ----------
[FunctionExecutionResult(content='Transferred to planner, adopting the role of planner immediately.', call_id='call_hd1sn7lsYSvNMeABbQbKaZsS')]
---------- writer ----------
Transferred to planner, adopting the role of planner immediately.
/Users/welcome/anaconda3/envs/autogen_0_4/lib/python3.11/site-packages/pydantic/main.py:441: UserWarning: Pydantic serializer warnings:
  PydanticSerializationUnexpectedValue: Expected `ToolCallRequestEvent` but got `TextMessage` with value `TextMessage(source='plann...TE', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ToolCallExecutionEvent` but got `TextMessage` with value `TextMessage(source='plann...TE', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `MemoryQueryEvent` but got `TextMessage` with value `TextMessage(source='plann...TE', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `UserInputRequestedEvent` but got `TextMessage` with value `TextMessage(source='plann...TE', type='TextMessage')` - serialized value may not be as expected
  PydanticSerializationUnexpectedValue: Expected `ModelClientStreamingChunkEvent` but got `TextMessage` with value `TextMessage(source='plann...TE', type='TextMessage')` - serialized value may not be as expected
  return self.__pydantic_serializer__.to_json(
---------- planner ----------
Research for TSLA stock is complete. The final report has been compiled with financial analysis and recent market news. 

TERMINATE

Process finished with exit code 0

"""