import os
from dotenv import load_dotenv
from groq import Groq
from tools.web_search import search_web

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def research_question(question: str) -> str:
    """Searches the web for a question and returns a summarized answer."""
    sources_text = search_web(question)

    prompt = f"""Based on these search results, write a short summary
answering the question: '{question}'

Search results:
{sources_text}

Keep the summary to 3-4 sentences and mention key sources."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
