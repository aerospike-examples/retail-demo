import aerospike
from aerospike import Client
from aerospike_helpers import cdt_ctx
from aerospike_helpers.operations import map_operations, list_operations

namespace = "retail-vector"
set_name = "products"

# Add categories and article types to a meta record
def load_categories(client: Client, cat: str, subCat: str, artType: str, usage: str):
    # Create Aerospike key
    # Tuple of "namespace", "set", and user-defined "key"
    key = (namespace, "cat_index", "product_meta")

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
    client.operate(key, ops)

# Creates a string secondary index on the specified bin
# Returns if already it exists
def create_string_sindex(client: Client, bin_name: str, index_name: str):
    try:
        client.index_string_create(
            namespace,
            set_name,
            bin_name,
            index_name
        )
    except:
        return
    
def get_product(client: Client, product_id: str) -> dict:
    key = (namespace, set_name, product_id)
    _, _, bins = client.get(key)
    
    return bins

def get_product_attribute(client: Client, product_id: str, attribute: str) -> str:
    key = (namespace, set_name, product_id)
    _, _, bins = client.select(key, [attribute])
    
    return bins[attribute]