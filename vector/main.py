import os
import array
import time
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Form, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from embed import create_embedding
from clients import vector_client, aerospike_client
from aerospike import predicates as p
from dotenv import load_dotenv

# Load .env file
load_dotenv("../.env")

# Get .env variables
namespace = os.getenv("PROXIMUS_NAMESPACE")
set_name = os.getenv("PROXIMUS_SET")
index_name = os.getenv("PROXIMUS_INDEX_NAME")

app = FastAPI(
    title="Aerospike Vector Search",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=None
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/rest/v1/home")
async def get_home():
    shoes = aerospike_query(index="subCategory", filter_value="Shoes")
    bags = aerospike_query(index="subCategory", filter_value="Bags")
    wallets = aerospike_query(index="subCategory", filter_value="Wallets")
    watches = aerospike_query(index="subCategory", filter_value="Watches")
    headwear = aerospike_query(index="subCategory", filter_value="Headwear")


    return {
        "Shoes": shoes, 
        "Bags": bags,
        "Wallets": wallets,
        "Watches": watches,
        "Headwear": headwear
    }

@app.get("/rest/v1/get")
async def get_product(prod: str):
    key = (namespace, set_name, prod)
    try:
        (_, _, bins) = aerospike_client.get(key=key)
        embedding = array.array('f', bins.pop('img_embedding', None))[2:].tolist()
        
        search = vector_search(embedding, bins=["id", "name", "images", "brandName"], count=11)

        related = []
        for item in search:
            if not str(item.bins["id"]) == str(prod):
                related.append(item.bins)
        
        return {"error": None, "product": bins, "related": related}
    except:
        return {"error": "Product not found"}

@app.get("/rest/v1/search")
async def search(q: str):
    embedding = create_embedding(q)
    
    start = time.time()
    results = vector_search(embedding, bins=["id", "name", "images", "brandName"])
    time_taken = time.time() - start

    products = []
    for result in results:
        product = result.bins
        product["distance"] = result.distance
        products.append(product)
    
    return { "products": products, "time": round(time_taken * 1000, 3) }

@app.get("/rest/v1/category")
async def get_category(cat: str):
    pass

def vector_search(embedding, bins=None, count=20):
    return vector_client.vector_search(
        namespace=namespace,
        index_name=index_name,
        query=embedding,
        limit=count,
        bin_names=bins
    )

def aerospike_query(index, filter_value, count=10):
    query = aerospike_client.query(namespace=namespace, set=set_name)
    query.where(p.equals(index, filter_value))
    query.select("id", "name", "images", "brandName")
    query.max_records = count

    records = query.results()
    
    products = []
    for record in records:
        (_, _, bins) = record
        products.append(bins)
    
    return products