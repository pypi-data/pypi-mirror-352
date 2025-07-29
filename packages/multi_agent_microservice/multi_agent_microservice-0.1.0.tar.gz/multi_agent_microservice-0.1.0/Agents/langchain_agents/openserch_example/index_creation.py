from opensearchpy import OpenSearch, exceptions

# Initialize the OpenSearch client
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'admin'),  # Username and password for authentication
    use_ssl=False,  # Set to True if using HTTPS in production
    verify_certs=False,  # Set to True in production with valid certificates
    ssl_show_warn=False  # Suppress SSL warnings for development
)

# Example 1: Create an index
try:
    index_name = 'test-index'
    if not client.indices.exists(index_name):
        client.indices.create(
            index=index_name,
            body={
                'settings': {
                    'index': {
                        'number_of_shards': 1,
                        'number_of_replicas': 1
                    }
                }
            }
        )
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists.")
except exceptions.RequestError as e:
    print(f"Error creating index: {e}")

# Example 2: Index a document
try:
    document = {
        'title': 'Sample Document',
        'content': 'This is a test document for OpenSearch.',
        'author': 'John Doe'
    }
    response = client.index(
        index=index_name,
        body=document,
        id='1',  # Document ID
        refresh=True  # Make document available for search immediately
    )
    print(f"Document indexed: {response['result']}")
except exceptions.RequestError as e:
    print(f"Error indexing document: {e}")

# Example 3: Search for documents
try:
    query = {
        'query': {
            'match': {
                'content': 'test'
            }
        }
    }
    response = client.search(
        index=index_name,
        body=query
    )
    print("Search results:")
    for hit in response['hits']['hits']:
        print(f" - {hit['_source']}")
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
