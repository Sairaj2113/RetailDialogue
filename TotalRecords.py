from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Initialize Pinecone
pc = Pinecone(api_key="pcsk_YhHjk_M8pFg9rZcMptxKFZVquyaZKWKxEj3mCKECNnR6FWuv9juBBjkTf1M9GMeVkvhzz")
index = pc.Index("nykaa-products")

# Load embedding model from sentence-transformers
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to convert product name into an embedding vector
def embed_text(text):
    return model.encode(text).tolist()

# Query text (the product you're searching for)
query = "Feather-Light Matte Liquid Lip Cream - 36 Curious Wine"
query_vector = embed_text(query)  # Convert query to vector using SentenceTransformer

# Query Pinecone to find the closest match
query_response = index.query(
    vector=query_vector,
    top_k=1,  # Get top 1 match (closest product)
    include_metadata=True
)

# Extracting and printing the price of the closest product match
if query_response['matches']:
    closest_match = query_response['matches'][0]
    product_name = closest_match['metadata']['name']
    product_price = closest_match['metadata']['price']
    print(f"Product: {product_name}, Price: {product_price}")
else:
    print("No matching product found.")

# Get the total count of products in the index
index_description = index.describe_index_stats()  # Get the index stats
total_product_count = index_description['total_vector_count']  # Extract the total vector count
print(f"Total count of products in the index: {total_product_count}")
