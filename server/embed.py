from sentence_transformers import SentenceTransformer

# Embedding model used to transform images 
# and text into a vector
model = SentenceTransformer("clip-ViT-B-32")

# Dimensions produced by the embedding model
# Used when creating the vector index
MODEL_DIM = 512

def create_embedding(data):
    embeddings = model.encode(data)

    # Returns the vector as a list
    # Required by Aerospike Vector Search 
    return embeddings.tolist()
