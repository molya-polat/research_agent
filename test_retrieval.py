from src.retriever import search_knowledge_base

queries = [
    "What is reward hacking?",
    "How does constitutional AI work?",
    "Can models be trained to deceive humans?",
    "What are the risks from mesa-optimization?",
]

for q in queries:
    print(f"\n{'=' * 60}")
    print(f"Query: {q}")
    print('=' * 60)
    results = search_knowledge_base(q, top_k=3)
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r.title} ({r.first_author}, {r.year}) "
              f"— chunk {r.chunk_index}, distance {r.distance:.3f}")
        print(f"    {r.text[:250]}...")