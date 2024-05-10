from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Form, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from embed import create_embedding
from clients import vector_client, aerospike_client
from threading import Lock
from dotenv import load_dotenv
import array

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
async def get_category():
    key = (namespace, set_name, "product_meta")
    (_, _, bins) = aerospike_client.get(key=key)

    return bins

@app.get("/rest/v1/get")
async def get_product(prod: str):
    key = (namespace, set_name, prod)
    (_, _, bins) = aerospike_client.get(key=key)
    embedding = array.array('f', bins.pop('img_embedding', None))[2:].tolist()
    
    search = vector_search(embedding, bins=["id", "name", "images", "brandName"], count=11)
    
    related = []
    for item in search:
        if not str(item.bins["id"]) == str(prod):
            related.append(item.bins)
    
    return {"product": bins, "related": related}

@app.get("/rest/v1/search")
async def search(q: str):
    embedding = create_embedding(q)
    results = vector_search(embedding, bins=["id", "name", "images", "brandName"])

    products = []
    for result in results:
        product = result.bins
        product["distance"] = result.distance
        products.append(product)
    
    return products

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