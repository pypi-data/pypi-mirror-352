from os import getenv

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.opensearch import OpensearchVectorStore, OpensearchVectorClient
from opensearchpy import OpenSearch
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import QueryBundle
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import CompactAndRefine

from agents.utils.utils import init

init()

# Initialize OpenSearch client
username = 'admin'
password = 'admin'
CLUSTER_URL = 'https://localhost:9200'
INDEX_NAME = getenv("OPENSEARCH_INDEX", "gpt-index-demo")

client = OpenSearch(
    hosts=[CLUSTER_URL],
    http_auth=(username, password),
    verify_certs=False
)

# Initialize OpensearchVectorClient
text_field = "content"
embedding_field = "embedding"
vector_client = OpensearchVectorClient(
    CLUSTER_URL, INDEX_NAME, 1536, embedding_field=embedding_field, text_field=text_field, os_client=client
)

# Initialize vector store and storage context
vector_store = OpensearchVectorStore(vector_client)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load the index from the vector store
index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)

# Initialize embedding model
embedding_model = OpenAIEmbedding()

# Define a function to handle user queries
def retrieve_and_respond(query: str):
    # Step 1: Convert query to embedding
    query_embedding = embedding_model.get_query_embedding(query)

    # Step 2: Perform similarity search (retrieve top 5 records)
    retriever = VectorIndexRetriever(index=index, similarity_top_k=5)
    query_bundle = QueryBundle(query_str=query, embedding=query_embedding)
    retrieved_nodes = retriever.retrieve(query_bundle)

    # Step 3: Filter and refine results (select top 3 records)
    refined_nodes = retrieved_nodes[:3]

    # Step 4: Call the LLM (RAG approach)
    response_synthesizer = CompactAndRefine()
    query_engine = RetrieverQueryEngine(retriever=retriever, response_synthesizer=response_synthesizer)
    response = query_engine.query(query)

    # Return the final response
    return {
        "query": query,
        "top_3_results": [node.text for node in refined_nodes],
        "response": str(response),
    }

# Example usage
if __name__ == "__main__":
    user_query = "What are the key ideas in Paul Graham's essays?"
    result = retrieve_and_respond(user_query)
    # print("Query:", result["query"])
    # print("Top 3 Results:", result["top_3_results"])
    # print("Response:", result["response"])
    for i, record in enumerate(result["top_3_results"], start=1):
        print(f"Record {i}:")
        print(record)
        print("==================================")  # Add a blank line after each record