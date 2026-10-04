import uuid
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables before importing services
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.pdf_processor import extract_pdf_text
from app.services.chunking import chunk_pages
from app.services.embedding_service import create_embeddings

from app.storage.document_store import (
    add_documents,
    get_documents,
    get_all_documents,
    delete_document
)

from app.services.similarity_search import search_with_pgvector
from app.services.llm_service import generate_answer


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="AI Research Assistant",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# BASIC ROUTES
# =========================================================

@app.get("/")
def home():
    return {
        "message": "AI Research Assistant API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# REQUEST MODELS
# =========================================================

class Message(BaseModel):
    text: str


class SearchRequest(BaseModel):
    question: str
    document_id: str
    top_k: int = Field(default=3, ge=1, le=20)


# =========================================================
# TEST ROUTE
# =========================================================

@app.post("/test")
def test_message(message: Message):
    return {
        "received": message.text,
        "status": "success"
    }


# =========================================================
# PDF UPLOAD
# =========================================================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # 1. Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file"
        )

    # 2. Read uploaded file
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty"
        )

    # 3. Extract text, create chunks, and generate embeddings
    try:
        pages = extract_pdf_text(file_bytes)
        print("PDF pages:", len(pages))

        chunks = chunk_pages(pages)
        print("Chunks:", len(chunks))

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No extractable text found in this PDF"
            )

        embeddings = create_embeddings(
            [chunk["text"] for chunk in chunks]
        )

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Number of embeddings does not match number of chunks"
            )

        # 4. Create a unique ID for this PDF
        document_id = str(uuid.uuid4())

        # 5. Store chunks and embeddings in Supabase
        add_documents(
            chunks,
            embeddings,
            document_id,
            filename=file.filename,
            total_pages=len(pages)
        )

        print("Embeddings:", len(embeddings))

    except HTTPException:
        raise

    except Exception as e:
        print("UPLOAD ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="PDF processing, embedding, or storage failed"
        )

    # 6. Return document details
    return {
        "document_id": document_id,
        "filename": file.filename,
        "total_pages": len(pages),
        "total_chunks": len(chunks),
        "embedding_dimensions": (
            len(embeddings[0]) if embeddings else 0
        ),
        "chunks": [
            {
                "page": chunk["page"],
                "text": chunk["text"],
                "embedding_created": bool(embeddings[i])
            }
            for i, chunk in enumerate(chunks)
        ]
    }


# =========================================================
# GET ALL DOCUMENTS
# =========================================================

@app.get("/documents")
def list_documents():

    try:
        all_documents = get_all_documents()

        return {
            "total_documents": len(all_documents),
            "documents": all_documents
        }

    except Exception as e:
        print("DOCUMENT LIST ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve documents"
        )


# =========================================================
# DELETE DOCUMENT
# =========================================================

@app.delete("/documents/{document_id}")
def remove_document(document_id: str):

    try:
        deleted = delete_document(document_id)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )

    except Exception as e:
        print("DELETE ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Could not delete document"
        )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }


# =========================================================
# SEMANTIC SEARCH
# =========================================================

@app.post("/search")
def search(request: SearchRequest):

    # 1. Validate question
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # 2. Check document exists and has chunks
    try:

        documents = get_documents(
            request.document_id
        )

        if not documents:
            raise HTTPException(
                status_code=404,
                detail="Document not found or has no chunks"
            )

        # 3. Convert question into an embedding
        query_embedding = create_embeddings(
            [question]
        )[0]

        # 4. Search using Supabase pgvector
        results = search_with_pgvector(
            query_embedding=query_embedding,
            document_id=request.document_id,
            top_k=request.top_k
        )

    except HTTPException:
        raise

    except ValueError as e:

        print(
            "SEARCH VALIDATION ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid document ID or search input"
        )

    except Exception as e:

        print(
            "SEARCH ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Search or embedding failed"
        )

    # 5. Return matching passages
    return {
        "document_id": request.document_id,
        "question": question,
        "total_results": len(results),
        "results": results
    }


# =========================================================
# ASK AI
# =========================================================

@app.post("/ask")
def ask_question(request: SearchRequest):

    # 1. Validate question
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:

        # 2. Check document exists and has chunks
        document_chunks = get_documents(
            request.document_id
        )

        if not document_chunks:
            raise HTTPException(
                status_code=404,
                detail="Document not found or has no chunks"
            )

        # 3. Convert question into an embedding
        query_embedding = create_embeddings(
            [question]
        )[0]

        # 4. Retrieve relevant chunks from Supabase
        results = search_with_pgvector(
            query_embedding=query_embedding,
            document_id=request.document_id,
            top_k=request.top_k
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No relevant chunks found"
            )

        # 5. Build context for the AI
        context = "\n\n".join(
            f"Page {item['page']}:\n{item['text']}"
            for item in results
        )

        # 6. Generate answer using your LLM
        answer = generate_answer(
            question,
            context
        )

    except HTTPException:
        raise

    except ValueError as e:

        print(
            "ASK VALIDATION ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid document ID or input"
        )

    except Exception as e:

        print(
            "ASK ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Answer generation or retrieval failed"
        )

    # 7. Return answer and source information
    return {
        "document_id": request.document_id,
        "question": question,
        "answer": answer,
        "sources": [
            {
                "page": item["page"],
                "score": item["score"],
                "text": item["text"]
            }
            for item in results
        ]
    }