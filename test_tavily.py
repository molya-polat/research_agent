from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

client = TavilyClient()  # reads TAVILY_API_KEY from env
result = client.search(
    query="What is retrieval augmented generation?",
    max_results=3,
)

for r in result["results"]:
    print(f"\n{r['title']}")
    print(f"  {r['url']}")
    print(f"  {r['content'][:200]}...")