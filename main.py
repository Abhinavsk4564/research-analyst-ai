from agents.router import route_topic
from agents.planner import create_research_plan
from agents.researcher import research_question
from agents.synthesizer import synthesize_report

def run_research(topic: str) -> str:
    print(f"\nRouting topic: {topic}")
    routing_decision = route_topic(topic)
    print(f"Detected style: {routing_decision['style']} — {routing_decision['reason']}")

    print(f"\nPlanning research for: {topic}")
    sub_questions = create_research_plan(topic)

    print("\nResearch plan:")
    for i, q in enumerate(sub_questions, 1):
        print(f"{i}. {q}")

    findings = []
    for i, question in enumerate(sub_questions, 1):
        print(f"\nResearching ({i}/{len(sub_questions)}): {question}")
        summary = research_question(question)
        findings.append({"question": question, "summary": summary})
        print("Done.")

    print("\nSynthesizing final report...")
    report = synthesize_report(topic, findings, style=routing_decision["style"])

    with open("output/report.md", "w", encoding="utf-8") as f:
        f.write(f"# Research Report: {topic}\n\n**Report style:** {routing_decision['style']}\n\n{report}")

    return report

if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    report = run_research(topic)
    print("\n\n=== FINAL REPORT ===\n")
    print(report)
    print("\nReport saved to output/report.md")
    