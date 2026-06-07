import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from risk_engine import enrich_risk, audit_readiness_score
from data_quality import quality_checks
from report_writer import generate_report
from audit_assistant import answer_question

st.set_page_config(page_title='AuditIQ | AI Audit Intelligence', page_icon='🛡️', layout='wide')

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / 'data' / 'sample_audit_findings.csv'

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        raw = pd.read_csv(uploaded_file)
    else:
        raw = pd.read_csv(DATA_PATH)
    return enrich_risk(raw)

st.markdown('''
<style>
.main {background-color: #0b1020;}
.block-container {padding-top: 2rem;}
.metric-card {background: linear-gradient(135deg,#111936,#17213f); padding: 18px; border-radius: 18px; border: 1px solid rgba(255,255,255,.08);} 
.hero {padding: 22px 0 10px 0;}
.hero h1 {font-size: 3rem; margin-bottom: 0;}
.hero p {font-size: 1.05rem; color: #cbd5e1;}
.small-muted {color: #94a3b8; font-size:.9rem;}
</style>
''', unsafe_allow_html=True)

with st.sidebar:
    st.title('AuditIQ')
    st.caption('AI-powered audit intelligence from security and control data')
    uploaded = st.file_uploader('Upload audit findings CSV', type=['csv'])
    st.divider()
    st.markdown('**Demo dataset included**')
    st.caption('Use the sample data or upload your own file with similar columns.')

df = load_data(uploaded)

st.markdown("""
<div class='hero'>
<h1>AuditIQ — AI Audit Intelligence Platform</h1>
<p>Convert audit findings into risk scores, executive dashboards, control insights and generated audit reports.</p>
</div>
""", unsafe_allow_html=True)

# Filters
c1, c2, c3, c4 = st.columns(4)
with c1:
    sev = st.multiselect('Severity', sorted(df['severity'].unique()), default=sorted(df['severity'].unique()))
with c2:
    status = st.multiselect('Status', sorted(df['status'].unique()), default=sorted(df['status'].unique()))
with c3:
    domain = st.multiselect('Control Domain', sorted(df['control_domain'].unique()), default=sorted(df['control_domain'].unique()))
with c4:
    reg = st.multiselect('Regulatory Impact', sorted(df['regulatory_impact'].unique()), default=sorted(df['regulatory_impact'].unique()))

filtered = df[df['severity'].isin(sev) & df['status'].isin(status) & df['control_domain'].isin(domain) & df['regulatory_impact'].isin(reg)]
readiness = audit_readiness_score(filtered)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric('Audit Readiness', f'{readiness}%')
m2.metric('Total Findings', len(filtered))
m3.metric('Critical Tier', int((filtered['risk_tier'] == 'Critical').sum()))
m4.metric('Overdue', int(filtered['is_overdue'].sum()))
m5.metric('Missing Evidence', int((filtered['evidence_status'] == 'Missing').sum()))

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(['Risk Dashboard', 'Data Quality', 'Report Writer', 'Ask AuditIQ'])

with tab1:
    left, right = st.columns(2)
    with left:
        sev_chart = filtered.groupby('severity', as_index=False).size()
        st.plotly_chart(px.bar(sev_chart, x='severity', y='size', title='Findings by Severity'), use_container_width=True)
        dom_chart = filtered.groupby('control_domain', as_index=False)['risk_score'].sum().sort_values('risk_score', ascending=False)
        st.plotly_chart(px.bar(dom_chart, x='risk_score', y='control_domain', orientation='h', title='Cumulative Risk by Control Domain'), use_container_width=True)
    with right:
        status_chart = filtered.groupby('status', as_index=False).size()
        st.plotly_chart(px.pie(status_chart, names='status', values='size', title='Finding Status Distribution'), use_container_width=True)
        app_chart = filtered.groupby('application', as_index=False)['risk_score'].sum().sort_values('risk_score', ascending=False).head(10)
        st.plotly_chart(px.bar(app_chart, x='application', y='risk_score', title='Top Risk Applications'), use_container_width=True)
    st.subheader('Audit Findings')
    st.dataframe(filtered.sort_values('risk_score', ascending=False), use_container_width=True, hide_index=True)

with tab2:
    st.subheader('Automated Data Quality Checks')
    qdf = quality_checks(filtered)
    st.dataframe(qdf, use_container_width=True, hide_index=True)
    st.caption('These checks simulate controls used before audit reporting: ownership, evidence completeness, duplicates and overdue remediation.')

with tab3:
    st.subheader('AI-Style Audit Report Writer')
    report_type = st.selectbox('Choose report type', ['Executive Audit Summary', 'Internal Audit Report', 'Compliance Status Report', 'Risk Remediation Report'])
    report = generate_report(filtered, readiness, report_type)
    st.download_button('Download Markdown Report', data=report, file_name='auditiq_report.md', mime='text/markdown')
    st.markdown(report)

with tab4:
    st.subheader('Ask AuditIQ')
    st.caption('Free data-aware assistant. No paid API required. Answers are generated from the filtered dataset.')
    question = st.text_input('Ask a question', placeholder='Which applications have the highest audit risk?')
    if st.button('Ask') or question:
        st.markdown(answer_question(question, filtered).replace('\n', '  \n'))
    st.markdown('**Try:** highest risk applications, overdue findings, evidence gaps, GDPR impact, top control domains, management summary')
