from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pinecone
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import generic_helper

# Initialize Pinecone client
pc = Pinecone(api_key="pcsk_YhHjk_M8pFg9rZcMptxKFZVquyaZKWKxEj3mCKECNnR6FWuv9juBBjkTf1M9GMeVkvhzz")  # Replace with your Pinecone API key

# Initialize SentenceTransformer model to convert product names to vectors
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize FastAPI app
app = FastAPI()

# Function to query Pinecone and get product details
def get_product_details_from_pinecone(product_name: str):
    # Embed the product name into a vector using SentenceTransformer
    query_vector = model.encode([product_name])[0]
    
    # Convert the numpy ndarray to a plain list before passing to Pinecone
    query_vector = query_vector.tolist()

    # Query Pinecone to get matching products
    query_response = pc.Index("nykaa-products").query(
        vector=query_vector,
        top_k=5,  # We take the top 5 matches
        include_metadata=True
    )

    if query_response['matches']:
        best_match = query_response['matches'][0]
        product_metadata = best_match["metadata"]

        # Extract product details from metadata
        product_details = {
            "name": product_metadata.get("name", "Not Available"),
            "brand": product_metadata.get("brand", "Not Available"),
            "price": product_metadata.get("price", "Not Available"),
            "image_url": product_metadata.get("image_url", "Not Available"),
            "content": product_metadata.get("content", "Not Available"),
            "reviews": product_metadata.get("reviews", "Not Available")
        }
        return product_details
    else:
        return None

# FastAPI endpoint to handle incoming requests
@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract intent and parameters from the payload
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    # Function to handle product search intent
    def product_search(parameters: dict, session_id: str):
        product_name = parameters.get("product", None)

        if not product_name:
            fulfillment_text = "Sorry, I couldn't find the product you're looking for. Can you please specify a product?"
        else:
            # Search for the product in Pinecone
            product_details = get_product_details_from_pinecone(product_name)

            if product_details:
                # Construct a response with the product details from Pinecone
                product_info = (
                    f"Product Name: {product_details['name']}\n"
                    f"Brand: {product_details['brand']}\n"
                    f"Price: {product_details['price']}\n"
                    f"Image URL: {product_details['image_url']}\n"
                    f"Content: {product_details['content']}\n"
                    f"Reviews: {product_details['reviews']}\n"
                )
                fulfillment_text = f"Here are the details for the product '{product_name}':\n\n{product_info}"
            else:
                fulfillment_text = f"Sorry, I couldn't find any details for the product '{product_name}'."

        return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })

    # Intent handler dictionary
    intent_handler_dict = {
        'product.search': product_search
    }

    # Call the handler function based on the detected intent
    return intent_handler_dict.get(intent, lambda p, s: JSONResponse(content={"fulfillmentText": "Sorry, I couldn't process your request."}))(parameters, session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
