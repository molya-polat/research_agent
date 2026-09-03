"""Streamlit UI for the research assistant."""

import streamlit as st

from src.agent import (
    ErrorEvent,
    FinalAnswerEvent,
    ThinkingEvent,
    ToolCallEvent,
    ToolResultEvent,
    stream_agent,
)


# ---- Page setup ----

st.set_page_config(
    page_title="AI Safety Research Assistant",
    page_icon="📚",
    layout="centered",
)

st.title("AI Safety Research Assistant")
st.caption(
    "Agentic RAG over 23 AI safety papers + live web search. "
    "Ask a question and watch the agent plan, retrieve, and synthesize."
)

with st.expander("How it works"):
    st.markdown(
        """
        The agent has two tools:

        - **search_knowledge_base** — semantic search over a curated corpus
          of 23 AI safety and alignment papers (arXiv, ~1,600 chunks in
          ChromaDB with sentence-transformers embeddings).
        - **search_web** — live web search via Tavily for recent
          information not covered by the corpus.

        The agent decides which tool to use for each part of your question,
        calls them, reads results, and synthesizes a final answer with
        citations.
        """
    )


# ---- Input ----

question = st.text_input(
    "Ask a research question",
    placeholder="e.g. What is Constitutional AI, and what recent research builds on it?",
)

col1, _ = st.columns([1, 3])
run = col1.button("Research", type="primary", disabled=not question.strip())


# ---- Run the agent and stream events ----

if run:
    trace_container = st.container()
    answer_container = st.container()
    sources_container = st.container()

    web_sources: list[dict] = []  # collected as we go

    with trace_container:
        st.subheader("Agent trace")

    try:
        for event in stream_agent(question):
            with trace_container:
                if isinstance(event, ThinkingEvent):
                    st.markdown(f"💭 *{event.text}*")

                elif isinstance(event, ToolCallEvent):
                    st.markdown(
                        f"🔧 **Calling `{event.name}`** with "
                        f"`{event.input}`"
                    )

                elif isinstance(event, ToolResultEvent):
                    with st.expander(f"📄 Result from `{event.name}`"):
                        st.text(event.result)
                    
                    if event.name == "search_web":
                        for line in event.result.split("\n"):
                            if line.startswith("URL:"):
                                web_sources.append({"url": line[5:].strip()})

                elif isinstance(event, ErrorEvent):
                    st.error(event.message)

            if isinstance(event, FinalAnswerEvent):
                with answer_container:
                    st.subheader("Answer")
                    st.markdown(event.text)
                if web_sources:
                    with sources_container:
                        st.subheader("Web sources")
                        for i,source in enumerate(web_sources, 1):
                            st.markdown(f"[{i}] {source['url']}")

    except Exception as e:
        st.error(f"Something went wrong: {e}")