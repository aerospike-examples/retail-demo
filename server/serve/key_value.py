import time
from clients import aerospike_client as client
from aerospike import predicates as p # type: ignore

# Get .env variables
namespace = "retail-vector"
set_name = "products"

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