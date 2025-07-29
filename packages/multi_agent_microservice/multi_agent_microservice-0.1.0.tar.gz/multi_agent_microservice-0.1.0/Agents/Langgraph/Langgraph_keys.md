
# Langgraph Key terms

https://github.com/NirDiamant/GenAI_Agents/blob/main/all_agents_tutorials/langgraph-tutorial.ipynb

https://github.com/krishnaik06/Agentic-Ai-Project/tree/main


https://github.com/patchy631/ai-engineering-hub/tree/main/agentic_rag


https://www.eyelevel.ai/post/most-accurate-rag

https://drive.google.com/drive/u/0/folders/1l45ljrGfOKsiNFh8QPji2eBAd2hOB51c


https://www.firecrawl.dev/pricing


https://mail.google.com/mail/u/0/#inbox/FMfcgzQZTCrjlPwfbZrDRlQVZjlHLFdB




https://medium.com/data-science/from-basics-to-advanced-exploring-langgraph-e8c1cf4db787

https://medium.com/the-ai-forum/build-a-reliable-rag-agent-using-langgraph-2694d55995cd

https://medium.com/data-science-collective/the-complete-guide-to-building-your-first-ai-agent-its-easier-than-you-think-c87f376c84b2

https://levelup.gitconnected.com/gentle-introduction-to-langgraph-a-step-by-step-tutorial-2b314c967d3c


https://github.com/V-Sher/LangGraphTutorial/blob/main/medium_langgraph.ipynb

https://levelup.gitconnected.com/gentle-introduction-to-langgraph-a-step-by-step-tutorial-2b314c967d3c


https://ai.gopubby.com/langgraph-building-a-dynamic-order-management-system-a-step-by-step-tutorial-0be56854fc91


https://github.com/schmitech/ai-driven-order-management/tree/main


# Create the workflow
workflow = StateGraph(MessagesState)

#Add nodes
workflow.add_node("RouteQuery", categorize_query)
workflow.add_node("CheckInventory", check_inventory)
workflow.add_node("ComputeShipping", compute_shipping)
workflow.add_node("ProcessPayment", process_payment)

workflow.add_conditional_edges(
"RouteQuery",
route_query_1,
{
"PlaceOrder": "CheckInventory",
"CancelOrder": "CancelOrder"
}
)
workflow.add_node("CancelOrder", call_model_2)
workflow.add_node("tools_2", tool_node_2)


# Define edges

workflow.add_edge(START, "RouteQuery")
workflow.add_edge("CheckInventory", "ComputeShipping")
workflow.add_edge("ComputeShipping", "ProcessPayment")
workflow.add_conditional_edges("CancelOrder", call_tools_2)
workflow.add_edge("tools_2", "CancelOrder")



# Compile the workflow
agent = workflow.compile()

# Visualize the workflow
mermaid_graph = agent.get_graph()
mermaid_png = mermaid_graph.draw_mermaid_png(draw_method=MermaidDrawMethod.API)
display(Image(mermaid_png))

# Query the workflow
user_query = "I wish to cancel order_id 223"
for chunk in agent.stream(
{"messages": [("user", user_query)]},
stream_mode="values",
):
chunk["messages"][-1].pretty_print()

auser_query = "customer_id: customer_14 : I wish to place order for item_51 with order quantity as 4 and domestic"
for chunk in agent.stream(
{"messages": [("user", auser_query)]},
stream_mode="values",
):
chunk["messages"][-1].pretty_print()


Graphs¶
At its core, LangGraph models agent workflows as graphs. You define the behavior of your agents using three key components:

State: A shared data structure that represents the current snapshot of your application. It can be any Python type, but is typically a TypedDict or Pydantic BaseModel.

Nodes: Python functions that encode the logic of your agents. They receive the current State as input, perform some computation or side-effect, and return an updated State.

Edges: Python functions that determine which Node to execute next based on the current State. They can be conditional branches or fixed transitions.

By composing Nodes and Edges, you can create complex, looping workflows that evolve the State over time. The real power, though, comes from how LangGraph manages that State. To emphasize: Nodes and Edges are nothing more than Python functions - they can contain an LLM or just good ol' Python code.

# In short: nodes do the work. edges tell what to do next.


1. StateGraph
2. Nodes
3. Edges
## Types of edges 
   1. Starting Edge (here graph.set_entry_point("model"))
   2. Normal Edges (here graph.add_edge("tools","model"))
   3. Conditional Edges (there are where a function is used to determine which nodes to go to first, to create this edge)
       **. Upstream node: the output of this node will be looked at to determine what to do next
       **. A function this will be called to determine which node to call next. it should retrun a string
       **. A mapping this mapping will be used to map output of the function in another node.
    Ex: graph.add_conditional_edge("model",)
4. Compiling the Graph
     **. app=graph.compile()

## Adding messages 
from typing import Annotated
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
foo: int
bar: Annotated[list[str], add]


from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict

class GraphState(TypedDict):
messages: Annotated[list[AnyMessage], add_messages]

