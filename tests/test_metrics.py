from sites.metrics import compute_metrics
from sites.site_registry import SITE_IDS


def test_all_metrics():
    for sid in SITE_IDS:
        m = compute_metrics(sid)
        assert 0 <= m["resilience_score"] <= 1.5
