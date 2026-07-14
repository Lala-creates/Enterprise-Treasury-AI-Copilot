from pathlib import Path
from typing import Any

import fitz


class UnsupportedDocumentError(ValueError):
    pass


def load_pdf(file_path: str | Path) -> list[dict[str, Any]]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise UnsupportedDocumentError(
            f"Unsupported file type: {path.suffix}"
        )

    pages: list[dict[str, Any]] = []

    with fitz.open(path) as pdf:
        for page_index, page in enumerate(pdf):
            text = page.get_text("text").strip()

            if not text:
                continue

            pages.append(
                {
                    "document_name": path.name,
                    "page_number": page_index + 1,
                    "text": text,
                    "metadata": {
                        "source_path": str(path),
                        "file_type": "pdf",
                    },
                }
            )

    if not pages:
        raise ValueError(
            f"No readable text was extracted from {path.name}"
        )

    return pages
