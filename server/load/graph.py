from gremlin_python.process.traversal import T, Column
from gremlin_python.process.graph_traversal import select, GraphTraversalSource

def load_product_graph(g: GraphTraversalSource, product: dict): 
    search = product["images"]["search"]["resolutions"]
    image_125X161 = search["125X161"]
    image_180X240 = search["180X240"]

    (g.addV("product")
        .property(T.id, product["id"])
        .property("id", product["id"])
        .property("name", product["name"])
        .property("gender", product["gender"])
        .property("usage", product["usage"])
        .property("season", product["season"])
        .property("brandName", product["brandName"])
        .property("category", product["category"])
        .property("subCategory", product["subCategory"])
        .property("image_125X161", image_125X161)
        .property("image_180X240", image_180X240)
        .next())

def load_customer_graph(g: GraphTraversalSource, customer: dict, products: list):
    (g.withSideEffect("properties", customer)
        .addV("customer").as_("customer")
        .property(T.id, customer["id"])
        .sideEffect(select("properties")
            .unfold().as_("kv")
            .select("customer")
            .property(select("kv").by(Column.keys), select("kv").by(Column.values))
        )
        .V(products)
        .addE("bought")
        .from_("customer")
        .iterate())