import aerospike
from aerospike_vector_search import types, client, admin

port = 3000
host = "localhost"
vect_port = 5002
vect_host = types.HostPort(host=host, port=vect_port)

vector_client = client.Client(seeds=vect_host)
vector_admin_client = admin.Client(seeds=vect_host)
aerospike_client = aerospike.client({"hosts": [(host, port)]})