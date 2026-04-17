import os
from pathlib import Path
from typing import List
import numpy as np
import faiss
from ..config import get_settings
from ..core.openai_client import embed_texts

settings = get_settings()


VECTOR_DIM = 1536
INDEX_PATH = Path(settings.vector_dir) / "faiss.index"
TEXT_STORE_PATH = Path(settings.vector_dir) / "text_store.txt"


def _ensure_vector_dir() -> None:
    os.makedirs(settings.vector_dir, exist_ok=True)


def _load_index() -> faiss.IndexFlatL2:
    _ensure_vector_dir()
    if INDEX_PATH.exists():
        return faiss.read_index(str(INDEX_PATH))
    return faiss.IndexFlatL2(VECTOR_DIM)


def _persist_index(index: faiss.IndexFlatL2) -> None:
    faiss.write_index(index, str(INDEX_PATH))


def _append_texts(texts: List[str]) -> None:
    _ensure_vector_dir()
    with open(TEXT_STORE_PATH, "a", encoding="utf-8") as handle:
        for text in texts:
            handle.write(text.replace("\n", " ") + "\n")


async def index_entries(entries: List[str]) -> None:
    if not entries:
        return
    embeddings = await embed_texts(entries)
    index = _load_index()
    index.add(np.array(embeddings, dtype="float32"))
    _persist_index(index)
    _append_texts(entries)
