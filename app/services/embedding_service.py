import chromadb
from openai import OpenAI

from app.core.config import settings
from app.models.schemas import DocumentChunk


class EmbeddingService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.openai_client = OpenAI(
            api_key=settings.openai_api_key
        )

        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_directory
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def create_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        response = self.openai_client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
        )

        return [item.embedding for item in response.data]

    def index_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> int:
        if not chunks:
            return 0

        texts = [chunk.text for chunk in chunks]
        embeddings = self.create_embeddings(texts)

        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=texts,
            embeddings=embeddings,
            metadatas=[
                {
                    "document_name": chunk.document_name,
                    "page_number": chunk.page_number or 0,
                    **{
                        key: str(value)
                        for key, value in chunk.metadata.items()
                    },
                }
                for chunk in chunks
            ],
        )

        return len(chunks)
