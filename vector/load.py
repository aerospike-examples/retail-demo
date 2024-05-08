from embed import create_embedding, MODEL_DIM
from clients import vector_admin_client, vector_client, aerospike_client
from aerospike_helpers import cdt_ctx
from aerospike_helpers.operations import map_operations, list_operations
from aerospike_vector_search import types
from dotenv import load_dotenv
from tqdm import tqdm
from PIL import Image
import aerospike
import glob
import os
import json

# Define file paths
env_path = "../.env"
img_path = "../data/images/"
prd_path = "../data/styles/**.json"

# Load .env file
load_dotenv(env_path)

# Get .env variables
namespace = os.getenv("PROXIMUS_NAMESPACE")
set_name = os.getenv("PROXIMUS_SET")
index_name = os.getenv("PROXIMUS_INDEX_NAME")

# Create product record with vector embedding of default image
def load_data(data):
    product = {
        "id": data.get("id"),
        "price": data.get("price"),
        "salePrice": data.get("discountedPrice"),
        "name": data.get("productDisplayName"),
        "descriptors": data.get("productDescriptors"),
        "variantName": data.get("variantName"),
        "added": data.get("catalogAddDate"),
        "brand": data.get("brandUserProfile"),
        "ageGroup": data.get("ageGroup"),
        "gender": data.get("gender"),
        "colors": [data.get("baseColour"), data.get("colour1"), data.get("colour2")],
        "season": data.get("season"),
        "usage": data.get("usage"),
        "articleAttr": data.get("articleAttributes"),
        "images": data.get("styleImages"),
        "displayCat": data.get("displayCategories").split(",") if data.get("displayCategories") else ["NA"],
        "category": data["masterCategory"]["typeName"],
        "subCategory": data["subCategory"]["typeName"],
        "articleType": data["articleType"]["typeName"],
        "options": data.get("styleOptions")
    }
    
    load_categories(product["category"], product["subCategory"], product["articleType"], product["usage"])

    key = file.split("/")[-1].split(".")[0]
    
    image = Image.open(img_path + key + ".jpg")
    product["img_embedding"] = create_embedding(image)

    vector_client.put(namespace=namespace, set_name=set_name, key=key, record_data=product)

# Add categories and article types to helper record
def load_categories(cat, subCat, artType, usage):
    key = (namespace, set_name, "product_meta")
    mapPolicy = {
        "map_write_flags": aerospike.MAP_WRITE_FLAGS_CREATE_ONLY | aerospike.MAP_WRITE_FLAGS_NO_FAIL,
        "map_order": aerospike.MAP_KEY_ORDERED
    }
    listPolicy = {
        "write_flags": aerospike.LIST_WRITE_ADD_UNIQUE | aerospike.LIST_WRITE_NO_FAIL,
        "list_order": aerospike.LIST_ORDERED
    }
    ops = [
        map_operations.map_put("categories", cat, {}, mapPolicy),
        map_operations.map_increment("categories", subCat, 1, ctx=[cdt_ctx.cdt_ctx_map_key(cat)]),
        list_operations.list_append("articleTypes", artType, listPolicy),
        list_operations.list_append("usage", usage, listPolicy)
    ]
    aerospike_client.operate(key, ops)
    
# Create the vector index if it does not exist
def create_index():
    print("Checking for vector index")
    for idx in vector_admin_client.index_list():
        if (
            idx["id"]["namespace"] == namespace
            and idx["id"]["name"] == index_name
        ):
            print("Index already exists")
            return
        
    print("Creating vector index")
    vector_admin_client.index_create(
        namespace=namespace,
        name=index_name,
        sets=set_name,
        vector_field="img_embedding",
        dimensions=MODEL_DIM,
        vector_distance_metric=types.VectorDistanceMetric.COSINE,
    )    
    vector_admin_client.close()
    print("Index created")

create_index()

# Get style files
files = sum([glob.glob(prd_path)], [])

# Load data into Aerospike
for file in tqdm(files, "Generating embeddings and loading data...", total=len(files)):
    style = open(file)
    data = json.load(style)["data"]
    load_data(data)
    
vector_client.close()
aerospike_client.close()

print("Data loaded.")