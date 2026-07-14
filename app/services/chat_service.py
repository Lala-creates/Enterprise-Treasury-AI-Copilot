from openai import OpenAI

from app.core.config import settings
from app.models.schemas import ChatResponse
from app.prompts.templates import (
    SYSTEM_PROMPT,
    build_rag_prompt,
)
from app.services.citation_service import CitationService
from app.services.retriever import Retriever


class ChatService:
    def __init__(
        self,
        retriever: Retriever | None = None,
        citation_service: CitationService | None = None,
    ) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.retriever = retriever or Retriever()
        self.citation_service = (
            citation_service or CitationService()
        )

    def answer_question(
        self,
        question: str,
        top_k: int = 5,
        conversation_history: list[dict] | None = None,
    ) -> ChatResponse:
        retrieved_chunks = self.retriever.retrieve(
            query=question,
            top_k=top_k,
        )

        if not retrieved_chunks:
            return ChatResponse(
                answer=(
                    "I could not find sufficient information in the "
                    "indexed documents to answer this question."
                ),
                citations=[],
                retrieved_chunks=0,
            )

        user_prompt = build_rag_prompt(
            question=question,
            retrieved_chunks=retrieved_chunks,
            conversation_history=conversation_history or [],
        )

        response = self.client.responses.create(
            model=settings.chat_model,
            instructions=SYSTEM_PROMPT,
            input=user_prompt,
        )

        answer = response.output_text

        citations = self.citation_service.create_citations(
            retrieved_chunks=retrieved_chunks,
            answer=answer,
        )

        response = self.client.responses.create(
            model=settings.chat_model,
            instructions=SYSTEM_PROMPT,
            input=user_prompt,
        )

        answer = response.output_text

        citations = self.citation_service.create_citations(
            retrieved_chunks=retrieved_chunks,
            answer=answer,
        )

        return ChatResponse(
            answer=answer,
            citations=citations,
            retrieved_chunks=len(retrieved_chunks),
        )
