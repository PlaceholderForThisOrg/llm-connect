import os


def embedding_model() -> str:
    return os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")


def embedding_dimensions() -> int:
    return int(os.environ.get("EMBEDDING_DIMENSIONS", "768"))
