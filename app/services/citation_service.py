import re

from app.models.schemas import SourceCitation


class CitationService:
    @staticmethod
    def extract_used_source_numbers(
        answer: str,
    ) -> set[int]:
        """
        Extract source numbers referenced by the model.

        Examples matched:
        [Source 1]
        [Source 1, p.47]
        [Sources 1, 3]
        """
        used_sources: set[int] = set()

        source_groups = re.findall(
            r"\[Sources?\s+([^\]]+)\]",
            answer,
            flags=re.IGNORECASE,
        )

        for group in source_groups:
            numbers = re.findall(r"\d+", group)

            for number in numbers:
                used_sources.add(int(number))

        return used_sources

    @classmethod
    def create_citations(
        cls,
        retrieved_chunks: list[dict],
        answer: str,
        excerpt_length: int = 500,
    ) -> list[SourceCitation]:
        """
        Return citations only for sources referenced in the answer.
        """
        used_source_numbers = cls.extract_used_source_numbers(
            answer
        )

        citations: list[SourceCitation] = []

        for index, chunk in enumerate(
            retrieved_chunks,
            start=1,
        ):
            if index not in used_source_numbers:
                continue

            text = chunk["text"].strip()

            if len(text) > excerpt_length:
                excerpt = (
                    text[:excerpt_length].rstrip() + "..."
                )
            else:
                excerpt = text

            citations.append(
                SourceCitation(
                    citation_number=index,
                    document_name=chunk["document_name"],
                    page_number=chunk.get("page_number"),
                    excerpt=excerpt,
                    chunk_id=chunk["chunk_id"],
                )
            )

        return citations
