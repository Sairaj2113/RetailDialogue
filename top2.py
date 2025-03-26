from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Initialize Pinecone
pc = Pinecone(api_key="pcsk_YhHjk_M8pFg9rZcMptxKFZVquyaZKWKxEj3mCKECNnR6FWuv9juBBjkTf1M9GMeVkvhzz")
index = pc.Index("nykaa-products")

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Query text
query_text = "long-lasting waterproof lipstick"
query_embedding = model.encode(query_text).tolist()  # Ensure it's a list

# Double-check the vector shape
print(f"Embedding Shape: {len(query_embedding)}")  # Should be 384

# Ensure the index exists
print(index.describe_index_stats())  

# Perform the query (use correct format)
results = index.query(
    vector=query_embedding,  # This must be a list of 384 floats
    top_k=2,  # Adjust top_k as needed
    include_metadata=True  # True instead of a list
)

# Print results
print(results)
