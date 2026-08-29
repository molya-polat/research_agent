import csv
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from .config import DATA_DIR, MANIFEST_PATH


@dataclass
class Document:
    """One paper's full text plus metadata."""
    filename: str
    arxiv_id: str
    title: str
    first_author: str
    year: str
    pages: list[str]  # one string per page

    @property
    def full_text(self) -> str:
        return "\n\n".join(self.pages)


def load_manifest() -> list[dict]:
    """Read manifest.csv into a list of dicts, one per paper."""
    with open(MANIFEST_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_pdf(path: Path) -> list[str]:
    """Extract text page-by-page from a PDF."""
    reader = PdfReader(str(path))
    return [page.extract_text() or "" for page in reader.pages]


def load_all_documents() -> list[Document]:
    """Load every paper listed in the manifest."""
    manifest = load_manifest()
    documents = []
    for row in manifest:
        pdf_path = DATA_DIR / row["filename"]
        if not pdf_path.exists():
            print(f"⚠️  Missing PDF: {row['filename']}")
            continue
        pages = load_pdf(pdf_path)
        documents.append(Document(
            filename=row["filename"],
            arxiv_id=row["arxiv_id"],
            title=row["title"],
            first_author=row["first_author"],
            year=row["year"],
            pages=pages,
        ))
        print(f"✓ Loaded {row['filename']} ({len(pages)} pages)")
    return documents