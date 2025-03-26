from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pinecone
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import generic_helper
import json

# Initialize Pinecone client
pc = Pinecone(api_key="pcsk_YhHjk_M8pFg9rZcMptxKFZVquyaZKWKxEj3mCKECNnR6FWuv9juBBjkTf1M9GMeVkvhzz")  # Replace with your Pinecone API key

# Initialize SentenceTransformer model to convert product names to vectors
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize FastAPI app
app = FastAPI()

# Placeholder for ongoing orders (in a real scenario, use a database)
inprogress_orders = {}

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

# Function to add products to the ongoing order
# Function to add products to the ongoing order
def add_to_order(parameters: dict, session_id: str):
    products = parameters["product"]  # List of product names
    quantities = parameters["number"]  # List of quantities for the products

    if len(products) != len(quantities):
        fulfillment_text = "Sorry, I didn't understand. Can you please specify products and quantities clearly?"
    else:
        new_order_dict = dict(zip(products, quantities))  # Combine products with quantities
        if session_id in inprogress_orders:
            current_order_dict = inprogress_orders[session_id]
            current_order_dict.update(new_order_dict)  # Update the ongoing order
            inprogress_orders[session_id] = current_order_dict
        else:
            inprogress_orders[session_id] = new_order_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far, you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

def get_top_products(search_query: str):
    try:
        # Convert the search query to a vector
        query_vector = model.encode([search_query])[0].tolist()

        # Query Pinecone for top 10 matching products
        query_response = pc.Index("nykaa-products").query(
            vector=query_vector,
            top_k=10,  # Fetch top 10 results
            include_metadata=True
        )

        # Extract product name and price
        if query_response["matches"]:
            top_products = [
                {
                    "name": match["metadata"].get("name", "Unknown"),
                    "price": match["metadata"].get("price", "Unknown"),
                }
                for match in query_response["matches"]
            ]
            return top_products

        else:
            return "No matching products found."

    except Exception as e:
        print(f"Error fetching products: {e}")
        return "Error while retrieving products."

def search_products(parameters: dict, session_id: str):
    # Ensure the search query is a string, even if it's a list
    search_query = parameters.get("product", None)
    
    if isinstance(search_query, list):
        search_query = " ".join(search_query)  # Join list items into a single string
    
    search_query = search_query.strip() if search_query else ""  # Ensure it's a non-empty string

    if not search_query:
        fulfillment_text = "Please specify a product category or name to search."
    else:
        products = get_top_products(search_query)

        if isinstance(products, list):
            # Format the response
            product_list = "\n\n".join(
                [f"🛍️ {p['name']} - ₹{p['price']}" for p in products]
            )
            fulfillment_text = f"Here are the top 10 products for '{search_query}':\n\n{product_list}"
        else:
            fulfillment_text = products  # If error or no results

    return JSONResponse(content={"fulfillmentText": fulfillment_text})



def get_recent_order_id():
    try:
        # Query Pinecone to get the latest order
        query_response = pc.Index("nykaa-orders").query(
            vector=[0] * 384,  # Dummy vector for searching all records
            top_k=1,  # Fetch only the latest order
            include_metadata=True
        )

        if query_response["matches"]:
            latest_order = query_response["matches"][0]
            return latest_order["metadata"].get("order_id", "Not Available")
        else:
            return "No orders found."

    except Exception as e:
        print(f"Error fetching recent order ID: {e}")
        return "Error fetching order ID."
    
def get_order_id(parameters: dict, session_id: str):
    recent_order_id = get_max_order_id()
    fulfillment_text = f"Your most recent order ID is: {recent_order_id}" if recent_order_id != "No orders found." else "No recent orders found."

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


# Function to save the order to the Pinecone index
def save_to_db(order: dict):
    max_order_id = get_max_order_id()
    new_order_id = max_order_id + 1  # Increment order_id

    for product_name, quantity in order.items():
        product_details = get_product_details_from_pinecone(product_name)
        if product_details:
            order_data = {
                "order_id": str(new_order_id),
                "product_name": product_details["name"],
                "brand": product_details["brand"],
                "price": product_details["price"],
                "image_url": product_details["image_url"],
                "content": product_details["content"],
                "reviews": product_details["reviews"],
                "quantity": quantity,
                "order_status": "Placed"  # Add the order_status field here
            }
            pc.Index("nykaa-orders").upsert(
                vectors=[(str(new_order_id), model.encode([product_name])[0].tolist(), order_data)]
            )

    return str(new_order_id)


def get_max_order_id():
    try:
        # Query all existing order IDs
        query_response = pc.Index("nykaa-orders").query(
            vector=[0] * 384,  # Dummy vector (depends on the model's embedding size)
            top_k=1000,  # Fetch as many orders as possible
            include_metadata=True
        )

        if query_response['matches']:
            existing_order_ids = [int(match["id"]) for match in query_response['matches'] if match["id"].isdigit()]
            return max(existing_order_ids) if existing_order_ids else 0
        else:
            return 0
    except Exception as e:
        print(f"Error fetching max order ID: {e}")
        return 0

