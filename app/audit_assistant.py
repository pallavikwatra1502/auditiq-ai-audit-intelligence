def answer_question(question, df):
    q = question.lower().strip()
    if not q:
        return 'Ask a question about audit findings, risk, overdue items, evidence or applications.'
    if 'highest' in q or 'top' in q or 'risky' in q:
        top = df.groupby('application')['risk_score'].sum().sort_values(ascending=False).head(5)
        return 'Highest risk applications:\n' + '\n'.join([f'- {k}: {v:.1f}' for k, v in top.items()])
    if 'overdue' in q:
        x = df[df['is_overdue']].sort_values('risk_score', ascending=False).head(10)
        return f'There are {len(df[df["is_overdue"]])} overdue findings. Top overdue items:\n' + '\n'.join([f'- {r.finding_id}: {r.application} | {r.severity} | {r.owner}' for r in x.itertuples()])
    if 'evidence' in q:
        counts = df['evidence_status'].value_counts()
        return 'Evidence status summary:\n' + '\n'.join([f'- {k}: {v}' for k, v in counts.items()])
    if 'gdpr' in q or 'fca' in q or 'sox' in q or 'pci' in q:
        reg = 'GDPR' if 'gdpr' in q else 'FCA' if 'fca' in q else 'SOX' if 'sox' in q else 'PCI-DSS'
        x = df[df['regulatory_impact'].str.upper() == reg.upper()]
        return f'{reg} related findings: {len(x)}. Open/In Progress: {len(x[x["status"].isin(["Open","In Progress"])])}.'
    if 'summary' in q or 'management' in q:
        return f'Audit summary: {len(df)} findings analysed, {int((df["risk_tier"]=="Critical").sum())} critical-tier risks, {int(df["is_overdue"].sum())} overdue items, and {int((df["evidence_status"]=="Missing").sum())} missing evidence gaps. Management should prioritise overdue critical findings and evidence completion.'
    if 'domain' in q or 'control' in q:
        top = df.groupby('control_domain')['risk_score'].sum().sort_values(ascending=False).head(5)
        return 'Highest risk control domains:\n' + '\n'.join([f'- {k}: {v:.1f}' for k, v in top.items()])
    return 'I can answer questions such as: highest risk applications, overdue findings, evidence gaps, GDPR/FCA impact, top control domains, or management summary.'
