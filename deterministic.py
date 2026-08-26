from dataclasses import dataclass
import re

from app.schemas.risk import Mitigation, RiskAssessment, RiskCategory

CATEGORY_WEIGHTS: dict[str, float] = {
    "privacy": 0.16,
    "security": 0.16,
    "financial_fraud": 0.16,
    "bias_fairness": 0.14,
    "hallucination_factuality": 0.14,
    "compliance": 0.12,
    "safety": 0.12,
}

CATEGORY_LABELS = {
    "privacy": "Privacy",
    "security": "Security",
    "financial_fraud": "Financial / fraud",
    "bias_fairness": "Bias / fairness",
    "hallucination_factuality": "Hallucination / factuality",
    "compliance": "Compliance",
    "safety": "Safety",
}


@dataclass(frozen=True)
class SignalRule:
    category: str
    score: int
    signal: str
    keywords: tuple[str, ...]


RULES = (
    SignalRule("privacy", 42, "Personal or sensitive data is present or requested", ("password", "otp", "one-time password", "pan", "aadhaar", "social security", "ssn", "medical record", "health record", "phone number", "email address", "location history", "biometric")),
    SignalRule("privacy", 24, "The scenario involves collecting, sharing, or exposing user data", ("upload contacts", "share data", "sell data", "scrape", "track users", "customer data", "employee data")),
    SignalRule("security", 52, "The input requests credentials, bypasses, or offensive behavior", ("steal", "bypass authentication", "disable mfa", "disable 2fa", "credential", "ransomware", "exploit", "exfiltrate", "malware", "phishing")),
    SignalRule("security", 28, "A high-impact system or privileged action is involved", ("admin access", "production database", "deploy to prod", "root access", "api key", "secret key")),
    SignalRule("financial_fraud", 58, "The input contains fraud, evasion, or unauthorized money movement signals", ("fraud", "fake invoice", "launder", "evade payment", "chargeback abuse", "steal money", "unauthorized transfer", "money mule")),
    SignalRule("financial_fraud", 30, "The scenario makes a consequential financial recommendation or decision", ("approve loan", "deny loan", "credit score", "insurance claim", "investment", "send payment", "refund customer", "bank account")),
    SignalRule("bias_fairness", 48, "The decision uses protected or sensitive attributes", ("gender", "race", "religion", "caste", "disability", "pregnancy", "age", "nationality", "ethnicity")),
    SignalRule("bias_fairness", 28, "The input ranks, screens, or excludes people", ("hire", "reject candidate", "rank applicants", "screen applicants", "fire employee", "eligibility", "automated decision")),
    SignalRule("hallucination_factuality", 34, "The output makes factual, legal, medical, or financial claims that need verification", ("diagnose", "legal advice", "guaranteed return", "cite sources", "according to", "medical advice", "compliance advice", "fact")),
    SignalRule("hallucination_factuality", 22, "The requested decision depends on incomplete or unverified information", ("without checking", "assume", "make up", "unknown", "no evidence", "guess")),
    SignalRule("compliance", 42, "The scenario involves regulated data, decisions, or obligations", ("gdpr", "dpdp", "hipaa", "pci", "aml", "kyc", "regulatory", "tax", "audit", "compliance")),
    SignalRule("compliance", 24, "The proposed action may lack consent, notice, review, or retention controls", ("without consent", "no consent", "keep forever", "delete records", "hide from user", "no audit trail")),
    SignalRule("safety", 62, "The input involves physical harm, self-harm, weapons, or dangerous instructions", ("weapon", "explosive", "poison", "self-harm", "suicide", "hurt someone", "unsafe dosage", "dangerous")),
    SignalRule("safety", 30, "The scenario controls a safety-sensitive or vulnerable-user context", ("child", "minor", "patient", "vehicle control", "medical device", "emergency", "factory")),
)

DEFAULT_RATIONALE = {
    "privacy": "No strong privacy signal was detected by the demo rules.",
    "security": "No strong security signal was detected by the demo rules.",
    "financial_fraud": "No strong financial or fraud signal was detected by the demo rules.",
    "bias_fairness": "No strong bias or fairness signal was detected by the demo rules.",
    "hallucination_factuality": "No strong factuality signal was detected by the demo rules.",
    "compliance": "No strong compliance signal was detected by the demo rules.",
    "safety": "No strong safety signal was detected by the demo rules.",
}

