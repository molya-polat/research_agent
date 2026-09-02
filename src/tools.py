"""Tool definitions and dispatch for the agent loop."""
from src.retriever import search_knowledge_base
from src.web_search import search_web


# ---- Tool schemas (what Claude sees) ----

WEB_SEARCH_TOOL = {
    "name": "search_web",
    "description": (
        "Search the live web for recent information, news, or anything "
        "published after the AI safety papers in the knowledge base. "
        "Use this for current events, recent research, or topics not "
        "covered by academic literature."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query. Be specific and concise.",
            }
        },
        "required": ["query"],
    },
}

SEARCH_KB_TOOL = {
    "name": "search_knowledge_base",
    "description": (
        "Search a curated corpus of 23 AI safety and alignment research "
        "papers (arXiv 2016-2024 and Anthropic transformer-circuits "
        "reports). Topics include: reward modeling, RLHF, Constitutional "
        "AI, mesa-optimization, deceptive alignment, sleeper agents, "
        "scalable oversight, mechanistic interpretability, and red-teaming. "
        "Use this for foundational or technical questions in these areas — "
        "it returns direct passages from primary sources with citations."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "The semantic search query. Use the language a paper "
                    "would use — e.g. 'reward hacking' or 'mesa-optimizer'."
                ),
            }
        },
        "required": ["query"],
    },
}


ALL_TOOLS = [WEB_SEARCH_TOOL, SEARCH_KB_TOOL]


# ---- Dispatch (how we execute what Claude requests) ----

def run_tool(name: str, tool_input: dict) -> str:
    """Execute a tool by name and return a string result for Claude."""
    if name == "search_web":
        results = search_web(query=tool_input["query"], max_results=5)
        if not results:
            return "No results found."
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                f"[{i}] {r.title}\nURL: {r.url}\n{r.content}"
            )
        return "\n\n".join(formatted)
    
    if name == "search_knowledge_base":
        results = search_knowledge_base(query=tool_input["query"], top_k=5)
        if not results:
            return "No results found."
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                f"[{i}] \"{r.title}\" ({r.first_author}, {r.year}) "
                f"— arXiv:{r.arxiv_id}, chunk {r.chunk_index}\n{r.text}"
            )
        return "\n\n".join(formatted)


    return f"Error: unknown tool '{name}'"