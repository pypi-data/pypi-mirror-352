from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.vector_stores.opensearch import OpensearchVectorStore, OpensearchVectorClient
from opensearchpy import OpenSearch
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.openai import OpenAI
from os import getenv

from agents.utils.utils import init

init()
# Setup OpenSearch client (same as ingestion)
username = 'admin'
password = 'admin'
CLUSTER_URL = 'https://localhost:9200'
INDEX_NAME = "gpt-index-demo"

os_client = OpenSearch(
    hosts=[CLUSTER_URL],
    http_auth=(username, password),
    verify_certs=False
)

from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class SourceNode:
    text: str
    metadata: Dict[str, Any]
    score: float

    @classmethod
    def from_node(cls, node_with_score) -> "SourceNode":
        return cls(
            text=node_with_score.node.get_content(),
            metadata=node_with_score.node.metadata,
            score=node_with_score.score
        )

# Connect to existing OpenSearch vector index
client = OpensearchVectorClient(
    CLUSTER_URL,
    INDEX_NAME,
    dim=1536,
    embedding_field="embedding",
    text_field="content",
    os_client=os_client
)

# Initialize vector store and storage context
vector_store = OpensearchVectorStore(client)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load the index (no documents needed this time)
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

# Set up the retriever

# Setup retriever for top 3 results
#retriever = index.as_retriever(similarity_top_k=4)
retriever = VectorIndexRetriever(index=index,similarity_top_k=4)

# Your input query
query = "What are the core ideas of Paul Graham about startups?"

# Retrieve similar nodes
nodes = retriever.retrieve(query)

print("==== Retrieved Top 3 Similar Nodes ====\n")

# for i, node in enumerate(nodes):
#     print(f"Node #{i + 1}")
#     print("ID: ", node.node.node_id)
#     print("Text: ", node.node.get_content()[:300], "...")  # Print first 300 chars
#     print("Score: ", node.score)
#     print("Metadata: ", node.node.metadata)
#     print("=" * 60)
#
# # Optional: Now feed to LLM if needed
# llm = OpenAI(model="gpt-4", temperature=0.3)
# query_engine = RetrieverQueryEngine.from_args(
#     retriever=retriever,
#     llm=llm
# )
# response = query_engine.query(query)
#
# print("\n==== Final Answer from LLM ====\n")
# print(response)

for i, node in enumerate(nodes):
    print(f"Node #{i + 1}")
    print("ID: ", node.node.node_id)
    print("Text: ", node.node.get_content()[:300], "...")  # Print first 300 chars
    print("Score: ", node.score)
    print("Metadata: ", node.node.metadata)
    print("=" * 60)

# Optional: Now feed to LLM if needed
llm = OpenAI(model="gpt-4", temperature=0.3)
query_engine = RetrieverQueryEngine.from_args(
    retriever=retriever,
    llm=llm
)
response = query_engine.query(query)

print("\n==== Final Answer from LLM ====\n")
print(response)
print("^^^^^^^^^^^^^^^^^^")
source_nodes = [SourceNode.from_node(n) for n in nodes]

for i, sn in enumerate(source_nodes):
    print(f"Node #{i+1}")
    print("Text:", sn.text[:300], "...")
    print("Score:", sn.score)
    print("Metadata:", sn.metadata)
    print("=" * 60)
