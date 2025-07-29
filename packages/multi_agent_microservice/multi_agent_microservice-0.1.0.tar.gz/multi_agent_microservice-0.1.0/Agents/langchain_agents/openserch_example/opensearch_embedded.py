from opensearchpy import OpenSearch, exceptions
from openai import OpenAI
import os
from agentsapi.utils.utils import init

init()


# Set OpenAI API key
# Initialize OpenAI client
openai_client = OpenAI()

# Initialize OpenSearch client
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'admin'),
    use_ssl=False,
    verify_certs=False,
    ssl_show_warn=False
)

# Sample data table (logical table as a list of dictionaries)
sample_data = [
    {'id': '1', 'text': 'The sun sets slowly behind the mountain.', 'category': 'Nature'},
    {'id': '2', 'text': 'Artificial intelligence is transforming industries.', 'category': 'Technology'},
    {'id': '3', 'text': 'The river flows gently through the valley.', 'category': 'Nature'}
]

# # Function to get OpenAI embeddings
# def get_openai_embedding(text):
#     response = openai.Embedding.create(
#         input=text,
#         model="text-embedding-3-small"  # Use a suitable OpenAI embedding model
#     )
#     return response['data'][0]['embedding']

# Function to get OpenAI embeddings
def get_openai_embedding(text):
    try:
        response = openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"  # Latest small embedding model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None
# Example 1: Create an index with k-NN vector field
index_name = 'embedding-test-index'
try:
    if not client.indices.exists(index_name):
        client.indices.create(
            index=index_name,
            body={
                'settings': {
                    'index': {
                        'number_of_shards': 1,
                        'number_of_replicas': 1,
                        'knn': True  # Enable k-NN for vector search
                    }
                },
                'mappings': {
                    'properties': {
                        'text': {'type': 'text'},
                        'category': {'type': 'keyword'},
                        'embedding': {
                            'type': 'knn_vector',
                            'dimension': 1536  # Dimension of text-embedding-3-small
                        }
                    }
                }
            }
        )
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists.")
except exceptions.RequestError as e:
    print(f"Error creating index: {e}")

# Example 2: Index documents with OpenAI embeddings
try:
    for doc in sample_data:
        # Generate embedding for the text
        embedding = get_openai_embedding(doc['text'])
        # Prepare document for indexing
        document = {
            'text': doc['text'],
            'category': doc['category'],
            'embedding': embedding
        }
        # Index the document
        response = client.index(
            index=index_name,
            body=document,
            id=doc['id'],
            refresh=True
        )
        print(f"Document {doc['id']} indexed: {response['result']}")
except exceptions.RequestError as e:
    print(f"Error indexing document: {e}")

# Example 3: Perform a k-NN vector search
try:
    query_text = "Mountain sunset"
    query_embedding = get_openai_embedding(query_text)
    search_body = {
        'query': {
            'knn': {
                'embedding': {
                    'vector': query_embedding,
                    'k': 2  # Return top 2 nearest neighbors
                }
            }
        }
    }
    response = client.search(
        index=index_name,
        body=search_body
    )
    print("k-NN Search results for 'Mountain sunset':")
    for hit in response['hits']['hits']:
        print(f" - ID: {hit['_id']}, Score: {hit['_score']}, Text: {hit['_source']['text']}, Category: {hit['_source']['category']}")
except exceptions.RequestError as e:
    print(f"Error searching: {e}")

# # Example 4: Delete the index (optional cleanup)
# try:
#     client.indices.delete(index=index_name)
#     print(f"Index '{index_name}' deleted successfully.")
# except exceptions.NotFoundError:
#     print(f"Index '{index_name}' not found.")
# except exceptions.RequestError as e:
#     print(f"Error deleting index: {e}")