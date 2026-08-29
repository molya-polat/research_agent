from src.loader import load_all_documents

docs = load_all_documents()
print(f"\nLoaded {len(docs)} documents.")
print(f"\nFirst doc: {docs[0].title}")
print(f"Pages: {len(docs[0].pages)}")
print(f"First 300 chars of page 1:\n{docs[0].pages[0][:300]}")