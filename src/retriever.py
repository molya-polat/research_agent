from dataclasses import dataclass

from .indexer import get_chroma_client, get_embedding_model
from .config import COLLECTION_NAME, TOP_K


@dataclass
class SearchResult:
    """One retrieved chunk with metadata and similarity score."""
    text: str
    title: str
    arxiv_id: str
    first_author: str
    year: str
    chunk_index: int
    distance: float  # cosine distance: lower = more similar


# Module-level caching so repeated calls don't reload the model / reconnect.
_collection = None
_model = None


def _get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def _get_model():
    global _model
    if _model is None:
        _model = get_embedding_model()
    return _model


def search_knowledge_base(query: str, top_k: int = TOP_K) -> list[SearchResult]:
    """Search the RAG index. Returns top_k most similar chunks."""
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    output = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append(SearchResult(
            text=text,
            title=meta["title"],
            arxiv_id=meta["arxiv_id"],
            first_author=meta["first_author"],
            year=meta["year"],
            chunk_index=meta["chunk_index"],
            distance=dist,
        ))
    return output