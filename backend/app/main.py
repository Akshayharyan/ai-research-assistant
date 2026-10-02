
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables before importing the OpenAI service
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.services.pdf_processor import extract_pdf_text
from app.services.chunking import chunk_pages
from app.services.embedding_service import create_embeddings


app = FastAPI(
    title="AI Research Assistant",
    version="1.0.0"
)


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


class Message(BaseModel):
    text: str


@app.post("/test")
def test_message(message: Message):
    return {
        "received": message.text,
        "status": "success"
    }


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

        # Avoid making an API request if the PDF has no extractable text
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No extractable text found in this PDF"
            )

        embeddings = create_embeddings(
            [chunk["text"] for chunk in chunks]
        )
        print("Embeddings:", len(embeddings))

    except HTTPException:
        raise

    except Exception as e:
        print("UPLOAD ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="PDF processing or embedding failed"
        )

    # 4. Return a preview (not the full embedding vectors)
    return {
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