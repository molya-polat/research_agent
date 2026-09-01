"""Run once to build the RAG index. Re-run if you change the corpus."""

from src.loader import load_all_documents
from src.chunker import chunk_all
from src.indexer import build_index


def main() -> None:
    print("Loading documents...\n")
    docs = load_all_documents()

    print(f"\nChunking {len(docs)} documents...\n")
    chunks = chunk_all(docs)

    print(f"\nTotal chunks: {len(chunks)}")
    print("\nBuilding index...\n")
    build_index(chunks)

    print("\n✓ Done. Vector store is ready at .chroma/")


if __name__ == "__main__":
    main()