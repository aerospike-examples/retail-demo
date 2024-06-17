from clients import graph_connection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __

g = traversal().with_remote(graph_connection)

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