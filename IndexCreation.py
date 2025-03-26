from pinecone import Pinecone, ServerlessSpec
import os

# Set your Pinecone API key
os.environ["PINECONE_API_KEY"] = "pcsk_YhHjk_M8pFg9rZcMptxKFZVquyaZKWKxEj3mCKECNnR6FWuv9juBBjkTf1M9GMeVkvhzz"

# Initialize Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Define the index name
index_name = "nykaa-orders"

# Check if the index exists before creating
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # Adjust according to your embedding model
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")  # Try "us-west1-gcp" or another available region
    )

# Connect to the index
index = pc.Index(index_name)

# Print the available indexes to verify
print(pc.list_indexes().names())
