import os
import glob
import json
import uuid
import random
import argparse
from faker import Faker
from clients import vector_client, vector_admin, aerospike_client, graph_connection
from gremlin_python.process.anonymous_traversal import traversal
from load.key_value import create_string_sindex, load_categories, get_product, get_product_attribute
from load.vector import create_vector_index, load_product_vector
from load.graph import load_product_graph, load_customer_graph
from embed import create_embedding
from PIL import Image
from tqdm import tqdm

graph_client = traversal().with_remote(graph_connection)
img_path = "./data/images/"
sindexes = {
    "category": "cat_idx",
    "subCategory": "subCat_idx",
    "usage": "usage_idx"
}
similar_variants = [
    # Similar variant 0: Same gender, season, usage, brandName, different id
    {"list": ["gender", "season", "usage", "brandName"]},
    # Similar variant 1: Same season, usage, category, different brandName, different id
    {"list": ["season", "usage", "category"], "attribute": "brandName"},
    # Similar variant 2: Same gender, usage, subCategory, different season, different id
    {"list": ["gender", "usage", "subCategory"], "attribute": "season"}
]
similar_indexes = [{}, {}, {}]
valid_ids = []

def format_string(product: dict, keys: list[str]):
    string = []
    for key in keys:
        value = product.get(key)
        if value:
            string.append(value)
    return "|".join(string)

def add_to_set(index: dict, key: str, value: str):
    matches: set = index.get(key)
    if matches == None:
        matches = {value}
        index[key] = matches
    else:
        matches.add(value)

def update_product_idx(product: dict):
    product_id: str = product.get("id")
    # Write the product vertex to the graph
    load_product_graph(graph_client, product) 
    
    valid_ids.append(product_id)
    idx_keys = []
    for variant in similar_variants:
        idx_keys.append(format_string(product, variant["list"]))

    for i, key in enumerate(idx_keys):
        add_to_set(similar_indexes[i], key, product_id)

def get_attribute(attribute, product_id, match):
    if attribute:
        return get_product_attribute(aerospike_client, product_id, attribute) == match
    return False

def get_products(product: dict, count: int, already_found: set):
    variant: dict
    for i, variant in enumerate(similar_variants):
        key = format_string(product, variant["list"])
        attribute = variant.get("attribute")
        matches = similar_indexes[i].get(key)
        found_items = 0
        if matches != None:
            matches_list = list(matches)
            while found_items < count:
                idx = random.randint(0, len(matches_list) - 1)
                start_idx = idx
                while matches_list[idx] in already_found or get_attribute(attribute, matches_list[idx], product.get(attribute)):
                    idx += 1
                    if idx >= len(matches_list):
                        idx = 0
                    if idx == start_idx:
                        return
                already_found.add(matches_list[idx])
                found_items += 1

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
def load_data(product: dict, key: str):
    image = Image.open(img_path + key + ".jpg")
    product["img_embedding"] = create_embedding(image)
    # Write to a record storing category and article type information in a map
    # Data not currently implemented but storing for future use
    load_categories(aerospike_client, product["category"], product["subCategory"], product["articleType"], product["usage"])
    # Write the product record to Aerospike and add to the vector index
    load_product_vector(vector_client, product, key)

def load_product_data(load_products):
    # Get style files
    prd_path = "./data/styles/**.json"
    files = sum([glob.glob(prd_path)], [])
    message = "Generating embeddings and loading data..." if load_products else "Loading product graph and index..."

    # Load data into Aerospike
    for file in tqdm(files, message, total=len(files)):
        # Open the style.json file
        # and get the relevant data
        style = open(file)
        data: dict = json.load(style)["data"]
        # Split the file name to create the product key
        key = file.split("/")[-1].split(".")[0]

        if os.path.isfile(f"{img_path}{key}.jpg"):
            product: dict = {
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
            
            update_product_idx(product)

            if load_products:
                # Load the data
                load_data(product, key)

def load_customer_data():
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
    
    print(f"{edges_created} edges created")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--load-customers", action="store_true", help="load the customer data")
    parser.add_argument("-p", "--load-products", action="store_true", help="load the product data")
    parser.add_argument("-t", "--truncate", action="store_true", help="truncate the existing namespace (only applied to data loaded)")
    args = parser.parse_args()

    load_customers = vars(args).get("load_customers")
    load_products = vars(args).get("load_products")
    truncate = vars(args).get("truncate")
    
    if not load_customers and not load_products:
        load_customers = True
        load_products = True

    if truncate:
        if load_customers:
            print("truncating customer data")
            graph_client.V().drop().iterate()
        if load_products:
            print("truncating product data")
            aerospike_client.truncate("retail-vector", "products")
    
    if load_products:
        # Create the vector index
        create_vector_index(vector_admin)

        # Create secondary indexes
        for k, v in sindexes.items():
            create_string_sindex(aerospike_client, k, v)

    load_product_data(load_products)

    if load_customers:
        load_customer_data()

    # Close the vector admin    
    vector_admin.close()
    # Close the vector client    
    vector_client.close()
    # Close the Aerospike client
    aerospike_client.close()
    # Close the Graph connection
    graph_connection.close()

    print("Data loaded.")

if __name__=="__main__": 
    main() 