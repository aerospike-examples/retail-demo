import glob
import json
import uuid
import random
from faker import Faker
from collections import defaultdict
from clients import vector_client, aerospike_client, graph_connection
from gremlin_python.process.anonymous_traversal import traversal
from load.key_value import create_string_sindex, load_categories, get_product, get_product_attribute
from load.vector import create_vector_index, load_product_vector
from load.graph import load_product_graph, load_customer_graph
from embed import create_embedding
from PIL import Image
from tqdm import tqdm

graph_client = traversal().with_remote(graph_connection)

img_path = "./data/images/"
prd_path = "./data/styles/**.json"

valid_ids = []

# Similar variant 0: Same gender, season, usage, brandName, different id
# Similar variant 1: Same brandName, usage, season, different subCategory, different id
# Similar variant 2: Same gender, usage, category, different season, different id
similar_variants = [
    {"list": ["gender", "season", "usage", "brandName"]},
    {"list": ["season", "usage", "category"], "attribute": "brandName"},
    {"list": ["gender", "usage", "subCategory"], "attribute": "season"}
]
similar_indexes = [defaultdict(set), defaultdict(set), defaultdict(set)]

def format_string(product: dict, keys: list[str]):
    string = []
    for key in keys:
        value = product.get(key)
        if value:
            string.append(value)
    return "|".join(string)

def add_to_set(idx: defaultdict, key: str, value: str):
    matches: set = idx.get(key)
    if matches == None:
        matches = set(value)
        idx[key] = matches
    else:
        matches.add(value)

def update_product_idx(product: dict):
    product_id: str = product.get("id")
    valid_ids.append(product_id)
    idx_keys = []
    for variant in similar_variants:
        idx_keys.append(format_string(product, variant["list"]))

    for i, key in enumerate(idx_keys):
        add_to_set(similar_indexes[i], key, product_id)

def get_products(product: dict, count: int, already_found: set):
    variant: dict
    for i, variant in enumerate(similar_variants):
        key = format_string(product, variant["list"])
        attribute = variant.get("attribute")
        matches = similar_indexes[i].get(key)
        found_items = 1
        if matches != None:
            matches_list = list(matches)
            while found_items < count + 1:
                idx = random.randint(0, len(matches_list) - 1)
                start_idx = idx
                attr_match = False
                if attribute:
                    attr_match = get_product_attribute(aerospike_client, matches_list[idx], attribute) == product[attribute]
                while matches_list[idx] in already_found or attr_match:
                    idx += 1
                    if idx >= len(matches_list):
                        idx = 0
                    if idx == start_idx:
                        return found_items - 1
                already_found.add(matches_list[idx])
                found_items += 1
        return found_items - 1

def find_similar_products(product_id: str, num_edges: int):
    product = get_product(aerospike_client, product_id)
    found_matches = set()
    var_1 = random.randint(0, num_edges)
    var_2 = 0
    if var_1 < num_edges:
        var_2 = random.randint(1, num_edges - var_1)
    var_3 = num_edges - var_1 - var_2
    for var in [var_1, var_2, var_3]:
        get_products(product, var, found_matches)
    return found_matches

# Create product record with a vector embedding 
# of the corrsponding products default image
def load_data(data: dict, key: str):
    product = {
        "id": key,
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
    colours: dict = data.get("colours", {})
    styles: dict = colours.get("colors") if colours else None
    if styles:
        product["styles"] = styles

    # Get the products corresponding image and generate the embedding
    # If it does not exist, return without writing the record
    try:
        image = Image.open(img_path + key + ".jpg")
        product["img_embedding"] = create_embedding(image)
    except:
        return
    
    update_product_idx(product)
    # Write to a record storing category and article type information in a map
    # Data not currently implemented but storing for future use
    load_categories(aerospike_client, product["category"], product["subCategory"], product["articleType"], product["usage"])
    # Write the product record to Aerospike and add to the vector index
    load_product_vector(vector_client, product, key)
    # Write the product vertex to the graph
    load_product_graph(graph_client, product) 

# Create the vector index
create_vector_index()

sindexes = {
    "category": "cat_idx",
    "subCategory": "subCat_idx",
    "usage": "usage_idx"
}

# Create secondary indexes
for k, v in sindexes.items():
    create_string_sindex(aerospike_client, k, v)

# Get style files
files = sum([glob.glob(prd_path)], [])

# Load data into Aerospike
for file in tqdm(files, "Generating embeddings and loading data...", total=len(files)):
    # Open the style.json file
    # and get the relevant data
    style = open(file)
    data: dict = json.load(style)["data"]
    # Split the file name to create the product key
    key = file.split("/")[-1].split(".")[0]
    # Load the data
    load_data(data, key)

NUM_CUSTOMERS = 100000
edges_created = 0
fake = Faker()

for _ in tqdm(range(NUM_CUSTOMERS), "Populating customers and graph relationships...", NUM_CUSTOMERS):
    product_id: str = valid_ids[random.randint(0, len(valid_ids) - 1)]
    num_edges = int((1 + random.randint(1, 11) * random.randint(1, 11)) / 10)
    results: set = find_similar_products(product_id, num_edges)
    results.add(product_id)
    customer = {
        "id": str(uuid.uuid4()),
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "address": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip": fake.zipcode()
    }
    products = list(results)
    edges_created += len(products)
    load_customer_graph(graph_client, customer, products)

# Close the vector client    
vector_client.close()
# Close the Aerospike client
aerospike_client.close()
# Close the Graph connection
graph_connection.close()

print(f"{edges_created} edges created")
print("Data loaded.")