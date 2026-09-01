import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .chunker import Chunk
from .config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL


def get_chroma_client() -> chromadb.PersistentClient:
    """One persistent Chroma client, writing to disk under .chroma/."""
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )


def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model (first call downloads it, ~80 MB)."""
    return SentenceTransformer(EMBEDDING_MODEL)


def build_index(chunks: list[Chunk]) -> None:
    """Embed every chunk and store in ChromaDB. Rebuilds from scratch."""
    client = get_chroma_client()

    # Delete existing collection so re-runs give a clean state.
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass  # first run, collection didn't exist yet

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    print(f"Loading embedding model '{EMBEDDING_MODEL}'...")
    model = get_embedding_model()

    print(f"Embedding {len(chunks)} chunks (this takes a few minutes)...")
    texts = [c.text for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

    print("Writing to ChromaDB...")
    collection.add(
        ids=[c.chunk_id for c in chunks],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[
            {
                "filename": c.filename,
                "arxiv_id": c.arxiv_id,
                "title": c.title,
                "first_author": c.first_author,
                "year": c.year,
                "chunk_index": c.chunk_index,
            }
            for c in chunks
        ],
    )
    print(f"✓ Indexed {len(chunks)} chunks into collection '{COLLECTION_NAME}'")