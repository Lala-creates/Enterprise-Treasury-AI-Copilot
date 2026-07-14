from app.ingestion.chunker import split_text


def test_split_text_creates_multiple_chunks() -> None:
    text = "A" * 2500
    chunks = split_text(text, chunk_size=1000, chunk_overlap=100)

    assert len(chunks) == 3
    assert all(chunks)