def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble finding your order. Can you please add products first?"
        })

    # Ensure both products and quantities are lists
    products = parameters.get("product", [])
    quantities = parameters.get("number", [])

    if not isinstance(products, list):
        products = [products]  # Wrap single value in a list

    if not isinstance(quantities, list):
        quantities = [quantities]  # Wrap single value in a list

    current_order = inprogress_orders[session_id]
    removed_items = []
    no_such_items = []

    for product, quantity in zip(products, quantities):
        product_lower = product.lower()  # Case insensitive comparison
        found = False

        for current_product in list(current_order.keys()):
            if current_product.lower() == product_lower:
                found = True
                current_quantity = current_order[current_product]

                # Remove the product or adjust quantity
                if quantity >= current_quantity:
                    del current_order[current_product]  # Remove the product completely
                    removed_items.append(f"{current_quantity} x {current_product}")
                else:
                    current_order[current_product] -= quantity
                    removed_items.append(f"{quantity} x {current_product}")
                break

        if not found:
            no_such_items.append(product)

    # Generate fulfillment text
    if removed_items:
        fulfillment_text = f"Removed {', '.join(removed_items)} from your order."
    else:
        fulfillment_text = "No items were removed."

    if no_such_items:
        fulfillment_text += f" Your current order does not contain {', '.join(no_such_items)}."

    if not current_order:
        fulfillment_text += " Your order is now empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


# Function to complete the order
import json
from fastapi.responses import JSONResponse

def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I couldn't find your ongoing order. Please add some items first."
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id:
            fulfillment_text = f"Awesome. Your order has been placed successfully! Here is your order ID: #{order_id}"
            del inprogress_orders[session_id]  # Remove the completed order
        else:
            fulfillment_text = "Sorry, there was an error while placing your order. Please try again."

    response_data = {
        "fulfillmentMessages": [
            {"text": {"text": [fulfillment_text]}}  # Correct format
        ],
        "source": "webhook"
    }

    print("Response Sent to Dialogflow:", json.dumps(response_data, indent=2))  # Debugging
    return JSONResponse(content=response_data)

def track_order(parameters: dict, session_id: str):
    order_id = parameters.get("number", None)  # Extract order ID from the parameters

    if not order_id:
        return JSONResponse(content={"fulfillmentText": "Please provide a valid order ID to track your order."})

    try:
        # Query Pinecone using the order_id and retrieve the matching entry from the index
        query_response = pc.Index("nykaa-orders").query(
            vector=[0] * 384,  # Dummy vector (for compatibility with your model)
            top_k=10,  # Fetch top 10 matches to be more thorough
            include_metadata=True
        )

        # Iterate through all returned matches to find the order with the matching order_id
        order_details = None
        for match in query_response['matches']:
            metadata = match['metadata']
            if metadata.get("order_id") == str(order_id):  # Match based on the order_id in metadata
                order_details = metadata
                break

        if order_details:
            # Extract details from the matched order
            product_name = order_details["product_name"]
            quantity = order_details["quantity"]
            price = order_details["price"]
            order_status = order_details["order_status"]

            # Calculate the total price
            total_price = float(price) * quantity  # Assuming price is a string, so converting to float

            # Construct the response text
            fulfillment_text = (
                f"Order ID: #{order_id}\n"
                f"Product: {product_name}\n"
                f"Quantity: {quantity}\n"
                f"Price: {price}\n"
                f"Order Status: {order_status}\n"
                f"Total Price: {total_price:.2f}"  # Display the total price with 2 decimal places
            )
        else:
            fulfillment_text = f"Sorry, we couldn't find any order with the ID #{order_id}. Please check your order ID."

    except Exception as e:
        fulfillment_text = f"An error occurred while tracking the order: {str(e)}"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})



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
            )
            fulfillment_text = f"Here are the details for the product '{product_name}':\n\n{product_info}"
        else:
            fulfillment_text = f"Sorry, I couldn't find any details for the product '{product_name}'."

    return JSONResponse(content={"fulfillmentText": fulfillment_text})

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

    # Intent handler dictionary
    intent_handler_dict = {
        'product.search': product_search,
        'top.products' : search_products,
        'order.add - context: ongoing-order': add_to_order,
        'order.remove - context : ongoing-order' : remove_from_order,
        'order.complete - context : ongoing-order': complete_order,
        'order.id : context - context : ongoing-order' : get_order_id,
        'track.order - context : ongoing-order': track_order
    }

    # Call the handler function based on the detected intent
    return intent_handler_dict.get(intent, lambda p, s: JSONResponse(content={"fulfillmentText": "Sorry, I couldn't process your request."}))(parameters, session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
