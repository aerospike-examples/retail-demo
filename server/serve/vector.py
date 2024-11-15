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
        include_fields=bins
    )
    time_taken = time.time() - start

    return results, round(time_taken * 1000, 3)

async def vector_search_by_key(key: str, bins: list=None, count: int = 20):
    start = time.time()
    results = client.vector_search_by_key(
        search_namespace=namespace,
        index_name=index_name,
        key=key,
        key_namespace=namespace,
        key_set=set_name,
        vector_field="img_embedding",
        limit=count,
        include_fields=bins
    )
    time_taken = time.time() - start

    return results, round(time_taken * 1000, 3)
