
from app.database import engine
from app.models.document import Document, DocumentChunk
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID


def add_documents(
    chunks,
    embeddings,
    document_id,
    filename="Unknown",
    total_pages=0
):
    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings count must match")

    doc_id = UUID(str(document_id))

    with Session(engine) as session:
        document = Document(
            id=doc_id,
            filename=filename,
            total_pages=total_pages,
            total_chunks=len(chunks)
        )
        session.add(document)

        for chunk, embedding in zip(chunks, embeddings):
            session.add(
                DocumentChunk(
                    document_id=doc_id,
                    page=chunk["page"],
                    content=chunk["text"],
                    embedding=embedding
                )
            )

        session.commit()


def get_documents(document_id=None):
    with Session(engine) as session:
        query = select(DocumentChunk)

        if document_id is not None:
            query = query.where(
                DocumentChunk.document_id == UUID(str(document_id))
            )

        rows = session.scalars(query).all()

        return [
            {
                "document_id": str(row.document_id),
                "page": row.page,
                "text": row.content,
                "embedding": row.embedding
            }
            for row in rows
        ]


def get_all_documents():
    with Session(engine) as session:
        rows = session.scalars(select(Document)).all()

        return [
            {
                "document_id": str(row.id),
                "filename": row.filename,
                "total_pages": row.total_pages,
                "total_chunks": row.total_chunks,
                "created_at": row.created_at.isoformat()
                if row.created_at else None
            }
            for row in rows
        ]


def get_document_metadata(document_id):
    with Session(engine) as session:
        row = session.get(Document, UUID(str(document_id)))

        if row is None:
            return None

        return {
            "document_id": str(row.id),
            "filename": row.filename,
            "total_pages": row.total_pages,
            "total_chunks": row.total_chunks
        }


def delete_document(document_id):
    with Session(engine) as session:
        row = session.get(Document, UUID(str(document_id)))

        if row is None:
            return False

        session.delete(row)
        session.commit()
        return True


def clear_documents():
    with Session(engine) as session:
        session.query(DocumentChunk).delete()
        session.query(Document).delete()
        session.commit()