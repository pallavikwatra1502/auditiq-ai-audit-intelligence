# AuditIQ Enterprise — AI-Powered Audit Intelligence Platform

AuditIQ Enterprise is a working Streamlit application that transforms cloud security, governance, compliance and data quality findings into risk scores, executive dashboards, remediation priorities and audit-ready reports.

## Live App

Deploy on Streamlit Community Cloud using:

```text
app/main.py
```

## What this project demonstrates

- Data ingestion from audit/security CSV files
- Data quality validation and audit-readiness checks
- Risk scoring engine for control findings
- Executive dashboard with risk analytics
- Architecture view for solution design
- Report writer for audit outputs
- Free data-aware Ask AuditIQ assistant
- Findings explorer with filters

## Architecture

```text
Data Sources
  ↓
Ingestion Layer
  ↓
Validation Layer
  ↓
Risk Intelligence Engine
  ↓
Experience Layer
  ↓
Audit Output
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app/main.py
```

## Repository structure

```text
app/
  main.py
  risk_engine.py
  data_quality.py
  report_writer.py
  audit_assistant.py

data/
  sample_audit_findings.csv

notebooks/
  audit_intelligence_analysis.ipynb

reports/
  sample_executive_report.md

requirements.txt
README.md
```

## Portfolio description

**AuditIQ Enterprise** is a data-driven audit intelligence platform that converts cloud security, governance and data quality findings into actionable risk insights, executive reporting, remediation intelligence and audit-ready evidence views.

## Future enhancements

- BigQuery connector
- PDF report export
- Gemini/OpenAI powered assistant
- Authentication
- Automated evidence ingestion
