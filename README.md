# AI TPM Assistant

A small Streamlit tool that reads a project tracker workbook and generates separate weekly status reports for each project/client.

## Features
- Reads `Summary` and `Risks and Issues` worksheets from an `.xlsx` workbook.
- Shows project and risk previews.
- Generates a separate Markdown report for each project and a combined report.
- Works without an AI key using deterministic source-based reporting.
- Optional Groq rewrite to improve executive readability. The prompt explicitly prohibits inventing facts.
- Downloads reports as Markdown.

## Run locally
1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Optional: copy `.env.example` to `.env` and set `GROQ_API_KEY` and `GROQ_MODEL`. Never commit `.env`.
5. Run: `streamlit run app.py`
6. Upload `T5_Project_Tracker.xlsx` (the companion tracker supplied with this assignment).

## Input workbook schema
- Worksheet `Summary`: Project, Client, Status, Next milestone, Milestone date, Main problem, TPM decision / next step.
- Worksheet `Risks and Issues`: ID, Project, Description, Probability, Impact, Owner, Mitigation / next action, Due date, Status.

## AI prompts used
**Build prompt:** "Build a Python Streamlit application that accepts an Excel project tracker with Summary and Risks and Issues worksheets. Read both sheets using Pandas and generate individual weekly status reports for each project."

**Report prompt (system):** "You are a careful Technical Program Manager. Rewrite the supplied facts as a concise executive weekly report. Use only supplied facts. Do not invent dates, progress, causes, owners, approvals or metrics. Preserve Red/Amber/Green status and explicitly label missing information as not provided. If facts conflict, flag it."

**Validation prompt:** "Review the Excel parsing logic. Ensure the application correctly reads both worksheets, handles missing values and does not confuse project risks with completed tasks."

## AI error and correction – complete honestly after your own test
Record one actual error observed while using your AI coding assistant. Example format: "The assistant initially assumed the `Risks` worksheet name, while the workbook uses `Risks and Issues`. I corrected the sheet name in the reader, added required-column validation, and reran the app with the supplied tracker." Replace this example with the error you actually encounter; do not claim an error you did not observe.

## Design and safety notes
- The workbook is treated as the source of truth; the application does not infer completed work from risks.
- AI rewriting is optional. If Groq is unavailable or errors, deterministic reporting remains available.
- Review AI output before sending it to a client. Do not upload confidential customer records or personal data to an external model.
- No API key is required for the core tool.

## AI tool disclosure
ChatGPT was used to help structure the assignment deliverables and draft the initial application. If you use Claude Code, Cursor or another assistant to modify the code, disclose that tool and the actual prompts in your final submission.
