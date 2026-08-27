"""RQ3 statistical parity + claim firewall tests."""
from __future__ import annotations

import math

import pytest

from ntn_resilience.claim_firewall import validate_claim_firewall
from ntn_resilience.experiment import run_experiment, simulate_run
from ntn_resilience.stats import (
    CI_SIM_VARIABILITY_WARNING,
    EVIDENCE_CLASS,
    T_CRIT_975,
    T_CRIT_VERIFICATION_SOURCE,
    mean_ci,
    paired_diff_ci,
    t_crit_975,
)


FIXED_SEEDS = list(range(1, 31))

SCIPY_T_PPF_975_REFERENCE = {
    1: 12.7062047362,
    3: 3.1824463053,
    11: 2.2009851601,
    19: 2.0930240544,
    29: 2.0452296421,
}


def test_t_crit_matches_scipy_reference_for_required_dfs():
    for df, expected in SCIPY_T_PPF_975_REFERENCE.items():
        assert abs(t_crit_975(df) - expected) < 1e-9
    assert abs(t_crit_975(1_000_000) - 1.95996398454) < 1e-4
    assert 11 in T_CRIT_975 and 19 in T_CRIT_975 and 29 in T_CRIT_975
    assert "SciPy" in T_CRIT_VERIFICATION_SOURCE


def test_mean_ci_rejects_non_95_level():
    with pytest.raises(ValueError, match="0.95"):
        mean_ci([0.1, 0.2, 0.3], level=0.99)


def test_mean_ci_n_lt_2_no_degenerate_ci():
    stats = mean_ci([0.5])
    assert stats["n"] == 1
    assert math.isnan(stats["ci_low"]) and math.isnan(stats["ci_high"])


def test_mean_ci_math():
    stats = mean_ci([0.7, 0.8, 0.75, 0.85])
    assert stats["n"] == 4
    assert abs(stats["mean"] - 0.775) < 1e-12
    half = t_crit_975(3) * stats["std"] / 2.0
    assert abs(stats["ci_low"] - (0.775 - half)) < 1e-12
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
    assert result["seeds"] == FIXED_SEEDS
    policies = {p["policy"]: p for p in result["policies"]}
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
            assert "paired_cohens_d_z" in paired
            assert "cohens_d_vs_baseline" not in paired
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


def test_paired_diff_ci_uses_dz():
    paired = paired_diff_ci([0.8, 0.9, 0.85, 0.88], [0.7, 0.75, 0.72, 0.74])
    assert paired["mean"] > 0
    assert math.isfinite(paired["ci_high"])
    assert math.isfinite(paired["paired_cohens_d_z"])
    assert paired["paired_cohens_d_z"] == paired["mean"] / paired["std"]
    assert "cohens_d_vs_baseline" not in paired
