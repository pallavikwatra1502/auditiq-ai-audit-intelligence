
import pandas as pd
from risk_engine import priority_queue, audit_readiness_score

def answer_question(df: pd.DataFrame, question: str) -> str:
    q = question.lower().strip()

    if not q:
        return "Ask me about high-risk applications, overdue findings, control domains, owners, evidence gaps or audit readiness."

    if any(word in q for word in ["highest risk", "top risk", "risky application", "highest-risk"]):
        top = df.groupby("application")["risk_score"].mean().sort_values(ascending=False).head(5)
        return "Highest-risk applications by average risk score:\n" + "\n".join([f"- {idx}: {round(val,1)}" for idx, val in top.items()])

    if any(word in q for word in ["overdue", "late", "past due"]):
        od = df[df["is_overdue"]].sort_values("risk_score", ascending=False).head(8)
        if od.empty:
            return "No overdue open remediation items were found in the current filtered dataset."
        return "Top overdue remediation items:\n" + "\n".join([f"- {r.finding_id}: {r.application} | {r.severity} | owner {r.owner_team} | score {r.risk_score}" for r in od.itertuples()])

    if any(word in q for word in ["evidence", "missing proof", "expired"]):
        ev = df[df["evidence_status"].isin(["Missing", "Expired"])]
        by_domain = ev.groupby("control_domain").size().sort_values(ascending=False).head(5)
        return f"There are {len(ev)} findings with missing or expired evidence. Main domains:\n" + "\n".join([f"- {idx}: {val}" for idx, val in by_domain.items()])

    if any(word in q for word in ["owner", "team", "responsible"]):
        owners = df[df["status"].ne("Closed")].groupby("owner_team")["risk_score"].agg(["count", "mean"]).sort_values(["count", "mean"], ascending=False).head(6)
        return "Open findings by owner team:\n" + "\n".join([f"- {idx}: {int(row['count'])} open findings, avg score {round(row['mean'],1)}" for idx, row in owners.iterrows()])

    if any(word in q for word in ["readiness", "score", "audit ready"]):
        return f"The current audit readiness score is {audit_readiness_score(df)}/100. This score considers open findings, missing evidence and unresolved critical/high risks."

    if any(word in q for word in ["gdpr", "sox", "pci", "fca", "iso"]):
        regs = df.groupby("regulatory_mapping")["risk_score"].agg(["count", "mean"]).sort_values("mean", ascending=False)
        return "Regulatory risk summary:\n" + "\n".join([f"- {idx}: {int(row['count'])} findings, avg score {round(row['mean'],1)}" for idx, row in regs.iterrows()])

    if any(word in q for word in ["summary", "management", "executive"]):
        total = len(df)
        open_count = len(df[df["status"].ne("Closed")])
        high = len(df[(df["severity"].isin(["Critical","High"])) & (df["status"].ne("Closed"))])
        overdue = len(df[df["is_overdue"]])
        return f"Executive summary: {total} findings analysed, {open_count} remain open, {high} are open critical/high risk and {overdue} are overdue. Management should prioritise overdue high-risk items and missing evidence."

    pq = priority_queue(df, 5)
    return "I can help with audit readiness, highest-risk applications, overdue items, evidence gaps, owner accountability and regulatory risk. Top current priorities are:\n" + "\n".join([f"- {r.finding_id}: {r.application} | {r.severity} | score {r.risk_score}" for r in pq.itertuples()])
