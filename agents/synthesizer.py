import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

STYLE_INSTRUCTIONS = {
    "factual": "Present the facts clearly and objectively, focusing on current data and statistics.",
    "comparison": "Structure sections to highlight comparisons — use pros/cons or side-by-side framing where relevant.",
    "trend": "Emphasize how things are changing over time and what the outlook or predictions are."
}

def synthesize_report(topic: str, findings: list[dict], style: str = "factual") -> str:
    """Combines all sub-question findings into one polished report, styled per the router's decision."""
    findings_text = ""
    for f in findings:
        findings_text += f"Sub-question: {f['question']}\nFindings: {f['summary']}\n\n"

    style_instruction = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["factual"])

    prompt = f"""You are a research analyst. Write a polished, well-structured
report on the topic below, using the research findings provided.

Topic: {topic}
Report style: {style}
{style_instruction}

Research findings:
{findings_text}

Structure the report as:
1. Executive Summary (2-3 sentences)
2. A section for each sub-topic covered above (use the sub-questions as section headers)
3. A brief conclusion

Write in clear, professional language."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Could not generate the final report due to an API error: {str(e)[:200]}"
    

