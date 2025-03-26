from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
import numpy as np

# Initialize Pinecone
pc = Pinecone(api_key="pcsk_YhHjk_M8pFg9rZcMptxKFZVquyaZKWKxEj3mCKECNnR6FWuv9juBBjkTf1M9GMeVkvhzz")
index = pc.Index("nykaa-products")

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize PCA to reduce the dimension to 384
pca = PCA(n_components=384)

# Function to embed text and reduce its dimension to 384
def embed_text(text):
    vector = model.encode(text)  # Get the 768-dimensional vector
    reduced_vector = pca.fit_transform(np.array([vector]))  # Apply PCA reduction to 384 dimensions
    return reduced_vector.tolist()[0]  # Return the reduced vector as a list

# Query Pinecone index for all records (assuming you know the total number of records, or can handle paginated queries)
top_k = 100  # Adjust based on how many records you want to check per query
all_matches = []
has_more = True
last_id = None  # To track the last record in the previous query for pagination

# Loop to get all records
while has_more:
    query_response = index.query(
        vector=[0] * 384,  # Use a dummy vector to retrieve all data (since we're getting metadata)
        top_k=top_k,
        include_metadata=True,
        filter=None,
        last_id=last_id
    )
    
    # Extract matches and track the last id for the next query
    matches = query_response["matches"]
    all_matches.extend(matches)
    
    # Check if there are more results
    has_more = query_response.get("has_more", False)
    last_id = query_response.get("last_id", None)

# Find the product with the highest price
highest_price = -float('inf')
highest_price_product = None

for match in all_matches:
    product_name = match["metadata"]["name"]
    product_price_str = match["metadata"].get("price", None)
    
    # Check if the price is available and is a valid number
    if product_price_str is not None:
        try:
            product_price = float(product_price_str)  # Try converting to float
            if product_price > highest_price:
                highest_price = product_price
                highest_price_product = product_name
        except ValueError:
            # Skip this product if price is not a valid float
            print(f"Skipping product with invalid price: {product_name}")

# Output the result
if highest_price_product:
    print(f"Product with the highest price: {highest_price_product}, Price: {highest_price}")
else:
    print("No valid products found with a price.")
