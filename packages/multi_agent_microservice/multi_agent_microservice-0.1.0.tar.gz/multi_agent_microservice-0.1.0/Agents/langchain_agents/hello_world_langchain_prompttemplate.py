from agentsapi.utils.utils import init
init()
from langchain_openai import ChatOpenAI
llm = ChatOpenAI()
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

output_parser = JsonOutputParser()

prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": output_parser.get_format_instructions()},
)

chain = prompt | llm | output_parser

response = chain.invoke({"query": "Can you tell me about LangSmith?"})

print(f" response ={response}")
