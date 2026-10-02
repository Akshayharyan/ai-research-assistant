from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def create_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    embeddings = model.encode(texts)

    return embeddings.tolist()