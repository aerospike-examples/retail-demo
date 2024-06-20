from aerospike_vector_search import types, Client as VectorClient, AdminClient as VectorAdmin
from embed import MODEL_DIM

namespace = "retail-vector"
set_name = "products"
index_name = "product_img"

# Creates the vector index on the "img_embedding" bin
# Returns if it already exists
def create_vector_index(admin: VectorAdmin):   
    print("Checking for vector index")
    
    for idx in admin.index_list():
        if (
            idx["id"]["namespace"] == namespace
            and idx["id"]["name"] == index_name
        ):
            print("Index already exists")
            admin.close()
            return
        
    print("Creating vector index")
    admin.index_create(
        namespace=namespace,
        name=index_name,
        sets=set_name,
        vector_field="img_embedding",
        dimensions=MODEL_DIM,
        vector_distance_metric=types.VectorDistanceMetric.COSINE,
    )    
    print("Index created")
    admin.close()

# Create product record with a vector embedding 
# of the corrsponding products default image
def load_product_vector(client: VectorClient, product: dict, key: str):
    # Write the product record to Aerospike and add to the vector index
    client.upsert(namespace=namespace, set_name=set_name, key=key, record_data=product)