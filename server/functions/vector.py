import os
import time
from aerospike_vector_search import types, client as vector_client
from dotenv import load_dotenv

# Load .env file
# Can be skipped if using env variables set in the OS
load_dotenv("../.env")

# Get .env variables
namespace = os.getenv("VECTOR_NAMESPACE")
set_name = os.getenv("VECTOR_SET")
index_name = os.getenv("VECTOR_INDEX_NAME")

vect_host = types.HostPort(host="localhost", port=5002)

# Initialize vector client 
# Used for writing/reading data to/from Aerospike using the vector index
client = vector_client.Client(seeds=vect_host)

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