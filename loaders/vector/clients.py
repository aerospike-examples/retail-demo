import aerospike
from aerospike_vector_search import types, client, admin

port = 3000
host = "localhost"
vect_port = 5002
vect_host = types.HostPort(host=host, port=vect_port)

# Initialize vector admin client
# Used for vector index creation and admin functions 
vector_admin_client = admin.Client(seeds=vect_host)

# Initialize vector client 
# Used for writing/reading data to/from Aerospike using the vector index
vector_client = client.Client(seeds=vect_host)

# Initialize aerospike client
# Used for key-value look, sindex queries, and task not requiring the vector index
aerospike_client = aerospike.client({"hosts": [(host, port)]})