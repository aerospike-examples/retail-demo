from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Form, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from embed import create_embedding
from clients import vector_client, aerospike_client
from threading import Lock
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

@app.get("/rest/v1/get")
async def get_product(prod: str):
    key = (namespace, set_name, prod)
    (_, _, bins) = aerospike_client.get(key=key)
    bins.pop('img_embedding', None)

    return bins

@app.get("/rest/v1/search")
async def search(q: str):
    embedding = create_embedding(q)
    results = vector_search(embedding, bins=["id", "name", "images"])

    products = []
    for result in results:
        product = result.bins
        product["distance"] = result.distance
        products.append(product)
    
    return products

def vector_search(embedding, bins=None, count=20):
    return vector_client.vector_search(
        namespace=namespace,
        index_name=index_name,
        query=embedding,
        limit=count,
        bin_names=bins
    )