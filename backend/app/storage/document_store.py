
# Temporary in-memory storage for PDF chunks and embeddings

documents = []


def add_documents(chunks, embeddings):
    """Store each chunk together with its embedding."""

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks and embeddings must match"
        )

    for chunk, embedding in zip(chunks, embeddings):
        documents.append({
            "page": chunk["page"],
            "text": chunk["text"],
            "embedding": embedding
        })


def get_documents():
    """Return all stored chunks and embeddings."""
    return documents


def clear_documents():
    """Clear all stored documents."""
    documents.clear()