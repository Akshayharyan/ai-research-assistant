
from sqlalchemy import text
from app.database import engine


def search_with_pgvector(query_embedding, document_id, top_k=3):
    """Return the top matching chunks using Supabase pgvector."""

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20")

    # Convert the embedding list into pgvector's string format.
    embedding_text = "[" + ",".join(
        str(float(value)) for value in query_embedding
    ) + "]"

    sql = text("""
        SELECT id, page, content, similarity
        FROM match_document_chunks(
            CAST(:query_embedding AS extensions.vector),
            CAST(:document_id AS UUID),
            :match_count
        )
    """)

    with engine.connect() as connection:
        result = connection.execute(
            sql,
            {
                "query_embedding": embedding_text,
                "document_id": str(document_id),
                "match_count": top_k
            }
        )

        return [
            {
                "document_id": str(document_id),
                "page": row.page,
                "text": row.content,
                "score": round(float(row.similarity), 4)
            }
            for row in result
        ]