
import pandas as pd

REQUIRED_COLUMNS = [
    "finding_id", "application", "cloud_environment", "control_domain", "control_name",
    "severity", "status", "owner_team", "business_criticality", "regulatory_mapping",
    "evidence_status", "repeat_finding", "identified_date", "due_date", "risk_description",
    "management_action"
]

def validate_dataset(df: pd.DataFrame) -> dict:
    results = {}
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    results["missing_columns"] = missing_cols

    if missing_cols:
        return results

    results["rows"] = len(df)
    results["duplicate_finding_ids"] = int(df["finding_id"].duplicated().sum())
    results["missing_owner"] = int(df["owner_team"].isna().sum() + (df["owner_team"].astype(str).str.strip() == "").sum())
    results["missing_evidence"] = int(df["evidence_status"].isin(["Missing", "Expired"]).sum())
    results["invalid_due_dates"] = int(pd.to_datetime(df["due_date"], errors="coerce").isna().sum())
    results["invalid_identified_dates"] = int(pd.to_datetime(df["identified_date"], errors="coerce").isna().sum())
    results["critical_without_action"] = int(((df["severity"] == "Critical") & (df["management_action"].astype(str).str.len() < 10)).sum())
    return results

def quality_summary(results: dict) -> str:
    if results.get("missing_columns"):
        return f"Dataset is missing required columns: {', '.join(results['missing_columns'])}"
    issues = []
    for label, key in [
        ("duplicate finding IDs", "duplicate_finding_ids"),
        ("missing owners", "missing_owner"),
        ("missing or expired evidence records", "missing_evidence"),
        ("invalid due dates", "invalid_due_dates"),
        ("invalid identified dates", "invalid_identified_dates"),
        ("critical findings without action plans", "critical_without_action"),
    ]:
        if results.get(key, 0):
            issues.append(f"{results[key]} {label}")
    if not issues:
        return "No major data quality issues detected. Dataset is ready for audit reporting."
    return "Detected: " + "; ".join(issues) + "."
