"""RQ3 statistical parity + claim firewall tests."""
from __future__ import annotations

import math

import pytest

from ntn_resilience.claim_firewall import validate_claim_firewall
from ntn_resilience.experiment import run_experiment, simulate_run
from ntn_resilience.stats import CI_SIM_VARIABILITY_WARNING, EVIDENCE_CLASS, mean_ci, paired_diff_ci


FIXED_SEEDS = [1, 2, 7, 42]


def test_mean_ci_math():
    stats = mean_ci([0.7, 0.8, 0.75, 0.85])
    assert stats["n"] == 4
    assert abs(stats["mean"] - 0.775) < 1e-12
    assert stats["ci_low"] < stats["mean"] < stats["ci_high"]


def test_fixed_seed_repro():
    a = simulate_run(policy="fallback", seed=1)
    b = simulate_run(policy="fallback", seed=1)
    assert a["min_service_fraction"] == b["min_service_fraction"]
    assert a["evidence_class"] == EVIDENCE_CLASS


def test_rq3_statistical_parity_and_firewall(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = run_experiment("rq3_gary_failover_sweeps", out_dir=tmp_path)
    assert result["evidence_class"] == EVIDENCE_CLASS
    assert result["ci_warning"] == CI_SIM_VARIABILITY_WARNING
    assert result["claim_firewall"]["ok"] is True
    assert result["decision_region_boundaries"]["local_peer_not_in_paper_iii_engine"] is True
    policies = {p["policy"]: p for p in result["policies"]}
    # Policy ordering under fixtures: adaptive/fallback should not invent NTN-always-better
    assert result["findings"]["ntn_always_better"] is False
    for name, block in policies.items():
        st = block["statistics"]
        assert st["n"] == len(FIXED_SEEDS)
        assert math.isfinite(st["mean_min_service"])
        assert math.isfinite(st["ci95_min_service"]["low"])
        assert "ci_warning" in st
        if name != "terrestrial_baseline":
            paired = st["paired_vs_terrestrial"]["min_service_fraction"]
            assert paired["paired"] is True
            assert len(paired["diffs"]) == len(FIXED_SEEDS)
    # Decision-region boundary serialization
    bounds = result["decision_region_boundaries"]
    assert bounds["hurts_examples"] is not None or bounds["ntn_hurts_count"] is not None
    assert "SYNTHETIC_SIM" in str(bounds["evidence_class"])


def test_claim_firewall_rejects_ntn_always_better():
    bad = {
        "evidence_class": EVIDENCE_CLASS,
        "findings": {"ntn_always_better": True, "hypothesis_rejected": True},
        "non_claims": ["Not operator performance"],
        "when_ntn_helps": {},
    }
    with pytest.raises(ValueError):
        validate_claim_firewall(bad)


def test_paired_diff_ci():
    paired = paired_diff_ci([0.8, 0.9, 0.85, 0.88], [0.7, 0.75, 0.72, 0.74])
    assert paired["mean"] > 0
    assert math.isfinite(paired["ci_high"])
