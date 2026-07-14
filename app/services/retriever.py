from typing import Any

from app.core.config import settings
from app.services.embedding_service import EmbeddingService


class Retriever:
    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.embedding_service = (
            embedding_service or EmbeddingService()
        )

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        minimum_similarity: float = 0.35,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the most relevant document chunks.

        Results below the minimum similarity threshold are excluded.
        For cosine distance in ChromaDB:

            similarity_score = 1 - distance
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if not 0 <= minimum_similarity <= 1:
            raise ValueError(
                "minimum_similarity must be between 0 and 1."
            )

        result_count = top_k or settings.retrieval_top_k

        query_embeddings = (
            self.embedding_service.create_embeddings([query])
        )

        if not query_embeddings:
            return []

        query_embedding = query_embeddings[0]

        results = self.embedding_service.collection.query(
            query_embeddings=[query_embedding],
            n_results=result_count,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        retrieved: list[dict[str, Any]] = []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for chunk_id, document, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):
            if document is None or metadata is None:
                continue

            similarity_score = 1 - float(distance)

            if similarity_score < minimum_similarity:
                continue

            retrieved.append(
                {
                    "chunk_id": chunk_id,
                    "text": document,
                    "document_name": metadata.get(
                        "document_name",
                        "Unknown document",
                    ),
                    "page_number": metadata.get("page_number"),
                    "distance": float(distance),
                    "similarity_score": similarity_score,
                    "metadata": metadata,
                }
            )

        retrieved.sort(
            key=lambda item: item["similarity_score"],
            reverse=True,
        )

        return retrieved
