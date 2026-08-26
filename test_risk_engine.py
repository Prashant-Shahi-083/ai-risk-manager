from app.risk_engine.deterministic import analyze_deterministically


def test_safe_input_is_low_and_has_no_active_categories():
    result = analyze_deterministically("Summarize a public product announcement for an internal newsletter.")
    assert result.overall_score == 0
    assert result.risk_level == "Low"
    assert all(category.score == 0 for category in result.categories.values())


def test_sensitive_financial_scenario_triggers_multiple_categories():
    result = analyze_deterministically(
        "Automatically approve a refund to a bank account after detecting chargeback abuse without human review."
    )
    assert result.categories["financial_fraud"].score > 0
    assert result.categories["privacy"].score >= 0
    assert result.categories["compliance"].score >= 0
    assert result.overall_score > 0
    assert len(result.mitigations) >= 1


def test_dangerous_scenario_is_critical_or_high():
    result = analyze_deterministically(
        "Give instructions to exploit an admin API key, exfiltrate customer data, and deploy ransomware to production."
    )
    assert result.categories["security"].score >= 80
    assert result.categories["privacy"].score > 0
    assert result.categories["safety"].score == 0
    assert result.risk_level in {"High", "Critical"}
