from src.web_search import search_web

results = search_web("latest news on AI safety regulation UK 2026")
for i, r in enumerate(results, 1):
    print(f"\n[{i}] {r.title}")
    print(f"    {r.url}")
    print(f"    {r.content[:200]}...")