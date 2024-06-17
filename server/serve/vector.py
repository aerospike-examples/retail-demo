import time
from clients import vector_client as client

# Get .env variables
namespace = "retail-vector"
set_name = "products"
index_name = "product_img"

# Cosine similarity search accross products in Aerospike
# Gets the top N products most similar to the provided vector embedding
# Returns a list of records and query execution time
async def vector_search(embedding, bins=None, count=20):
    start = time.time()
    results = client.vector_search(
        namespace=namespace,
        index_name=index_name,
        query=embedding,
        limit=count,
        field_names=bins
    )
    time_taken = time.time() - start

    return results, round(time_taken * 1000, 3)