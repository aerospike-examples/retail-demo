from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Form, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
from embed import create_embedding
from clients import proximus_client, aerospike_client
from threading import Lock

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

@app.get("/rest/v1/search")
async def search(cat: str, brand: str):
    # TODO
    return