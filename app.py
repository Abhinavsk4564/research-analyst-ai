import streamlit as st
from tools.pdf_export import create_pdf
from agents.router import route_topic
from agents.planner import create_research_plan
from agents.researcher import research_question
from agents.synthesizer import synthesize_report

st.set_page_config(page_title="Research Analyst AI", page_icon="🔎", layout="wide")

st.title("🔎 Research Analyst AI")
st.caption("A multi-agent system: Router → Planner → Researcher → Synthesizer")

# --- Sidebar: live agent status ---
st.sidebar.header("🤖 Agent Pipeline")
status_router = st.sidebar.empty()
status_planner = st.sidebar.empty()
status_researcher = st.sidebar.empty()
status_synth = st.sidebar.empty()

def reset_sidebar():
    status_router.write("⬜ Router")
    status_planner.write("⬜ Planner")
    status_researcher.write("⬜ Researcher")
    status_synth.write("⬜ Synthesizer")

reset_sidebar()

# --- Persistent state ---
if "result" not in st.session_state:
    st.session_state.result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

topic = st.text_input("Enter a research topic:", placeholder="e.g. Python vs Javascript for beginners")

if st.button("Run Research", type="primary") and topic:

    st.session_state.chat_history = []
    reset_sidebar()

    status_router.write("⏳ Router")
    routing_decision = route_topic(topic)
    status_router.write("✅ Router")

    status_planner.write("⏳ Planner")
    sub_questions = create_research_plan(topic)
    status_planner.write("✅ Planner")

    status_researcher.write("⏳ Researcher")
    findings = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, question in enumerate(sub_questions, 1):
        status_text.text(f"Researching ({i}/{len(sub_questions)}): {question}")
        result = research_question(question)
        findings.append(result)
        progress_bar.progress(i / len(sub_questions))

    status_researcher.write("✅ Researcher")
    status_text.text("Research complete!")

    status_synth.write("⏳ Synthesizer")
    report = synthesize_report(topic, findings, style=routing_decision["style"])
    status_synth.write("✅ Synthesizer")

    full_report = f"# Research Report: {topic}\n\n**Report style:** {routing_decision['style']}\n\n{report}"
    with open("output/report.md", "w", encoding="utf-8") as f:
        f.write(full_report)

    # Save everything needed for display into session_state
    st.session_state.result = {
        "topic": topic,
        "routing_decision": routing_decision,
        "sub_questions": sub_questions,
        "findings": findings,
        "report": report,
        "full_report": full_report,
    }

# --- Display persisted results (survives reruns from chat input) ---
if st.session_state.result:
    r = st.session_state.result

    st.success(f"**Detected style:** {r['routing_decision']['style']} — {r['routing_decision']['reason']}")

    with st.expander("📋 Research Plan", expanded=False):
        for i, q in enumerate(r["sub_questions"], 1):
            st.write(f"{i}. {q}")

    AGREEMENT_ICONS = {"high": "🟢", "medium": "🟡", "low": "🔴"}

    with st.expander("🔍 Detailed Findings & Sources"):
        for f in r["findings"]:
            st.markdown(f"**{f['question']}**")
            icon = AGREEMENT_ICONS.get(f.get("agreement", ""), "⚪")
            st.caption(f"{icon} Source agreement: {f.get('agreement', 'unknown')} — {f.get('agreement_reason', '')}")
            st.write(f['summary'])
            if f.get("sources"):
                st.caption("Sources:")
                for s in f["sources"]:
                    st.markdown(f"- [{s['title']}]({s['url']})")
            st.divider()

    st.markdown("---")
    st.header("📄 Final Report")
    st.markdown(r["report"])

    st.download_button(
        "Download Report (Markdown)",
        data=r["full_report"],
        file_name="research_report.md",
        mime="text/markdown"
    )

    pdf_bytes = create_pdf(r["topic"], r["routing_decision"]["style"], r["report"])

    st.download_button(
        "Download Report (PDF)",
        data=pdf_bytes,
        file_name="research_report.pdf",
        mime="application/pdf"
    )

    # --- Follow-up Chat ---
    st.markdown("---")
    st.subheader("💬 Ask a follow-up question")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    follow_up = st.chat_input("Ask something about this topic...")

    if follow_up:
        st.session_state.chat_history.append({"role": "user", "content": follow_up})
        with st.chat_message("user"):
            st.write(follow_up)

        with st.chat_message("assistant"):
            with st.spinner("Researching your question..."):
                answer = research_question(follow_up)
            st.write(answer["summary"])
            if answer.get("sources"):
                st.caption("Sources:")
                for s in answer["sources"]:
                    st.markdown(f"- [{s['title']}]({s['url']})")

        st.session_state.chat_history.append({"role": "assistant", "content": answer["summary"]})
        