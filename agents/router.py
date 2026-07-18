import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def route_topic(topic: str) -> dict:
    """Analyzes a topic and decides which report style fits best."""
    prompt = f"""You are a routing agent for a research system. Analyze the topic below
and decide which ONE report style best fits it:

- "factual" - straightforward topics needing facts, current state, statistics
- "comparison" - topics comparing two or more things, options, or approaches
- "trend" - topics about change over time, predictions, or future outlook

Topic: {topic}

Respond ONLY with JSON in this exact format, no other text:
{{"style": "factual", "reason": "one short sentence explaining why"}}"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}]
        )
        raw_text = response.choices[0].message.content.strip()
        return json.loads(raw_text)
    except Exception:
        return {"style": "factual", "reason": "Defaulted due to an API error."}
    
    