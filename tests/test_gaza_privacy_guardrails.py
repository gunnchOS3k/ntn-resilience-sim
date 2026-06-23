from sites.metrics import compute_metrics


def test_gaza_privacy_score():
    m = compute_metrics("gaza")
    assert m["privacy_risk_score"] >= 0.5
