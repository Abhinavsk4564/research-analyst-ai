import streamlit as st
from agents.router import route_topic
from agents.planner import create_research_plan
from agents.researcher import research_question
from agents.synthesizer import synthesize_report

st.set_page_config(page_title="Research Analyst AI", page_icon="🔎", layout="wide")

st.title("🔎 Research Analyst AI")
st.caption("A multi-agent system: Router → Planner → Researcher → Synthesizer")

topic = st.text_input("Enter a research topic:", placeholder="e.g. Python vs Javascript for beginners")

if st.button("Run Research", type="primary") and topic:

    # --- Router ---
    with st.spinner("Routing topic..."):
        routing_decision = route_topic(topic)

    st.success(f"**Detected style:** {routing_decision['style']} — {routing_decision['reason']}")

    # --- Planner ---
    with st.spinner("Creating research plan..."):
        sub_questions = create_research_plan(topic)

    with st.expander("📋 Research Plan", expanded=True):
        for i, q in enumerate(sub_questions, 1):
            st.write(f"{i}. {q}")

    # --- Researcher (loop) ---
    findings = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, question in enumerate(sub_questions, 1):
        status_text.text(f"Researching ({i}/{len(sub_questions)}): {question}")
        summary = research_question(question)
        findings.append({"question": question, "summary": summary})
        progress_bar.progress(i / len(sub_questions))

    status_text.text("Research complete!")

    with st.expander("🔍 Detailed Findings"):
        for f in findings:
            st.markdown(f"**{f['question']}**")
            st.write(f['summary'])
            st.divider()

    # --- Synthesizer ---
    with st.spinner("Writing final report..."):
        report = synthesize_report(topic, findings, style=routing_decision["style"])

    st.markdown("---")
    st.header("📄 Final Report")
    st.markdown(report)

    # Save + download
    full_report = f"# Research Report: {topic}\n\n**Report style:** {routing_decision['style']}\n\n{report}"
    with open("output/report.md", "w", encoding="utf-8") as f:
        f.write(full_report)

    st.download_button(
        "Download Report (Markdown)",
        data=full_report,
        file_name="research_report.md",
        mime="text/markdown"
    )
    