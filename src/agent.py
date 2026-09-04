"""The single-agent research assistant."""

from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Iterator
from dataclasses import dataclass

from src.tools import ALL_TOOLS, run_tool

try:
    import streamlit as st
    for key in ("ANTHROPIC_API_KEY", "TAVILY_API_KEY"):
        if key in st.secrets and not os.environ.get(key):
            os.environ[key] = st.secrets[key]
except (ImportError, FileNotFoundError, AttributeError):
    pass  # not running under Streamlit, or no secrets file — .env is used


SYSTEM_PROMPT = """You are a research assistant with two knowledge sources:

1. A curated corpus of 23 AI safety and alignment papers (arXiv + Anthropic \
transformer-circuits). Use `search_knowledge_base` for foundational or \
technical concepts, primary source citations, or anything the corpus is \
likely to cover.

2. The live web via `search_web`. Use this for current events, recent \
research (2025 onward), organizational news, or topics outside the corpus.

Strategy:
- For a mixed question ("what is X and what's new about it"), use BOTH \
tools — one call per source.
- Prefer the knowledge base for technical claims, since it gives you \
primary source passages you can cite precisely.
- Do not answer from your own prior knowledge — always search first, then \
cite what you found.

Final answer:
- Concise. Structured with short headings if helpful.
- Cite knowledge-base sources as (First-author et al., Year, arXiv:ID).
- Cite web sources by [number] with URL.
- Do not make claims without a citation."""


MAX_ITERATIONS = 10  # safety cap — stop the loop if it runs away

load_dotenv()  
# ---- Event types (what the agent yields) ----

@dataclass
class ThinkingEvent:
    text: str          # narration between tool calls

@dataclass
class ToolCallEvent:
    name: str
    input: dict

@dataclass
class ToolResultEvent:
    name: str
    result: str

@dataclass
class FinalAnswerEvent:
    text: str

@dataclass
class ErrorEvent:
    message: str


AgentEvent = (
    ThinkingEvent | ToolCallEvent | ToolResultEvent | FinalAnswerEvent | ErrorEvent
)


# ---- The generator ----

def stream_agent(user_question: str) -> Iterator[AgentEvent]:
    """Run the agent, yielding events as they happen."""
    client = Anthropic()
    messages = [{"role": "user", "content": user_question}]

    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            final_text = "".join(
                b.text for b in response.content if b.type == "text"
            )
            yield FinalAnswerEvent(text=final_text)
            return

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "text" and block.text.strip():
                    yield ThinkingEvent(text=block.text)
                if block.type == "tool_use":
                    yield ToolCallEvent(name=block.name, input=block.input)
                    result = run_tool(block.name, block.input)
                    yield ToolResultEvent(name=block.name, result=result)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        yield ErrorEvent(message=f"Unexpected stop_reason: {response.stop_reason}")
        return

    yield ErrorEvent(message="Agent exceeded max iterations without finishing.")

def run_agent(user_question: str, verbose: bool = True) -> str:
    """Run the agent loop until Claude produces a final answer."""
    client = Anthropic()
    messages = [{"role": "user", "content": user_question}]

    for iteration in range(MAX_ITERATIONS):
        if verbose:
            print(f"\n--- Iteration {iteration + 1} ---")

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            messages=messages,
        )

        # Save Claude's response into the conversation history.
        messages.append({"role": "assistant", "content": response.content})

        # Case 1: Claude is done answering.
        if response.stop_reason == "end_turn":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            if verbose:
                print(f"\n[Final answer]\n{final_text}")
            return final_text

        # Case 2: Claude wants to use one or more tools.
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "text" and verbose:
                    print(f"[Claude] {block.text}")
                if block.type == "tool_use":
                    if verbose:
                        print(f"[Tool call] {block.name}({block.input})")
                    result = run_tool(block.name, block.input)
                    if verbose:
                        print(f"[Tool result] {result[:200]}...")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Feed tool results back as a user message.
            messages.append({"role": "user", "content": tool_results})
            continue

        # Case 3: something unexpected (max_tokens, refusal, etc.)
        if verbose:
            print(f"[Unexpected stop_reason: {response.stop_reason}]")
        return "Agent stopped unexpectedly."

    return "Agent exceeded max iterations without finishing."