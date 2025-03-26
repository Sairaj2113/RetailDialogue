from pinecone import Pinecone

# Initialize Pinecone with your API key
pc = Pinecone(api_key="pcsk_YhHjk_M8pFg9rZcMptxKFZVquyaZKWKxEj3mCKECNnR6FWuv9juBBjkTf1M9GMeVkvhzz")

# Specify the name of your index
index_name = "nykaa-orders"

# Get the index
index = pc.Index(index_name)

# Delete all records from the index
index.delete(delete_all=True)
