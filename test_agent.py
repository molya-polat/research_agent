from src.agent import run_agent

questions = [
    # Should trigger KB only — foundational, entirely covered by the corpus
    "What is mesa-optimization and why is it a safety concern?",

    # Should trigger web only — recent event, outside corpus
    "Who won the 2024 US presidential election?",

    # Should trigger BOTH — foundational concept + recent development
    "What is Constitutional AI, and what recent research builds on it?",
]

for q in questions:
    print("\n" + "#" * 70)
    print(f"# QUESTION: {q}")
    print("#" * 70)
    answer = run_agent(q, verbose=True)
    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(answer)