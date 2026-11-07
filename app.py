import os
from io import BytesIO
from datetime import date
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AI TPM Assistant", page_icon="📊", layout="wide")
st.title("AI TPM Assistant")
st.caption("Turn a two-tab project tracker into concise, evidence-based client status reports.")

uploaded = st.file_uploader("Upload the Task 5 Excel tracker", type=["xlsx"])

def clean(v):
    if pd.isna(v):
        return "Not provided"
    return str(v).strip()

def make_report(project, summary, risks, use_ai=False, api_key=""):
    # Deterministic source facts; AI is an optional writing aid, not the source of truth.
    facts = {
        "project": clean(summary.get("Project")),
        "client": clean(summary.get("Client")),
        "status": clean(summary.get("Status")),
        "next_milestone": clean(summary.get("Next milestone")),
        "milestone_date": clean(summary.get("Milestone date")),
        "main_problem": clean(summary.get("Main problem")),
        "decision": clean(summary.get("TPM decision / next step")),
        "risks": risks.fillna("").to_dict(orient="records")
    }
    lines = [
        f"# Weekly status report – {facts['project']}",
        f"**Client:** {facts['client']}  ",
        f"**Overall status:** {facts['status']}  ",
        f"**Next milestone:** {facts['next_milestone']} ({facts['milestone_date']})",
        "",
        "## Executive summary",
        facts["main_problem"],
        "",
        "## TPM actions / recommendation",
        facts["decision"],
        "",
        "## Open risks and issues"
    ]
    if len(risks):
        for _, r in risks.iterrows():
            lines.append(
                f"- **{clean(r.get('ID'))} – {clean(r.get('Description'))}** "
                f"(Probability: {clean(r.get('Probability'))}; Impact: {clean(r.get('Impact'))}; "
                f"Owner: {clean(r.get('Owner'))}; Due: {clean(r.get('Due date'))}; "
                f"Status: {clean(r.get('Status'))}). Action: {clean(r.get('Mitigation / next action'))}"
            )
    else:
        lines.append("- No risks are listed for this project in the uploaded tracker.")
    report = "\n".join(lines)

    if use_ai and api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                temperature=0.1,
                messages=[
                    {"role":"system","content":(
                        "You are a careful Technical Program Manager. Rewrite the supplied facts "
                        "as a concise executive weekly report. Use only supplied facts. Do not invent "
                        "dates, progress, causes, owners, approvals or metrics. Preserve Red/Amber/Green "
                        "status and explicitly label missing information as not provided. If facts conflict, flag it."
                    )},
                    {"role":"user","content":report}
                ]
            )
            report = completion.choices[0].message.content
        except Exception as e:
            st.warning(f"AI rewrite failed; showing the deterministic report instead. Error: {e}")
    return report

if uploaded:
    try:
        summary = pd.read_excel(uploaded, sheet_name="Summary")
        risks = pd.read_excel(uploaded, sheet_name="Risks and Issues")
        required_summary = {"Project","Client","Status","Next milestone","Milestone date","Main problem","TPM decision / next step"}
        required_risks = {"ID","Project","Description","Probability","Impact","Owner","Mitigation / next action","Due date","Status"}
        if not required_summary.issubset(summary.columns):
            st.error(f"Summary sheet is missing columns: {sorted(required_summary-set(summary.columns))}")
            st.stop()
        if not required_risks.issubset(risks.columns):
            st.error(f"Risks and Issues sheet is missing columns: {sorted(required_risks-set(risks.columns))}")
            st.stop()

        st.success(f"Loaded {len(summary)} projects and {len(risks)} risks/issues.")
        c1,c2,c3 = st.columns(3)
        c1.metric("Projects", len(summary))
        c2.metric("Open / tracked risks", len(risks))
        c3.metric("Red projects", int((summary["Status"].astype(str).str.lower()=="red").sum()))
        st.subheader("Tracker preview")
        st.dataframe(summary, width="stretch")
        st.dataframe(risks, width="stretch")

        st.subheader("Report generation")
        use_ai = st.checkbox("Use Groq to polish the report (optional; deterministic report works without an API key)", value=False)
        api_key = ""
        if use_ai:
            api_key = st.text_input("Groq API key", type="password", help="Used only for this session; do not commit it.")
        for _, row in summary.iterrows():
            project = clean(row["Project"])
            project_risks = risks[risks["Project"].astype(str).str.casefold() == project.casefold()]
            with st.expander(f"{project} – {clean(row['Status'])}", expanded=True):
                report = make_report(project, row, project_risks, use_ai, api_key)
                st.markdown(report)
                st.download_button(
                    f"Download {project} report",
                    data=report.encode("utf-8"),
                    file_name=f"{project.lower().replace(' ','_')}_weekly_status.md",
                    mime="text/markdown",
                    key=f"download_{project}"
                )
        combined = "\n\n---\n\n".join(
            make_report(clean(row["Project"]), row,
                        risks[risks["Project"].astype(str).str.casefold()==clean(row["Project"]).casefold()],
                        use_ai, api_key)
            for _, row in summary.iterrows()
        )
        st.download_button("Download combined weekly report", combined.encode("utf-8"),
                           "weekly_status_all_projects.md", "text/markdown")
    except Exception as e:
        st.error(f"Could not read this workbook: {e}")
else:
    st.info("Upload the supplied T5_Project_Tracker.xlsx to generate one report per client.")
    st.markdown("**Expected worksheets:** `Summary` and `Risks and Issues`.")
