import os
import time
import aerospike
from aerospike import predicates as p # type: ignore
from dotenv import load_dotenv

# Load .env file
# Can be skipped if using env variables set in the OS
load_dotenv("../.env")

# Get .env variables
namespace = os.getenv("VECTOR_NAMESPACE")
set_name = os.getenv("VECTOR_SET")

# Initialize aerospike client
# Used for key-value look, sindex queries, and task not requiring the vector index
client = aerospike.client({"hosts": [("localhost", 3000)]})

# Key-Value lookup of a specified product
# Gets the product record
# Returns the record bins
async def aerospike_get_product(prod):
    # Create Aerospike key
    # Tuple of "namespace", "set", and user-defined "key"
    key = (namespace, set_name, prod)
    # Gets the product record from Aerospike
    (_, _, bins) = client.get(key)
    
    return bins

# Secondary index query on a specfied index and filter
# Gets the first N records of the secondary index query
# Returns a list of dictionaries, each containing a records bins, and the query execution time
async def aerospike_query(index, filter_value, count=10):
    query = client.query(namespace=namespace, set=set_name)
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