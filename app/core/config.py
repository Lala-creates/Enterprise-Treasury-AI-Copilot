import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
    embedding_model: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL",
        "text-embedding-3-small",
    )

    chroma_directory: str = os.getenv(
        "CHROMA_DIRECTORY",
        "./data/chroma",
    )

    collection_name: str = os.getenv(
        "CHROMA_COLLECTION_NAME",
        "treasury_documents",
    )

    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))


settings = Settings()
