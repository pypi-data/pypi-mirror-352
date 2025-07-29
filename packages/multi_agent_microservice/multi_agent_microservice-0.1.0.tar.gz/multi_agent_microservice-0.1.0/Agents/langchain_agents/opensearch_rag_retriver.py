from langchain_community.vectorstores import OpenSearchVectorSearch

from agentsapi.utils.utils import init

init()
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
# vectorstore = OpenSearchVectorSearch(
#     opensearch_url="https://localhost:9200",
#     http_auth=("admin", "admin"),
#     verify_certs=False,
#     index_name="rag_openai",
#     vector_field="embedding",  # <-- Ensure this is exactly as defined
#     text_field="content",
#     embedding_function=embeddings
# )
_is_aoss = False
vectorstore = OpenSearchVectorSearch(
    index_name="rag_openai",
    embedding_function=embeddings,
    opensearch_url="https://localhost:9200",
    http_auth=("admin", "admin"),
    verify_certs=False,
    is_aoss=_is_aoss,
    timeout=30,
    retry_on_timeout=True,
    max_retries=5,
)

# retriever = vectorstore.as_retriever(
#     search_type="similarity",
#     search_kwargs={"k": 3}  # Retrieve top 3 similar docs
# )
# retriever = vectorstore.as_retriever(
#     search_type="similarity",
#     search_kwargs={
#         "k": 3,
#         "vector_field": "embedding"  # <--- This is the critical fix
#     }
# )
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 3,
        "vector_field": "embedding",   # tell it which vector field to use
        "text_field": "content"         # tell it which text field to read
    }
)

docs = retriever.invoke("What is the document about?")
for doc in docs:
    print(doc.page_content)
