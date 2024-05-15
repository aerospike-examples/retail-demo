import os
import array
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from embed import create_embedding
from clients import vector_client, aerospike_client
from aerospike import predicates as p
from dotenv import load_dotenv
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.aiohttp.transport import AiohttpTransport
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Load .env file
load_dotenv("../.env")

# Get .env variables
namespace = os.getenv("PROXIMUS_NAMESPACE")
set_name = os.getenv("PROXIMUS_SET")
index_name = os.getenv("PROXIMUS_INDEX_NAME")

connection = DriverRemoteConnection("ws://localhost:8182/gremlin", "g", transport_factory=lambda:AiohttpTransport(call_from_event_loop=True))
g = traversal().with_remote(connection)

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

@app.get("/rest/v1/get")
async def get_product(prod: str):
    
    try:
        product = await aerospike_get_product(prod)
        
        embedding_bytes = product.pop('img_embedding', None)[22:]
        embedding = array.array('f', embedding_bytes).tolist()        
        (search, _) = await vector_search(embedding, bins=["id", "name", "images", "brandName"], count=11)

        related = []
        for item in search:
            if not str(item.fields["id"]) == str(prod):
                related.append(item.fields)
        
        results = await get_also_bought(key=prod)

        also_bought = []
        for result in results:
            if not result["id"][0].value == prod:
                prd = {}
                for key in result:
                    prd[key] = result[key][0].value
                also_bought.append(prd)   

        return {"error": None, "product": product, "related": related, "also_bought": also_bought}
    except Exception as e:
        print(e)
        return {"error": "Product not found"}

@app.get("/rest/v1/search")
async def search(q: str):
    embedding = create_embedding(q)
    results, time = await vector_search(embedding, bins=["id", "name", "images", "brandName"])

    products = []
    for result in results:
        product = result.fields
        product["distance"] = result.distance
        products.append(product)
    
    return { "products": products, "time": time }

@app.get("/rest/v1/category")
async def get_category(idx: str, filter_value: str):
    
    products, time = await aerospike_query(index=idx, filter_value=filter_value, count=20)

    return {"products": products, "time": time}

async def get_also_bought(key, count=10):
    return (
        g.V(key)
            .in_("bought")
            .out("bought")
            .dedup()
            .order().by(__.in_("bought").count())
            .limit(count)
            .property_map()
            .to_list()
    )

async def vector_search(embedding, bins=None, count=20):
    start = time.time()
    results = vector_client.vector_search(
        namespace=namespace,
        index_name=index_name,
        query=embedding,
        limit=count,
        field_names=bins
    )
    time_taken = time.time() - start

    return results, round(time_taken * 1000, 3)

async def aerospike_get_product(prod):
    key = (namespace, set_name, prod)
    (_, _, bins) = aerospike_client.get(key)
    
    return bins

async def aerospike_query(index, filter_value, count=10):
    query = aerospike_client.query(namespace=namespace, set=set_name)
    query.where(p.equals(index, filter_value))
    query.select("id", "name", "images", "brandName")
    query.max_records = count

    start = time.time()
    records = query.results()
    time_taken = time.time() - start
    
    products = []
    for record in records:
        (_, _, bins) = record
        products.append(bins)
    
    return products, round(time_taken * 1000, 3)