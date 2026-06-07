import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from risk_engine import enrich_risk, audit_readiness_score, priority_queue
from data_quality import validate_dataset, quality_summary, REQUIRED_COLUMNS
from report_writer import generate_executive_report
from audit_assistant import answer_question

st.set_page_config(
    page_title="AuditIQ Enterprise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background: #071018; }
    .block-container { padding-top: 1.2rem; }
    .hero {
        padding: 32px 36px;
        border: 1px solid rgba(120,255,220,.22);
        background: radial-gradient(circle at top right, rgba(85,245,208,.20), transparent 34%),
                    linear-gradient(135deg, rgba(17,27,39,.98), rgba(7,16,24,.98));
        border-radius: 28px;
        margin-bottom: 22px;
    }
    .eyebrow {
        color: #55f5d0;
        letter-spacing: 6px;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
    }
    .hero h1 {
        font-size: 56px;
        line-height: 1.02;
        margin: 8px 0 10px 0;
        color: #eef6ff;
    }
    .hero p {
        color: #aab8c8;
        font-size: 18px;
        max-width: 980px;
    }
    .creator {
        margin-top: 18px;
        color: #dce8f5;
        font-weight: 700;
    }
    .creator span {
        color: #55f5d0;
    }
    .metric-card {
        padding: 18px 20px;
        border-radius: 20px;
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.10);
    }
    .metric-card h3 { color: #55f5d0; margin: 0; font-size: 30px; }
    .metric-card span { color: #aab8c8; font-size: 14px; }
    div[data-testid="stMetricValue"] { color: #eef6ff; }
    div[data-testid="stMetricLabel"] { color: #aab8c8; }
    .section-title {
        color: #eef6ff;
        font-size: 28px;
        margin-top: 12px;
        margin-bottom: 8px;
        font-weight: 800;
    }
    .soft-card {
        padding: 20px;
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 22px;
        min-height: 130px;
    }
    .soft-card h3 { color: #eef6ff; margin-top: 0; }
    .soft-card p { color: #aab8c8; }
    .arch-box {
        padding: 18px 20px;
        border-radius: 18px;
        border: 1px solid rgba(85,245,208,.18);
        background: rgba(255,255,255,.045);
        margin-bottom: 12px;
    }
    .arch-arrow { text-align: center; color: #55f5d0; font-size: 26px; font-weight: 900; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,.06);
        border-radius: 999px;
        padding: 10px 18px;
        color: #dbe6f4;
    }
</style>
""", unsafe_allow_html=True)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_audit_findings.csv"

@st.cache_data
def load_default_data():
    return pd.read_csv(DATA_PATH)

def load_data():
    with st.sidebar:
        st.markdown("## AuditIQ Controls")
        uploaded = st.file_uploader("Upload audit findings CSV", type=["csv"])
        st.caption("Use the sample dataset or upload your own file with the required columns.")
    if uploaded:
        return pd.read_csv(uploaded)
    return load_default_data()

raw_df = load_data()
validation = validate_dataset(raw_df)

if validation.get("missing_columns"):
    st.error("Uploaded dataset is missing required columns.")
    st.write(validation["missing_columns"])
    st.stop()

df = enrich_risk(raw_df)

with st.sidebar:
    st.markdown("### Filters")
    domains = st.multiselect("Control domain", sorted(df["control_domain"].unique()))
    severities = st.multiselect("Severity", ["Critical", "High", "Medium", "Low"])
    statuses = st.multiselect("Status", sorted(df["status"].unique()))
    regs = st.multiselect("Regulatory mapping", sorted(df["regulatory_mapping"].unique()))
    if domains:
        df = df[df["control_domain"].isin(domains)]
    if severities:
        df = df[df["severity"].isin(severities)]
    if statuses:
        df = df[df["status"].isin(statuses)]
    if regs:
        df = df[df["regulatory_mapping"].isin(regs)]

st.markdown("""
<div class="hero">
    <div class="eyebrow">Cloud Security • Data Governance • Audit Automation</div>
    <h1>AuditIQ Enterprise</h1>
    <p>
    Transforms cloud security, governance and data quality findings into actionable risk insights,
    executive reporting, remediation intelligence and audit-ready evidence views.
    </p>
    <div class="creator">Created by <span>Pallavi Kwatra</span> · Senior Data Engineer | Cloud Security & Governance</div>
</div>
""", unsafe_allow_html=True)

total = len(df)
open_count = len(df[df["status"].ne("Closed")])
critical_high = len(df[(df["severity"].isin(["Critical","High"])) & (df["status"].ne("Closed"))])
overdue = len(df[df["is_overdue"]])
missing_ev = len(df[df["evidence_status"].isin(["Missing", "Expired"])])
readiness = audit_readiness_score(df)
coverage = int(round(100 - ((missing_ev / total) * 100))) if total else 0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Audit Readiness", f"{readiness}/100")
m2.metric("Findings Analysed", total)
m3.metric("Open Items", open_count)
m4.metric("Critical/High Open", critical_high)
m5.metric("Evidence Coverage", f"{coverage}%")

st.markdown("""
<div style="height:8px"></div>
""", unsafe_allow_html=True)

tabs = st.tabs(["Executive Dashboard", "Data Quality", "Architecture", "Report Writer", "Ask AuditIQ", "Findings Explorer"])

with tabs[0]:
    st.markdown('<div class="section-title">Executive Risk Overview</div>', unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    s1.markdown('<div class="soft-card"><h3>Risk Scoring Engine</h3><p>Scores each finding using severity, evidence status, overdue age, business criticality, regulatory impact and repeat-finding signals.</p></div>', unsafe_allow_html=True)
    s2.markdown('<div class="soft-card"><h3>Governance Intelligence</h3><p>Highlights ownership gaps, evidence quality, control domains and regulatory exposure across cloud and data platforms.</p></div>', unsafe_allow_html=True)
    s3.markdown('<div class="soft-card"><h3>Audit-Ready Output</h3><p>Generates executive summaries, control weakness reports and remediation queues from the filtered audit dataset.</p></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        sev = df.groupby("severity").size().reset_index(name="count")
        fig = px.bar(sev, x="severity", y="count", title="Findings by Severity")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        dom = df.groupby("control_domain")["risk_score"].mean().reset_index().sort_values("risk_score", ascending=False)
        fig = px.bar(dom, x="risk_score", y="control_domain", orientation="h", title="Average Risk Score by Control Domain")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        stat = df.groupby("status").size().reset_index(name="count")
        fig = px.pie(stat, names="status", values="count", title="Remediation Status")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        heat = df.pivot_table(index="control_domain", columns="severity", values="risk_score", aggfunc="mean").fillna(0)
        fig = px.imshow(heat, text_auto=True, title="Risk Heatmap: Domain vs Severity")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Priority Remediation Queue</div>', unsafe_allow_html=True)
    st.dataframe(priority_queue(df, 10), use_container_width=True)

with tabs[1]:
    st.markdown('<div class="section-title">Data Quality & Audit Readiness Checks</div>', unsafe_allow_html=True)
    quality = validate_dataset(df)
    st.info(quality_summary(quality))
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("Duplicate IDs", quality.get("duplicate_finding_ids", 0))
    q2.metric("Missing Owners", quality.get("missing_owner", 0))
    q3.metric("Missing/Expired Evidence", quality.get("missing_evidence", 0))
    q4.metric("Invalid Due Dates", quality.get("invalid_due_dates", 0))
    q5.metric("Evidence Coverage", f"{coverage}%")
    st.markdown("### Required Dataset Columns")
    st.code(", ".join(REQUIRED_COLUMNS), language="text")

with tabs[2]:
    st.markdown('<div class="section-title">Architecture</div>', unsafe_allow_html=True)
    st.caption("This view shows how the working demo is designed as a modular audit intelligence pipeline.")
    arch = [
        ("Data Sources", "Cloud logging exports, IAM reviews, CMDB extracts, control attestations, DLP scans and data quality monitors."),
        ("Ingestion Layer", "CSV upload for the live demo, with a future-ready path for BigQuery or scheduled cloud data ingestion."),
        ("Validation Layer", "Required schema checks, owner validation, evidence completeness checks, date checks and duplicate-finding detection."),
        ("Risk Intelligence Engine", "Weighted scoring using severity, evidence status, overdue remediation, business criticality, regulatory mapping and repeat findings."),
        ("Experience Layer", "Executive dashboard, data quality scorecard, audit report writer, findings explorer and Ask AuditIQ assistant."),
        ("Audit Output", "Management-ready reporting, remediation priority queue and downloadable filtered evidence dataset.")
    ]
    for title, text in arch:
        st.markdown(f'<div class="arch-box"><h3>{title}</h3><p>{text}</p></div>', unsafe_allow_html=True)
        if title != "Audit Output":
            st.markdown('<div class="arch-arrow">↓</div>', unsafe_allow_html=True)
    lineage = df.groupby(["control_domain", "regulatory_mapping"]).size().reset_index(name="records")
    fig = px.sunburst(lineage, path=["control_domain", "regulatory_mapping"], values="records", title="Control Domain → Regulatory Mapping")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    st.markdown('<div class="section-title">AI-Style Audit Report Writer</div>', unsafe_allow_html=True)
    report_type = st.selectbox("Report type", ["Executive Audit Report", "Compliance Status Report", "Control Weakness Report", "Remediation Plan", "Board Risk Summary"])
    report = generate_executive_report(df, report_type)
    st.markdown(report)
    st.download_button("Download Markdown Report", data=report, file_name="auditiq_report.md", mime="text/markdown")
    st.download_button("Download Filtered Dataset", data=df.to_csv(index=False), file_name="filtered_audit_findings.csv", mime="text/csv")

with tabs[4]:
    st.markdown('<div class="section-title">Ask AuditIQ</div>', unsafe_allow_html=True)
    st.caption("Free data-aware assistant. No paid API key is used.")
    examples = [
        "Which applications have the highest risk?",
        "What findings are overdue?",
        "Where is evidence missing?",
        "Give me an executive summary",
        "Show regulatory risk summary",
        "Which owner teams have most open findings?"
    ]
    selected = st.selectbox("Try a question", [""] + examples)
    question = st.text_input("Ask your own audit question", value=selected)
    if st.button("Ask AuditIQ"):
        st.markdown(answer_question(df, question))

with tabs[5]:
    st.markdown('<div class="section-title">Audit Findings Explorer</div>', unsafe_allow_html=True)
    st.dataframe(df.sort_values("risk_score", ascending=False), use_container_width=True)
