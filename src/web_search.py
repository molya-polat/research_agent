from dataclasses import dataclass
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
try:
    import streamlit as st
    for key in ("TAVILY_API_KEY",):
        if key in st.secrets and not os.environ.get(key):
            os.environ[key] = st.secrets[key]
except (ImportError, FileNotFoundError, AttributeError):
    pass
@dataclass
class WebResult:
    """One web search result."""
    title: str
    url: str
    content: str  # short snippet Tavily extracts


# Lazy singleton — created on first call, reused after.
_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        _client = TavilyClient()
    return _client


def search_web(query: str, max_results: int = 5) -> list[WebResult]:
    """Search the web via Tavily. Returns top max_results snippets."""
    client = _get_client()
    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic",  # 'advanced' costs more per search
    )
    return [
        WebResult(
            title=r["title"],
            url=r["url"],
            content=r["content"],
        )
        for r in response["results"]
    ]