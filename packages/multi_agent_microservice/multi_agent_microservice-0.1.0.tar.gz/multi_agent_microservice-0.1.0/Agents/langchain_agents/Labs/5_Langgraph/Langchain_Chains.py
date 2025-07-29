from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from agentsapi.utils.utils import init

init()
message = [AIMessage(content=f"So you said you were researching ocean mamals?", name="Model")]
message.append(HumanMessage(content=f"Yes, that is right", name="Lance"))
message.append(AIMessage(content=f"Great,what would you like to learn about", name="Model"))
message.append(HumanMessage(content=f"I want to learn about the best place to see orcas in the US.", name="Lance"))

for m in message:
    m.pretty_print()

from langchain_groq import ChatGroq

llm = ChatGroq(model='qwen-qwq-32b')
print(llm)

results = llm.invoke(message)
print(results)


def add(a: int, b: int) -> int:
    return a + b


llm_with_tools = llm.bind_tools([add])

tool_call = llm_with_tools.invoke([HumanMessage(content=f"What is 2 plus 3", name="Lance")])

print(tool_call)

print(tool_call.tool_calls)

from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from typing import Annotated
from langgraph.graph.message import add_messages


class MessageState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


initial_message = [AIMessage(content="Hello! How can i assist you?", name="Model"),
                   HumanMessage(content="I am looking for information on generative AI.", name="Krish")]

new_message = AIMessage(content="Sure, I can help with that.what specifically are you interested in?", name="Model")
add_messages(initial_message, new_message)

# Node
def tool_calling_llm(state:MessageState):
    return {"messages":[llm_with_tools.invoke(state["messages"])]}


# Build graph
builder=StateGraph(MessageState)
#
# builder.add_node("tool_calling_llm",tool_calling_llm)
# builder.add_edge(START,"tool_calling_llm")
# builder.add_edge(tool_calling_llm,END)

builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)

graph = builder.compile()

messages=graph.invoke({"messages":HumanMessage(content="What is 2 minus 3")})
for m in messages['messages']:
    m.pretty_print()



# # Node
# def tool_calling_llm(state: MessagesState):
#     return {"messages": [llm_with_tools.invoke(state["messages"])]}
#
# # Build graph
# builder = StateGraph(MessagesState)
# builder.add_node("tool_calling_llm", tool_calling_llm)
# builder.add_node("tools", ToolNode([multiply,add]))
#
# builder.add_edge(START, "tool_calling_llm")
# builder.add_conditional_edges(
#     "tool_calling_llm",
#     # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
#     # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
#     tools_condition,
# )
# builder.add_edge("tools", END)
# #builder.add_edge("tool2", END)
# graph = builder.compile()
#
# # View
# display(Image(graph.get_graph().draw_mermaid_png()))