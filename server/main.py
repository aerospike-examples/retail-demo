import array
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from embed import create_embedding
from serve.key_value import aerospike_get_product, aerospike_query
from serve.graph import get_also_bought
from serve.vector import vector_search, vector_search_by_key

# Instantiates the app to serve the API 
app = FastAPI(
    title="Aerospike Vector Search",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None
)

# Add CORS middleware to allow calls from the browser front end to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Called when navigating to the homepage
# Performs secondary index queries on multiple "subCategory" values
# Returns and object containing the result of each query
@app.get("/rest/v1/home")
async def get_home():
    (shoes, _) = await aerospike_query(index="subCategory", filter_value="Shoes")
    (bags, _) = await aerospike_query(index="subCategory", filter_value="Bags")
    (wallets, _) = await aerospike_query(index="subCategory", filter_value="Wallets")
    (watches, _) = await aerospike_query(index="subCategory", filter_value="Watches")
    (headwear, _) = await aerospike_query(index="subCategory", filter_value="Headwear")

    return {
        "Shoes": shoes, 
        "Bags": bags,
        "Wallets": wallets,
        "Watches": watches,
        "Headwear": headwear
    }

# Called for product details
# Performs a key-value lookup on the specified product 
# Uses the product vector embedding in a cosine similarity search
# Uses the product key to traverse the graph and identify items also bought by other customers
# Returns and object containing the result of each query   
@app.get("/rest/v1/get")
async def get_product(prod: str):
    try:
        # Gets product data through a key-value lookup
        product = await aerospike_get_product(prod)
        
        # Performs cosine similarity search using the products key to use its vector embedding      
        (search, _) = await vector_search_by_key(prod, bins=["id", "name", "images", "brandName"], count=10)
        # Get the fields for each related item in the search result
        related = [item.fields for item in search]
        
        # Performs the graph traversal for recommended items
        results = await get_also_bought(key=prod)

        # Creates a list of recommended product dictionaries while removing this product
        also_bought = []
        for result in results:
            if not result["id"][0].value == prod:
                prd = {}
                for key in result:
                    prd[key] = result[key][0].value
                also_bought.append(prd)   

        return {"error": None, "product": product, "related": related, "also_bought": also_bought}
    except:
        return {"error": "Product not found"}

# Called when searching products
# Turns text query into a vector embedidng that can be used for cosine similarity search with the vector client
# Returns the top 20 results ordered by distance, along with query execution time
@app.get("/rest/v1/search")
async def search(q: str):
    # Generate vector embedding on the query text
    embedding = create_embedding(q)
    # Get the results of the vector search
    results, time = await vector_search(embedding, bins=["id", "name", "images", "brandName"])

    # Creates a list of product dictionaries most similar to the query
    products = []
    for result in results:
        product = result.fields
        product["distance"] = result.distance
        products.append(product)
    
    return { "products": products, "time": time }

# Called when looking at specific "category", "subCategory", or "usage" pages
# Performs a secondary index query on the provided index using the provided filter value
# Returns the first 20 results, along with execution time  
@app.get("/rest/v1/category")
async def get_category(idx: str, filter_value: str):
    # Get the results of the secondary index query
    products, time = await aerospike_query(index=idx, filter_value=filter_value, count=20)

    return {"products": products, "time": time}
