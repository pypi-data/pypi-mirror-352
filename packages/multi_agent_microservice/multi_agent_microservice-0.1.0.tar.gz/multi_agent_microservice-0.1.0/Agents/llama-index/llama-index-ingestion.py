from os import getenv
from llama_index.core import SimpleDirectoryReader
from llama_index.vector_stores.opensearch import (
    OpensearchVectorStore,
    OpensearchVectorClient,
)
from llama_index.core import VectorStoreIndex, StorageContext
from opensearchpy import OpenSearch

from agents.utils.utils import init

init()
# http endpoint for your cluster (opensearch required for vector index usage)
# endpoint = getenv("OPENSEARCH_ENDPOINT", "http://localhost:9200")
# # index to demonstrate the VectorStore impl
idx = getenv("OPENSEARCH_INDEX", "gpt-index-demo")
username = 'admin'
password = 'admin'
CLUSTER_URL = 'https://localhost:9200'
client = OpenSearch(
    hosts=[CLUSTER_URL],
    http_auth=(username, password),
    verify_certs=False
)

# load some sample data
documents = SimpleDirectoryReader("/Users/welcome/Desktop/data/data/paul_graham/").load_data()

# OpensearchVectorClient stores text in this field by default
text_field = "content"
# OpensearchVectorClient stores embeddings in this field by default
embedding_field = "embedding"
# OpensearchVectorClient encapsulates logic for a
# single opensearch index with vector search enabled
client = OpensearchVectorClient(
    CLUSTER_URL, idx, 1536, embedding_field=embedding_field, text_field=text_field,os_client=client
)
# initialize vector store
vector_store = OpensearchVectorStore(client)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
# initialize an index using our sample data and the client we just created
index = VectorStoreIndex.from_documents(
    documents=documents, storage_context=storage_context
)