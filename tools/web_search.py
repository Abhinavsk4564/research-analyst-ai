import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str, max_results: int = 5) -> str:
    """Searches the web and returns combined source text."""
    results = tavily_client.search(query, max_results=max_results)

    sources_text = ""
    for result in results["results"]:
        sources_text += f"Source: {result['url']}\n{result['content']}\n\n"

    return sources_text
