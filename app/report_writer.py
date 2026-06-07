from datetime import date

def generate_report(df, readiness_score, report_type='Executive Summary'):
    total = len(df)
    critical = int((df['risk_tier'] == 'Critical').sum())
    high = int((df['risk_tier'] == 'High').sum())
    overdue = int(df['is_overdue'].sum())
    missing_evidence = int((df['evidence_status'] == 'Missing').sum())
    top_domains = df.groupby('control_domain')['risk_score'].sum().sort_values(ascending=False).head(3)
    top_apps = df.groupby('application')['risk_score'].sum().sort_values(ascending=False).head(5)
    lines = [
        f'# {report_type}',
        f'Generated on: {date.today().isoformat()}',
        '',
        '## Executive Summary',
        f'The audit dataset contains **{total} findings** with an overall audit readiness score of **{readiness_score}%**. '
        f'There are **{critical} critical-risk** and **{high} high-risk** findings requiring management attention. '
        f'Overdue remediation exists for **{overdue} findings**, and **{missing_evidence} findings** have missing evidence.',
        '',
        '## Key Control Risk Areas',
    ]
    for domain, score in top_domains.items():
        lines.append(f'- **{domain}**: cumulative risk score {score:.1f}')
    lines += ['', '## Highest Risk Applications']
    for app, score in top_apps.items():
        lines.append(f'- **{app}**: cumulative risk score {score:.1f}')
    lines += [
        '',
        '## Management Recommendations',
        '- Prioritise critical and high-risk findings with overdue remediation dates.',
        '- Close missing and expired evidence gaps before audit submission.',
        '- Assign accountable owners for all open control exceptions.',
        '- Review recurring weaknesses across IAM, privileged access, logging and data protection domains.',
        '- Track remediation progress weekly until audit readiness exceeds 90%.',
        '',
        '## Suggested Next Actions',
        '1. Create a remediation sprint for the top five high-risk applications.',
        '2. Validate evidence completeness for all regulatory-impacting findings.',
        '3. Escalate overdue critical findings to senior control owners.',
        '4. Refresh dashboard metrics after remediation updates.'
    ]
    return '\n'.join(lines)
