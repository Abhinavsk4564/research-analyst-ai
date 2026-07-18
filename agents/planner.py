import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def create_research_plan(topic: str) -> list[str]:
    """Turns a topic into a list of sub-questions."""
    prompt = f"""You are a research planner. Break the topic below into 4 clear,
specific sub-questions that together would cover the topic well.

Topic: {topic}

Respond ONLY with a JSON array of strings, like:
["question 1", "question 2", "question 3", "question 4"]
No other text."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        raw_text = response.choices[0].message.content.strip()
        return json.loads(raw_text)
    except Exception:
        return [f"What is important to know about {topic}?"]
    
    