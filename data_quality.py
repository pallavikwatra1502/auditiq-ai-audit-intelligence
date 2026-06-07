import pandas as pd

def quality_checks(df: pd.DataFrame) -> pd.DataFrame:
    checks = []
    checks.append({'check': 'Missing owners', 'count': int(df['owner'].isna().sum() + (df['owner'].astype(str).str.strip() == '').sum()), 'severity': 'High'})
    checks.append({'check': 'Missing evidence', 'count': int((df['evidence_status'] == 'Missing').sum()), 'severity': 'High'})
    checks.append({'check': 'Expired evidence', 'count': int((df['evidence_status'] == 'Expired').sum()), 'severity': 'Medium'})
    checks.append({'check': 'Duplicate finding IDs', 'count': int(df['finding_id'].duplicated().sum()), 'severity': 'Critical'})
    checks.append({'check': 'Overdue remediation', 'count': int(df.get('is_overdue', False).sum()), 'severity': 'High'})
    checks.append({'check': 'Open critical findings', 'count': int(((df['severity'] == 'Critical') & (df['status'] != 'Remediated')).sum()), 'severity': 'Critical'})
    return pd.DataFrame(checks)
