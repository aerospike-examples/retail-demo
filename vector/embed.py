from sentence_transformers import SentenceTransformer

model = SentenceTransformer("clip-ViT-B-32")
MODEL_DIM = 512

def create_embedding(data):
    embeddings = model.encode(data)
    return embeddings.tolist()
