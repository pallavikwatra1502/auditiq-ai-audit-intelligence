# AuditIQ — AI-Powered Audit Intelligence Platform

AuditIQ is a working data and AI portfolio project that converts audit/security control findings into risk scores, dashboards, data quality insights, management summaries and generated audit reports.

The project is designed to run for free using GitHub + Streamlit Community Cloud. It does not require BigQuery, OpenAI, Gemini or paid hosting.

## What the project demonstrates

- Data engineering thinking: ingestion, validation, transformation and scoring
- Security governance: audit findings, control domains, regulatory impact and evidence status
- Analytics engineering: dashboards, risk scoring, control reporting and remediation insights
- AI product thinking: an audit report writer and a data-aware assistant built without paid APIs

## Live App Features

- Upload CSV or use included sample audit findings data
- Filter by severity, status, control domain and regulatory impact
- Calculate audit readiness score
- Score each finding using a risk engine
- Detect data quality issues such as missing evidence, overdue remediation and duplicate IDs
- Generate executive audit reports
- Ask questions about the audit dataset through a free data-aware assistant

## Repository Structure

```text
app/
  main.py               Streamlit application
  risk_engine.py        Risk scoring logic
  data_quality.py       Data validation checks
  report_writer.py      Audit report generation
  audit_assistant.py    Free data-aware Q&A assistant

data/
  sample_audit_findings.csv

reports/
  sample_executive_audit_report.md

notebooks/
  audit_intelligence_analysis.ipynb
```

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app/main.py
```

## Free Deployment

Deploy this repository on Streamlit Community Cloud:

1. Push this folder to a new GitHub repository.
2. Go to Streamlit Community Cloud.
3. Sign in with GitHub.
4. Click **New app**.
5. Select the repository.
6. Set main file path to:

```text
app/main.py
```

7. Click **Deploy**.

## Sample Questions for Ask AuditIQ

- Which applications have the highest audit risk?
- What are the overdue findings?
- Summarise evidence gaps.
- What is the GDPR impact?
- Which control domains have the highest risk?
- Generate a management summary.

## Future Enhancements

- BigQuery connector
- Gemini/OpenAI powered RAG assistant
- PDF report export
- User authentication
- Cloud Run deployment
- Automated data ingestion pipeline
