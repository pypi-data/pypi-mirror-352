import os

from agentsapi.utils.utils import init

init()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI()
print(llm)

print("Invoke the model")
response = llm.invoke("What is Agentic AI?")
print(response)
print(type(response))

print(f" Content of message = {response.content}")

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([

    ("system", "You are an expert AI Engineer. Provide me answer based on the question"),
    ("user", "{input}")
])

print(prompt)

llm_chat_prompt_template = ChatOpenAI(model="gpt-4o")

chain = prompt | llm_chat_prompt_template

print(f" Chain ={chain}")

#response_chat = chain.invoke({"input": "Can you tell me about langsmith around 500 lines?"})
#print(f"response ={response_chat.content}")

from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

output_parser = StrOutputParser()

chain = prompt | llm_chat_prompt_template | output_parser

#response_str_output = chain.invoke({"input": "Can you tell me about Langsmith write 200 lines ?"})
#print(f"response_str_output ={response_str_output}")

# JSON parser
output_parser = JsonOutputParser()
# Chain setup
final_json_chain = prompt | llm_chat_prompt_template | output_parser

# Invoke
response_json_output = final_json_chain.invoke({"input": "Can you tell me about Langsmith in around 200 lines?"})

print(f"response_json_output = {response_json_output}")