MITIGATION_LIBRARY = {
    "privacy": ("Minimize data collection, redact sensitive fields, and document consent and retention rules.", "Privacy / data owner"),
    "security": ("Use least privilege, isolate the action, add authentication and audit logging, and test abuse cases.", "Security owner"),
    "financial_fraud": ("Require human approval for money movement, add transaction limits, and evaluate false positives and false negatives.", "Risk / finance owner"),
    "bias_fairness": ("Remove unnecessary sensitive attributes, measure subgroup outcomes, and add human review before adverse decisions.", "Responsible AI owner"),
    "hallucination_factuality": ("Verify claims against trusted sources, show uncertainty, and block high-impact actions when evidence is missing.", "Domain reviewer"),
    "compliance": ("Map the workflow to applicable obligations, preserve an audit trail, and obtain legal/compliance review before deployment.", "Compliance owner"),
    "safety": ("Add hard safety boundaries, refuse dangerous instructions, and require qualified human oversight for high-impact contexts.", "Safety owner"),
}


def _risk_level(score: int) -> str:
    if score < 25:
        return "Low"
    if score < 50:
        return "Medium"
    if score < 75:
        return "High"
    return "Critical"


def analyze_deterministically(text: str) -> RiskAssessment:
    lowered = text.lower()
    category_scores = {key: 0 for key in CATEGORY_WEIGHTS}
    category_signals: dict[str, list[str]] = {key: [] for key in CATEGORY_WEIGHTS}

    for rule in RULES:
        if any(re.search(rf"\b{re.escape(keyword)}\b", lowered) for keyword in rule.keywords):
            category_scores[rule.category] = min(100, category_scores[rule.category] + rule.score)
            if rule.signal not in category_signals[rule.category]:
                category_signals[rule.category].append(rule.signal)

    categories: dict[str, RiskCategory] = {}
    for key, score in category_scores.items():
        label = CATEGORY_LABELS[key]
        if category_signals[key]:
            rationale = f"{label} indicators were triggered by the input: " + "; ".join(category_signals[key]) + "."
        else:
            rationale = DEFAULT_RATIONALE[key]
        categories[key] = RiskCategory(score=score, rationale=rationale, signals=category_signals[key])

    weighted_score = round(sum(category_scores[key] * weight for key, weight in CATEGORY_WEIGHTS.items()))
    # Preserve a high-signal floor so one severe category is not hidden by
    # unrelated zeroes. The floor is intentionally documented in the README.
    highest_category = max(category_scores.values(), default=0)
    weighted_score = max(weighted_score, round(highest_category * 0.75))
    top_categories = sorted(category_scores.items(), key=lambda item: item[1], reverse=True)
    active = [CATEGORY_LABELS[key] for key, score in top_categories if score > 0]
    score_level = _risk_level(weighted_score)

    if active:
        summary = f"The prototype detected the strongest signals in {', '.join(active[:3])}. Treat this as a triage result, not a certified compliance or safety decision."
    else:
        summary = "The prototype did not detect strong keyword signals. Absence of a signal does not mean the scenario is safe; review context and evidence before acting."

    mitigations: list[Mitigation] = []
    for key, score in top_categories:
        if score <= 0:
            continue
        priority = "Immediate" if score >= 60 else "High" if score >= 40 else "Medium"
        action, owner = MITIGATION_LIBRARY[key]
        mitigations.append(Mitigation(priority=priority, action=action, owner=owner))

    if not mitigations:
        mitigations.append(Mitigation(priority="Medium", action="Add a human review checkpoint, confirm the source evidence, and document the decision boundary before deployment.", owner="Builder"))

    return RiskAssessment(
        overall_score=weighted_score,
        risk_level=score_level,
        summary=summary,
        categories=categories,
        mitigations=mitigations,
        assumptions=[
            "This is a transparent keyword-and-rule demonstration engine, not a trained risk model.",
            "The input is treated as untrusted text and no external facts are verified.",
            "A human should review any decision involving people, money, regulated data, or physical safety.",
        ],
        engine="deterministic-demo",
    )
