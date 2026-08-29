from src.loader import load_all_documents
from src.chunker import chunk_all

docs = load_all_documents()
print(f"\nChunking {len(docs)} documents...\n")

chunks = chunk_all(docs)

print(f"\nTotal chunks: {len(chunks)}")
print(f"\nSample chunk (first from first doc):")
print(f"  ID: {chunks[0].chunk_id}")
print(f"  Title: {chunks[0].title}")
print(f"  Length: {len(chunks[0].text)} chars")
print(f"  First 200 chars:\n{chunks[0].text[:200]}")

# Sanity check: average chunk length
avg_len = sum(len(c.text) for c in chunks) / len(chunks)
print(f"\nAverage chunk length: {avg_len:.0f} chars")