import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from tools.web_search import search_web

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def _extract_json(text: str) -> dict:
    """Tries to safely parse JSON, cleaning up common LLM formatting issues."""
    text = text.strip()
    # Remove markdown code fences if present
    text = re.sub(r"^```(json)?", "", text)
    text = re.sub(r"```$", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: treat the whole thing as a plain summary
        return {
            "summary": text,
            "agreement": "unknown",
            "agreement_reason": "Could not parse structured agreement data."
        }

def research_question(question: str) -> dict:
    """Searches the web, summarizes findings, and rates source agreement."""
    search_data = search_web(question)

    prompt = f"""Based on these search results, answer the question: '{question}'

Search results:
{search_data['text']}

Respond ONLY with valid JSON in this exact format, no other text, no markdown code fences:
{{"summary": "4-5 sentence summary mentioning key sources", "agreement": "high", "agreement_reason": "one short sentence"}}

Important: escape any quotes inside the summary text properly so the JSON stays valid.
For "agreement", use "high" if sources consistently agree, "medium" if mostly aligned with minor differences,
or "low" if sources conflict or contradict each other."""

    try:
        response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
        )
        raw_text = response.choices[0].message.content
        parsed = _extract_json(raw_text)
    except Exception as e:
        return {
        "question": question,
        "summary": f"⚠️ Could not complete this research: {str(e)[:150]}",
        "agreement": "unknown",
        "agreement_reason": "",
        "sources": search_data["sources"]
    }

    return {
        "question": question,
        "summary": parsed.get("summary", "Summary unavailable."),
        "agreement": parsed.get("agreement", "unknown"),
        "agreement_reason": parsed.get("agreement_reason", ""),
        "sources": search_data["sources"]
    }
