from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MANIFEST_PATH = DATA_DIR / "manifest.csv"
CHROMA_DIR = PROJECT_ROOT / ".chroma"

# Chunking
CHUNK_SIZE = 500        # target tokens per chunk
CHUNK_OVERLAP = 50      # tokens shared between adjacent chunks

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ChromaDB
COLLECTION_NAME = "ai_safety_papers"

# Retrieval
TOP_K = 5               # how many chunks to return per query