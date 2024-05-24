from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.aiohttp.transport import AiohttpTransport
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import __

# Create the Gremlin connection the the Aerospike Graph Service
# Queries to the graph service use the Gremlin Python library 
connection = DriverRemoteConnection("ws://localhost:8182/gremlin", "g", transport_factory=lambda:AiohttpTransport(call_from_event_loop=True))
g = traversal().with_remote(connection)

# Gremlin query to find customers that bought a product
# Gets the top N products also bought by those customers
# Returns a list of product vertices 
async def get_also_bought(key, count=10):
    return (
        g.V(key)
            .in_("bought")
            .out("bought")
            .dedup()
            .order().by(__.in_("bought").count())
            .limit(count)
            .property_map()
            .to_list()
    )