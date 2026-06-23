from pathlib import Path

import yaml

from sites.metrics import compute_metrics
from sites.site_registry import SITE_IDS

ROOT = Path(__file__).resolve().parents[1]


def test_all_site_configs():
    for sid in SITE_IDS:
        path = ROOT / "configs" / "sites" / sid / "baseline.yaml"
        assert path.exists(), sid
        data = yaml.safe_load(path.read_text())
        assert data["site_id"] == sid
        assert "units" in data


def test_outage_model():
    from sites.outage_model import outage_timeline

    tl = outage_timeline("gary", steps=10, seed=1)
    assert len(tl) == 10
    assert "path" in tl[0]


def test_edge_cache():
    from sites.edge_cache import edge_cache_simulation

    r = edge_cache_simulation("gaza")
    assert r["offline_continuity_score"] > 0


def test_metrics():
    m = compute_metrics("graham_land")
    assert "resilience_score" in m
    assert m["units"]["latency"] == "ms"


def test_gaza_privacy_guardrails():
    m = compute_metrics("gaza")
    assert m["privacy_risk_score"] >= 0.5
    readme = (ROOT / "docs" / "sites" / "gaza" / "README.md").read_text()
    assert "privacy" in readme.lower() or "sensitive" in readme.lower()


def test_graham_land_non_claim_policy():
    m = compute_metrics("graham_land")
    assert m["link_margin_db"] is not None
    readme = (ROOT / "docs" / "sites" / "graham_land" / "README.md").read_text()
    assert "conceptual" in readme.lower() or "field operation" in readme.lower()


def test_run_all_sites_cli():
    from sites.run_site_scenario import run_scenario

    for sid in SITE_IDS:
        result = run_scenario(sid)
        assert result["metrics"]["site_id"] == sid
