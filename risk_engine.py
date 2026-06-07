from datetime import date
import pandas as pd

SEVERITY_SCORE = {'Critical': 40, 'High': 30, 'Medium': 18, 'Low': 8}
EVIDENCE_SCORE = {'Missing': 25, 'Expired': 18, 'Partial': 10, 'Complete': 0}
BUSINESS_SCORE = {'Critical': 20, 'High': 14, 'Medium': 8, 'Low': 3}
REGULATORY_SCORE = {'GDPR': 12, 'FCA': 12, 'SOX': 10, 'PCI-DSS': 10, 'ISO 27001': 7, 'Internal Policy': 4}
STATUS_SCORE = {'Open': 12, 'In Progress': 6, 'Risk Accepted': 4, 'Remediated': -10}

def enrich_risk(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data['due_date'] = pd.to_datetime(data['due_date']).dt.date
    today = date.today()
    data['days_overdue'] = data['due_date'].apply(lambda d: max((today - d).days, 0))
    data['is_overdue'] = data['days_overdue'] > 0
    data['risk_score'] = (
        data['severity'].map(SEVERITY_SCORE).fillna(0) +
        data['evidence_status'].map(EVIDENCE_SCORE).fillna(0) +
        data['business_criticality'].map(BUSINESS_SCORE).fillna(0) +
        data['regulatory_impact'].map(REGULATORY_SCORE).fillna(0) +
        data['status'].map(STATUS_SCORE).fillna(0) +
        data['days_overdue'].clip(0, 60) * 0.35
    ).round(1)
    data['risk_tier'] = pd.cut(
        data['risk_score'],
        bins=[-999, 30, 55, 80, 999],
        labels=['Low', 'Medium', 'High', 'Critical']
    ).astype(str)
    return data

def audit_readiness_score(df: pd.DataFrame) -> int:
    if df.empty:
        return 100
    open_risk = df[df['status'].isin(['Open', 'In Progress'])]['risk_score'].sum()
    max_possible = max(len(df) * 100, 1)
    score = 100 - ((open_risk / max_possible) * 100)
    return int(max(0, min(100, round(score))))
