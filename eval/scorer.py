"""Score eval results and generate a Markdown report."""

import json
from pathlib import Path

RESULTS_PATH = Path(__file__).parent / "results.json"
REPORT_PATH = Path(__file__).parent / "report.md"


def check_tool_selection(expected: list[str], actual_calls: list[dict]) -> bool:
    """Correct if the set of tools called matches expected exactly."""
    actual_set = {c["name"] for c in actual_calls}
    return actual_set == set(expected)


def check_citations(expected_sources: list[str], final_answer: str) -> tuple[bool, list[str]]:
    """For KB sources, check the arXiv ID appears in the answer.

    Returns (all_found, missing).
    """
    if not expected_sources:
        return True, []
    missing = [s for s in expected_sources if s not in final_answer]
    return len(missing) == 0, missing


def score_one(result: dict) -> dict:
    """Score a single result and return per-question metrics."""
    tool_ok = check_tool_selection(result["expected_tools"], result["tool_calls"])
    cite_ok, missing = check_citations(result["expected_sources"], result["final_answer"])
    return {
        "id": result["id"],
        "category": result["category"],
        "tool_selection_correct": tool_ok,
        "citation_correct": cite_ok,
        "missing_citations": missing,
        "n_tool_calls": len(result["tool_calls"]),
        "elapsed_seconds": result["elapsed_seconds"],
        "error": result.get("error"),
    }


def aggregate(scores: list[dict]) -> dict:
    """Compute aggregate metrics."""
    n = len(scores)
    tool_correct = sum(1 for s in scores if s["tool_selection_correct"])
    cite_correct = sum(1 for s in scores if s["citation_correct"])
    avg_iters = sum(s["n_tool_calls"] for s in scores) / n
    avg_time = sum(s["elapsed_seconds"] for s in scores) / n

    by_category: dict[str, dict] = {}
    for s in scores:
        cat = s["category"]
        if cat not in by_category:
            by_category[cat] = {"n": 0, "tool_ok": 0, "cite_ok": 0}
        by_category[cat]["n"] += 1
        by_category[cat]["tool_ok"] += int(s["tool_selection_correct"])
        by_category[cat]["cite_ok"] += int(s["citation_correct"])

    return {
        "n": n,
        "tool_selection_accuracy": f"{tool_correct}/{n} ({tool_correct/n:.0%})",
        "citation_accuracy": f"{cite_correct}/{n} ({cite_correct/n:.0%})",
        "avg_tool_calls": round(avg_iters, 2),
        "avg_seconds": round(avg_time, 1),
        "by_category": by_category,
    }


def render_report(agg: dict, scores: list[dict]) -> str:
    """Render a Markdown report."""
    lines = [
        "# Evaluation report",
        "",
        f"Ran on {agg['n']} hand-written questions covering four categories:",
        "`kb_only`, `web_only`, `both`, and `out_of_scope`.",
        "",
        "## Aggregate metrics",
        "",
        f"- **Tool-selection accuracy:** {agg['tool_selection_accuracy']}",
        f"- **Citation accuracy:** {agg['citation_accuracy']}",
        f"- **Average tool calls per question:** {agg['avg_tool_calls']}",
        f"- **Average time per question:** {agg['avg_seconds']}s",
        "",
        "## Accuracy by category",
        "",
        "| Category | N | Tool selection | Citations |",
        "|---|---|---|---|",
    ]
    for cat, d in agg["by_category"].items():
        lines.append(
            f"| `{cat}` | {d['n']} | {d['tool_ok']}/{d['n']} | {d['cite_ok']}/{d['n']} |"
        )
    lines += [
        "",
        "## Per-question results",
        "",
        "| ID | Category | Tool ✓ | Cite ✓ | Calls | Time |",
        "|---|---|---|---|---|---|",
    ]
    for s in scores:
        tool = "✅" if s["tool_selection_correct"] else "❌"
        cite = "✅" if s["citation_correct"] else "❌"
        lines.append(
            f"| `{s['id']}` | {s['category']} | {tool} | {cite} "
            f"| {s['n_tool_calls']} | {s['elapsed_seconds']}s |"
        )

    fails = [s for s in scores if not s["tool_selection_correct"] or not s["citation_correct"]]
    if fails:
        lines += ["", "## Failures worth investigating", ""]
        for s in fails:
            lines.append(f"- **`{s['id']}`**")
            if not s["tool_selection_correct"]:
                lines.append(f"  - Wrong tools called")
            if not s["citation_correct"]:
                lines.append(f"  - Missing citations: {s['missing_citations']}")

    return "\n".join(lines) + "\n"


def main() -> None:
    with open(RESULTS_PATH) as f:
        data = json.load(f)

    scores = [score_one(r) for r in data["results"]]
    agg = aggregate(scores)
    report = render_report(agg, scores)

    with open(REPORT_PATH, "w") as f:
        f.write(report)

    print(report)
    print(f"\n✓ Report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()