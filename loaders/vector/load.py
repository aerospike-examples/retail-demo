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

# Define file paths for loading env variables and data
env_path = "../../.env"
img_path = "../../data/images/"
prd_path = "../../data/styles/**.json"

# Load .env file
# Can be skipped if using env variables set in the OS
load_dotenv(env_path)

# Get .env variables
namespace = os.getenv("VECTOR_NAMESPACE")
set_name = os.getenv("VECTOR_SET")
index_name = os.getenv("VECTOR_INDEX_NAME")

# Add categories and article types to a meta record
def load_categories(cat, subCat, artType, usage):
    # Create Aerospike key
    # Tuple of "namespace", "set", and user-defined "key"
    key = (namespace, set_name, "product_meta")

    # Defines a map policy for writing and order
    # Only creates a key in it does not exist
    # Fails gracefully if the key does exist
    # Maintains map order by key
    mapPolicy = {
        "map_write_flags": aerospike.MAP_WRITE_FLAGS_CREATE_ONLY | aerospike.MAP_WRITE_FLAGS_NO_FAIL,
        "map_order": aerospike.MAP_KEY_ORDERED
    }

    # Defines a list policy for writing and order
    # Only appends a value if it does not exist
    # Fails gracefully if the value does exist
    # Maintains list order by value
    listPolicy = {
        "write_flags": aerospike.LIST_WRITE_ADD_UNIQUE | aerospike.LIST_WRITE_NO_FAIL,
        "list_order": aerospike.LIST_ORDERED
    }

    # Defines the operations to perform on the map and list bins
    ops = [
        # Adds new "category" key to the map with an empty map as the value
        # Policy dictates it will only add thekey if it does not exist 
        map_operations.map_put("categories", cat, {}, mapPolicy),
        # Using the category as context, this finds the "subCategory" key in the "category" map
        # and increments its value by 1. If the "subCategory" key doesn't exist, it creates it
        # intitializing it with a value of 1
        map_operations.map_increment("categories", subCat, 1, ctx=[cdt_ctx.cdt_ctx_map_key(cat)]),
        # These both append items to the "articleTypes" and "usage" lists
        # Policy dictates these will only append if the value doesn't exist
        list_operations.list_append("articleTypes", artType, listPolicy),
        list_operations.list_append("usage", usage, listPolicy)
    ]
    # Perform the operations
    aerospike_client.operate(key, ops)

# Create product record with a vector embedding 
# of the corrsponding products default image
def load_data(data, key):
    product = {
        "id": data.get("id"),
        "price": data.get("price"),
        "salePrice": data.get("discountedPrice"),
        "name": data.get("productDisplayName"),
        "descriptors": data.get("productDescriptors"),
        "variantName": data.get("variantName"),
        "added": data.get("catalogAddDate"),
        "brandName": data.get("brandName"),
        "brandProfile": data.get("brandUserProfile"),
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

    # This section retreives the nested styles data
    # and adds to the record if it exists
    colours = data.get("colours")
    styles = colours.get("colors") if colours else None    
    if styles:
        product["styles"] = styles

    # Get the products corresponding image and generate the embedding
    # If it does not exist, return without writing the record
    try:
        image = Image.open(img_path + key + ".jpg")
        product["img_embedding"] = create_embedding(image)
    except:
        return
    
    # Write to a record storing category and article type information in a map
    # Data not currently implemented but storing for future use
    load_categories(product["category"], product["subCategory"], product["articleType"], product["usage"])

    # Write the product record to Aerospike and add to the vector index
    vector_client.upsert(namespace=namespace, set_name=set_name, key=key, record_data=product)
 
# Creates the vector index on the "img_embedding" bin
# Returns if it already exists
def create_vector_index():
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
    print("Index created")

# Create the vector index
create_vector_index()
# Close the vactor admin client
vector_admin_client.close()

# Creates a string secondary index on the specified bin
# Returns if already it exists
def create_string_sindex(bin_name, index_name):
    try:
        aerospike_client.index_string_create(
            namespace,
            set_name,
            bin_name,
            index_name
        )
    except:
        return

# Create secondary index for "category" bin
create_string_sindex("category", "cat_idx")

# Create secondary index for "subCategory" bin
create_string_sindex("subCategory", "subCat_idx")

# Create secondary index for "usage" bin
create_string_sindex("usage", "usage_idx")

# Get style files
files = sum([glob.glob(prd_path)], [])

# Load data into Aerospike
for file in tqdm(files, "Generating embeddings and loading data...", total=len(files)):
    # Open the style.json file
    # and get the relevant data
    style = open(file)
    data = json.load(style)["data"]

    # Split the file name to create the product key
    key = file.split("/")[-1].split(".")[0]
    
    # Load the data
    load_data(data, key)

# Close the vector client    
vector_client.close()
# Close the Aerospike client
aerospike_client.close()

print("Data loaded.")