
import pandas as pd
from risk_engine import audit_readiness_score, priority_queue

def _fmt_pct(part, whole):
    return "0%" if whole == 0 else f"{round((part / whole) * 100, 1)}%"

def generate_executive_report(df: pd.DataFrame, report_type: str = "Executive Audit Report") -> str:
    total = len(df)
    readiness = audit_readiness_score(df)
    open_df = df[df["status"].ne("Closed")]
    critical_high = df[(df["severity"].isin(["Critical", "High"])) & (df["status"].ne("Closed"))]
    overdue = df[df["is_overdue"]]
    missing_ev = df[df["evidence_status"].isin(["Missing", "Expired"])]
    top_domains = df.groupby("control_domain")["risk_score"].mean().sort_values(ascending=False).head(5)
    top_apps = df.groupby("application")["risk_score"].mean().sort_values(ascending=False).head(5)
    queue = priority_queue(df, 8)

    md = f"""# {report_type}

## Executive Summary

AuditIQ analysed **{total} control findings** across cloud security, data governance and data quality domains. The current audit readiness score is **{readiness}/100**.

Key risk indicators:
- **{len(open_df)} open findings** ({_fmt_pct(len(open_df), total)} of total)
- **{len(critical_high)} open critical/high findings**
- **{len(overdue)} overdue remediation items**
- **{len(missing_ev)} findings with missing or expired evidence**

## Key Control Weaknesses

The highest-risk control domains by average score are:

"""
    for domain, score in top_domains.items():
        md += f"- **{domain}** — average risk score {round(score, 1)}\n"

    md += "\n## Highest-Risk Applications\n\n"
    for app, score in top_apps.items():
        md += f"- **{app}** — average risk score {round(score, 1)}\n"

    md += "\n## Priority Remediation Queue\n\n"
    for _, r in queue.iterrows():
        md += f"- **{r['finding_id']} | {r['application']} | {r['severity']} | Score {r['risk_score']}** — {r['management_action']}\n"

    md += """

## Management Recommendations

1. Prioritise overdue critical and high-risk findings with missing evidence.
2. Establish automated evidence collection for cloud security and data governance controls.
3. Assign clear ownership for repeat findings and track remediation through weekly governance.
4. Improve data quality checks before audit reporting to reduce manual validation.
5. Monitor high-risk applications continuously using risk score thresholds.

## Conclusion

The audit portfolio shows measurable remediation progress opportunities. The most immediate value will come from closing overdue high-risk findings, improving evidence completeness and strengthening governance around repeat control failures.
"""
    return md
