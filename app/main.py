"""
Enterprise Treasury AI Copilot
FastAPI Application (v1)

This version expands the starter app with:
- API metadata
- CORS support
- Health and readiness endpoints
- Root information endpoint
- Document upload endpoint
- Chat endpoint
- Better exception handling
"""

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.ingestion.chunker import create_document_chunks
from app.ingestion.document_loader import load_pdf
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    UploadResponse,
)
from app.services.chat_service import ChatService
from app.services.embedding_service import EmbeddingService

app = FastAPI(
    title="Enterprise Treasury AI Copilot API",
    description="Production-oriented API for Treasury AI, RAG and document intelligence.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_service = EmbeddingService()
chat_service = ChatService()


@app.get("/")
def root():
    return {
        "application": "Enterprise Treasury AI Copilot",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "chat_model": settings.chat_model,
        "embedding_model": settings.embedding_model,
    }


@app.get("/ready")
def readiness():
    return {"ready": True}


@app.post("/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or "uploaded.pdf"

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF documents are currently supported.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = Path(tmp.name)

        pages = load_pdf(temp_path)

        for page in pages:
            page["document_name"] = filename

        chunks = create_document_chunks(
            pages,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        count = embedding_service.index_chunks(chunks)

        return UploadResponse(
            document_name=filename,
            chunks_created=count,
            status="indexed",
        )

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )

    finally:
        await file.close()

        if temp_path and temp_path.exists():
            temp_path.unlink()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return chat_service.answer_question(
            question=request.question,
            top_k=request.top_k,
            conversation_history=[
                message.model_dump()
                for message in request.conversation_history
            ],
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chat request failed: {exc}",
        ) from exc


@app.get("/documents")
def list_documents():
    """
    Placeholder endpoint.

    In the next milestone this will query PostgreSQL
    and return every indexed document.
    """
    return {
        "message": "Not implemented yet.",
        "next_milestone": "PostgreSQL document catalog",
    }


@app.post("/compare")
def compare_documents():
    """
    Placeholder endpoint.

    Future feature:
    Basel III vs Internal Treasury Policy comparison.
    """
    return {
        "message": "Coming soon."
    }


@app.post("/generate/user-stories")
def generate_user_stories():
    """
    Future feature.

    Generate:
    - Business Requirements
    - User Stories
    - Acceptance Criteria
    """
    return {
        "message": "Coming soon."
    }

