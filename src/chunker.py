from dataclasses import dataclass

import tiktoken

from .config import CHUNK_SIZE, CHUNK_OVERLAP
from .loader import Document


@dataclass
class Chunk:
    """A piece of a document, ready to be embedded and stored."""
    text: str
    filename: str
    arxiv_id: str
    title: str
    first_author: str
    year: str
    chunk_index: int   # position of this chunk within its document

    @property
    def chunk_id(self) -> str:
        """Unique ID for ChromaDB — filename plus position."""
        return f"{self.filename}::chunk_{self.chunk_index}"


# One tokenizer instance, reused across all calls (loading it is slow).
_encoder = tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks measured in tokens."""
    tokens = _encoder.encode(text)
    if not tokens:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(_encoder.decode(chunk_tokens))
        if end >= len(tokens):
            break
        start += step

    return chunks


def chunk_document(doc: Document) -> list[Chunk]:
    """Chunk one document, preserving its metadata on every chunk."""
    text_pieces = chunk_text(doc.full_text, CHUNK_SIZE, CHUNK_OVERLAP)
    return [
        Chunk(
            text=piece,
            filename=doc.filename,
            arxiv_id=doc.arxiv_id,
            title=doc.title,
            first_author=doc.first_author,
            year=doc.year,
            chunk_index=i,
        )
        for i, piece in enumerate(text_pieces)
    ]


def chunk_all(documents: list[Document]) -> list[Chunk]:
    """Chunk every document and return one flat list."""
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"  {doc.filename}: {len(chunks)} chunks")
    return all_chunks