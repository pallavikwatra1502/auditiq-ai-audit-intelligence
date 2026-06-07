
import pandas as pd
import numpy as np
from datetime import date

SEVERITY_WEIGHT = {"Critical": 40, "High": 28, "Medium": 16, "Low": 8}
EVIDENCE_WEIGHT = {"Missing": 20, "Expired": 14, "Partial": 10, "Available": 0}
STATUS_WEIGHT = {"Open": 14, "In Progress": 8, "Risk Accepted": 12, "Closed": -8}
CRITICALITY_WEIGHT = {"Tier 0": 16, "Tier 1": 11, "Tier 2": 6, "Tier 3": 2}
REGULATORY_WEIGHT = {"GDPR": 10, "SOX": 9, "PCI-DSS": 9, "FCA": 8, "ISO 27001": 7, "Internal Policy": 3}

def enrich_risk(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
    df["identified_date"] = pd.to_datetime(df["identified_date"], errors="coerce")
    today = pd.Timestamp(date.today())
    df["days_overdue"] = (today - df["due_date"]).dt.days
    df["is_overdue"] = (df["days_overdue"] > 0) & (~df["status"].eq("Closed"))

    score = (
        df["severity"].map(SEVERITY_WEIGHT).fillna(0)
        + df["evidence_status"].map(EVIDENCE_WEIGHT).fillna(0)
        + df["status"].map(STATUS_WEIGHT).fillna(0)
        + df["business_criticality"].map(CRITICALITY_WEIGHT).fillna(0)
        + df["regulatory_mapping"].map(REGULATORY_WEIGHT).fillna(0)
        + np.where(df["repeat_finding"].eq("Yes"), 10, 0)
        + np.where(df["is_overdue"], 12, 0)
    )
    df["risk_score"] = score.clip(lower=0, upper=100).round(0).astype(int)

    def band(x):
        if x >= 80:
            return "Very High"
        if x >= 60:
            return "High"
        if x >= 40:
            return "Medium"
        return "Low"

    df["risk_band"] = df["risk_score"].apply(band)
    return df

def audit_readiness_score(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    open_weight = len(df[df["status"].ne("Closed")]) / max(len(df), 1)
    missing_evidence = len(df[df["evidence_status"].isin(["Missing", "Expired"])]) / max(len(df), 1)
    critical_open = len(df[(df["severity"].isin(["Critical", "High"])) & (df["status"].ne("Closed"))]) / max(len(df), 1)
    score = 100 - ((open_weight * 35) + (missing_evidence * 35) + (critical_open * 30))
    return int(max(0, min(100, round(score))))

def priority_queue(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    cols = ["finding_id", "application", "control_domain", "severity", "status", "owner_team", "evidence_status", "due_date", "risk_score", "management_action"]
    return df.sort_values(["risk_score", "days_overdue"], ascending=[False, False])[cols].head(n)
