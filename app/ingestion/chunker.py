import re
import uuid
from typing import Any

from app.models.schemas import DocumentChunk


def normalize_text(text: str) -> str:
    """
    Clean excessive whitespace while preserving paragraph breaks.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = [line.strip() for line in text.split("\n")]

    cleaned_lines: list[str] = []
    previous_line_was_blank = False

    for line in lines:
        if line:
            cleaned_lines.append(line)
            previous_line_was_blank = False
        elif not previous_line_was_blank:
            cleaned_lines.append("")
            previous_line_was_blank = True

    return "\n".join(cleaned_lines).strip()


def split_into_sentences(text: str) -> list[str]:
    """
    Split long paragraphs into sentences without requiring an
    external NLP library.
    """
    sentence_pattern = r"(?<=[.!?])\s+(?=[A-Z0-9])"

    sentences = re.split(sentence_pattern, text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def split_long_text(
    text: str,
    chunk_size: int,
) -> list[str]:
    """
    Split a paragraph that is longer than chunk_size.

    The function first attempts to split by sentences. If a single
    sentence is still too long, it falls back to word-aware splitting.
    """
    sentences = split_into_sentences(text)

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        if sentence_length > chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk).strip())
                current_chunk = []
                current_length = 0

            words = sentence.split()
            word_chunk: list[str] = []
            word_chunk_length = 0

            for word in words:
                additional_length = len(word) + (
                    1 if word_chunk else 0
                )

                if (
                    word_chunk
                    and word_chunk_length + additional_length
                    > chunk_size
                ):
                    chunks.append(" ".join(word_chunk).strip())
                    word_chunk = [word]
                    word_chunk_length = len(word)
                else:
                    word_chunk.append(word)
                    word_chunk_length += additional_length

            if word_chunk:
                chunks.append(" ".join(word_chunk).strip())

            continue

        additional_length = sentence_length + (
            1 if current_chunk else 0
        )

        if (
            current_chunk
            and current_length + additional_length > chunk_size
        ):
            chunks.append(" ".join(current_chunk).strip())
            current_chunk = [sentence]
            current_length = sentence_length
        else:
            current_chunk.append(sentence)
            current_length += additional_length

    if current_chunk:
        chunks.append(" ".join(current_chunk).strip())

    return chunks


def get_overlap_text(
    text: str,
    chunk_overlap: int,
) -> str:
    """
    Create overlap using complete sentences where possible.

    This avoids starting a new chunk in the middle of a word.
    """
    if chunk_overlap <= 0:
        return ""

    sentences = split_into_sentences(text)

    overlap_sentences: list[str] = []
    overlap_length = 0

    for sentence in reversed(sentences):
        sentence_length = len(sentence) + (
            1 if overlap_sentences else 0
        )

        if (
            overlap_sentences
            and overlap_length + sentence_length > chunk_overlap
        ):
            break

        overlap_sentences.insert(0, sentence)
        overlap_length += sentence_length

    overlap_text = " ".join(overlap_sentences).strip()

    if len(overlap_text) > chunk_overlap:
        words = overlap_text.split()
        selected_words: list[str] = []
        selected_length = 0

        for word in reversed(words):
            additional_length = len(word) + (
                1 if selected_words else 0
            )

            if (
                selected_words
                and selected_length + additional_length
                > chunk_overlap
            ):
                break

            selected_words.insert(0, word)
            selected_length += additional_length

        overlap_text = " ".join(selected_words)

    return overlap_text


def split_text(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """
    Split text using paragraph and sentence boundaries.

    This reduces chunks that begin or end in the middle of sentences,
    making retrieved evidence and citations easier to verify.
    """
    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero."
        )

    if chunk_overlap < 0:
        raise ValueError(
            "chunk_overlap cannot be negative."
        )

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    normalized_text = normalize_text(text)

    if not normalized_text:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(
            r"\n\s*\n",
            normalized_text,
        )
        if paragraph.strip()
    ]

    text_units: list[str] = []

    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            text_units.append(paragraph)
        else:
            text_units.extend(
                split_long_text(
                    text=paragraph,
                    chunk_size=chunk_size,
                )
            )

    chunks: list[str] = []
    current_parts: list[str] = []
    current_length = 0

    for unit in text_units:
        separator_length = 2 if current_parts else 0
        proposed_length = (
            current_length
            + separator_length
            + len(unit)
        )

        if current_parts and proposed_length > chunk_size:
            completed_chunk = "\n\n".join(
                current_parts
            ).strip()

            if completed_chunk:
                chunks.append(completed_chunk)

            overlap_text = get_overlap_text(
                text=completed_chunk,
                chunk_overlap=chunk_overlap,
            )

            current_parts = (
                [overlap_text, unit]
                if overlap_text
                else [unit]
            )

            current_length = len(
                "\n\n".join(current_parts)
            )

            if current_length > chunk_size:
                current_parts = [unit]
                current_length = len(unit)

        else:
            current_parts.append(unit)
            current_length = proposed_length

    if current_parts:
        final_chunk = "\n\n".join(current_parts).strip()

        if final_chunk:
            chunks.append(final_chunk)

    return chunks


def create_document_chunks(
    pages: list[dict[str, Any]],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[DocumentChunk]:
    """
    Convert page-level document content into structured chunks while
    preserving the document name, page number, and metadata.
    """
    document_chunks: list[DocumentChunk] = []

    for page in pages:
        page_text = page.get("text", "").strip()

        if not page_text:
            continue

        text_chunks = split_text(
            text=page_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for chunk_index, chunk_text in enumerate(
            text_chunks
        ):
            document_chunks.append(
                DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    text=chunk_text,
                    document_name=page[
                        "document_name"
                    ],
                    page_number=page.get(
                        "page_number"
                    ),
                    metadata={
                        **page.get("metadata", {}),
                        "chunk_index": chunk_index,
                        "chunking_strategy":
                            "paragraph_sentence_aware",
                    },
                )
            )

    return document_chunks
