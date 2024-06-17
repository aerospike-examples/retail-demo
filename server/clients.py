import aerospike
from aerospike_vector_search import types, client, admin
from gremlin_python.driver.aiohttp.transport import AiohttpTransport
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

aerospike_host = "aerospike-cluster"
aerospike_port = 3000

vector_host = "aerospike-vector"
vector_port = 5000
vector_seed = types.HostPort(host=vector_host, port=vector_port)

# Initialize vector admin client
# Used for vector index creation and admin functions 
vector_admin = admin.Client(seeds=vector_seed)

# Initialize vector client 
# Used for writing/reading data to/from Aerospike using the vector index
vector_client = client.Client(seeds=vector_seed)

# Initialize aerospike client
# Used for key-value look, sindex queries, and task not requiring the vector index
aerospike_client = aerospike.client({"hosts": [(aerospike_host, aerospike_port)]})

# Create the Gremlin connection the the Aerospike Graph Service
# Queries to the graph service use the Gremlin Python library 
graph_connection = DriverRemoteConnection("ws://aerospike-graph:8182/gremlin", "g", transport_factory=lambda:AiohttpTransport(call_from_event_loop=True))
