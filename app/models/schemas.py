from typing import Any, Literal

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    text: str
    document_name: str
    page_number: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SourceCitation(BaseModel):
    citation_number: int
    document_name: str
    page_number: int | None = None
    excerpt: str
    chunk_id: str

class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)

class ChatRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)

    conversation_history: list[ConversationMessage] = Field(
        default_factory=list,
        max_length=12,
    )


class ChatResponse(BaseModel):
    answer: str
    citations: list[SourceCitation]
    retrieved_chunks: int


class UploadResponse(BaseModel):
    document_name: str
    chunks_created: int
    status: str
