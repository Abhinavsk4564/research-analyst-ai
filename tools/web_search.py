import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str, max_results: int = 5) -> dict:
    """Searches the web. Returns both combined text and structured source list."""
    results = tavily_client.search(query, max_results=max_results)

    sources_text = ""
    sources_list = []
    for result in results["results"]:
        sources_text += f"Source: {result['url']}\n{result['content']}\n\n"
        sources_list.append({"title": result.get("title", result["url"]), "url": result["url"]})

    return {"text": sources_text, "sources": sources_list}
