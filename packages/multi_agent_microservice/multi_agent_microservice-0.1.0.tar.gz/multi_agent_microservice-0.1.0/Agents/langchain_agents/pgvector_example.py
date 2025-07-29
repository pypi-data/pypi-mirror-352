from langchain_huggingface import HuggingFaceEmbeddings  # ✅ use this, not the old import
from langchain_community.vectorstores.pgvector import PGVector

# 1. Embedding model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2. PostgreSQL connection string
CONNECTION_STRING = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"

# 3. Vector store
vectorstore = PGVector(
    connection_string=CONNECTION_STRING,
    collection_name="hello_world_collection",
    embedding_function=embeddings,
)

# 4. Add documents
docs = ["Hello world!", "LangChain works with PostgreSQL!", "Vectors are awesome."]
ids = vectorstore.add_texts(docs)
print(f"Inserted document IDs: {ids}")

# 5. Similarity search
results = vectorstore.similarity_search("What does LangChain support?", k=2)

# 6. Print results
for doc in results:
    print(doc.page_content)
