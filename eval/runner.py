"""Run every eval question through the agent and record what happens."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from src.agent import (
    ErrorEvent,
    FinalAnswerEvent,
    ThinkingEvent,
    ToolCallEvent,
    ToolResultEvent,
    stream_agent,
)

QUESTIONS_PATH = Path(__file__).parent / "questions.json"
RESULTS_PATH = Path(__file__).parent / "results.json"


def run_one(question: str) -> dict:
    """Run one question and record the full trace."""
    tool_calls: list[dict] = []
    tool_results: list[str] = []
    final_answer = ""
    error: str | None = None
    started = time.time()

    for event in stream_agent(question):
        if isinstance(event, ToolCallEvent):
            tool_calls.append({"name": event.name, "input": event.input})
        elif isinstance(event, ToolResultEvent):
            tool_results.append(event.result)
        elif isinstance(event, FinalAnswerEvent):
            final_answer = event.text
        elif isinstance(event, ErrorEvent):
            error = event.message
        # ThinkingEvent ignored — not scored.

    elapsed = time.time() - started
    return {
        "tool_calls": tool_calls,
        "tool_results": tool_results,
        "final_answer": final_answer,
        "error": error,
        "elapsed_seconds": round(elapsed, 2),
    }


def main() -> None:
    with open(QUESTIONS_PATH) as f:
        questions = json.load(f)

    results = []
    for i, q in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] {q['id']}")
        print(f"    Q: {q['question']}")
        try:
            run_data = run_one(q["question"])
        except Exception as e:
            print(f"    ✗ Crashed: {e}")
            run_data = {
                "tool_calls": [],
                "tool_results": [],
                "final_answer": "",
                "error": str(e),
                "elapsed_seconds": 0,
            }

        tool_names = [tc["name"] for tc in run_data["tool_calls"]]
        print(f"    Tools called: {tool_names}")
        print(f"    Elapsed: {run_data['elapsed_seconds']}s")

        results.append({**q, **run_data})

    output = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "n_questions": len(questions),
        "results": results,
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Results saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()