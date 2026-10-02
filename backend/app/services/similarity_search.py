
import math


def cosine_similarity(vector_a, vector_b):
    """Calculate cosine similarity between two vectors."""

    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must have the same dimensions")

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def search_documents(query_embedding, documents, top_k=3):
    """Return the top matching chunks for a query."""

    results = []

    for document in documents:
        score = cosine_similarity(
            query_embedding,
            document["embedding"]
        )

        results.append({
            "page": document["page"],
            "text": document["text"],
            "score": round(score, 4)
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]