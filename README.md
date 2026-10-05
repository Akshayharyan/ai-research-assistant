# AI Research Assistant

AI Research Assistant is a free, local-first RAG workspace for asking questions about uploaded PDF documents. It extracts page text, creates embeddings, retrieves relevant passages with pgvector, and uses Ollama with Qwen to generate an answer with source pages.

## Features

- PDF upload, page extraction, chunking, and embedding
- Document library with selection and deletion
- Semantic search and grounded question answering
- Source passages with page numbers and relevance scores
- Responsive React workspace with loading, empty, error, and success states
- Local Ollama inference for a zero-cost educational setup

## Architecture

```text
React + Vite
    -> FastAPI
        -> PDF text extraction -> chunks -> Sentence Transformers
        -> PostgreSQL + pgvector
        -> Ollama + Qwen
```

RAG works by retrieving the passages most similar to a question and giving only those passages to the language model. The answer can then be checked against the displayed source passages.

## Stack

- Frontend: React, Vite, JavaScript, CSS
- Backend: Python, FastAPI, Uvicorn
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- Database: PostgreSQL with pgvector, accessed through Supabase-compatible storage
- LLM: Ollama with `qwen2.5:1.5b`

## Project structure

```text
backend/
  app/
    main.py
    services/
    storage/
frontend/
  src/
    components/
    services/api.js
    App.jsx
```

## Local setup

### Backend

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Configure `backend/.env` with the database connection required by the existing SQLAlchemy setup.
4. Start the API:

   ```bash
   uvicorn app.main:app --reload
   ```

The API is available at `http://127.0.0.1:8000`, with Swagger at `/docs`.

### Database

Use a Supabase project or another PostgreSQL instance with pgvector enabled. The existing backend models and storage code define the document and chunk tables used by the application. Keep database credentials in `backend/.env`; never expose them to the frontend.

### Ollama

Install Ollama, start it, and pull the configured model:

```bash
ollama pull qwen2.5:1.5b
```

Ollama must be running at `http://localhost:11434`. Inference remains local and does not require a paid API.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://127.0.0.1:8000`. To use another backend, create `frontend/.env.local`:

```text
VITE_API_URL=http://127.0.0.1:8000
```

Do not put database credentials, API keys, or service-role secrets in `VITE_*` variables.

## API endpoints

- `GET /health` - health check
- `POST /upload` - process a PDF
- `GET /documents` - list uploaded documents
- `DELETE /documents/{document_id}` - delete a document
- `POST /search` - retrieve relevant passages
- `POST /ask` - retrieve passages and generate an answer

## Example workflow

1. Start PostgreSQL/Supabase, Ollama, the FastAPI backend, and the Vite frontend.
2. Upload a PDF from the workspace sidebar.
3. Select it from the library.
4. Ask a question in the chat box.
5. Review the answer and the supporting page passages.

## Deployment and security

The frontend can be deployed as a free static site. The backend needs access to PostgreSQL, the embedding model, and Ollama; for this educational project, running those locally is the supported zero-cost configuration. Do not commit `.env` files or credentials. The repository `.gitignore` excludes environment files.

## Future improvements

- Conversation history per document
- Streaming answers
- Authentication and per-user libraries
- OCR for scanned PDFs
- Automated frontend and backend integration tests

## Screenshots

Add screenshots of the upload, document library, answer, and source views here.
