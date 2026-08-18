"""RQ3 digital experiment: policies, seeds, sweeps, recovery, compound failures."""
from __future__ import annotations

from ntn_resilience.channel_assumptions import SCENARIO_FAMILIES, load_registry
from ntn_resilience.experiment import recovery_steps, run_experiment, simulate_run
from ntn_resilience.fallback_policy import POLICIES, select_path, select_policy_path


def test_legacy_select_path():
    assert select_path(True, False) == "terrestrial"
    assert select_path(False, True) == "ntn"
    assert select_path(False, False) == "offline"


def test_terrestrial_baseline_never_uses_ntn():
    run = simulate_run(policy="terrestrial_baseline", seed=1, ntn_visibility=1.0, terrestrial_outage_p=0.5)
    assert run["ntn_path_fraction"] == 0.0
    assert run["evidence_status"] == "synthetic_simulation"


def test_fallback_uses_ntn_when_terrestrial_down():
    path = select_policy_path(
        "fallback",
        terrestrial_up=False,
        ntn_visible=True,
        terrestrial_capacity_mbps=20,
        ntn_capacity_mbps=5,
        terrestrial_latency_ms=25,
        ntn_latency_ms=40,
        min_capacity_mbps=1,
        max_latency_ms=500,
    )
    assert path == "ntn"


def test_adaptive_prefers_lower_latency_when_both_ok():
    path = select_policy_path(
        "adaptive",
        terrestrial_up=True,
        ntn_visible=True,
        terrestrial_capacity_mbps=20,
        ntn_capacity_mbps=5,
        terrestrial_latency_ms=25,
        ntn_latency_ms=400,
        min_capacity_mbps=1,
        max_latency_ms=500,
    )
    assert path == "terrestrial"


def test_recovery_steps_and_repeated_seeds_are_deterministic():
    a = simulate_run(policy="fallback", seed=1)
    b = simulate_run(policy="fallback", seed=1)
    c = simulate_run(policy="fallback", seed=99)
    assert a["uptime_fraction"] == b["uptime_fraction"]
    assert a["offline_steps"] == b["offline_steps"]
    assert {a["uptime_fraction"], c["uptime_fraction"]}  # both defined
    assert recovery_steps([True, True, True]) == 0
    assert recovery_steps([True, False, False, True]) == 2


def test_compound_failure_reduces_uptime_vs_simple():
    simple = simulate_run(policy="fallback", seed=7, terrestrial_outage_p=0.2, compound=False)
    compound = simulate_run(
        policy="fallback", seed=7, terrestrial_outage_p=0.2, compound=True, power_outage_p=0.5
    )
    assert compound["uptime_fraction"] <= simple["uptime_fraction"] + 1e-9


def test_rq3_experiment_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert "urban_emergency" in SCENARIO_FAMILIES
    registry = load_registry()
    assert registry["assumptions"]["ntn_latency_ms"]["assumption_class"] == "literature_backed"
    result = run_experiment("rq3_gary_failover_sweeps", out_dir=tmp_path)
    assert result["research_question"] == "RQ3"
    names = {p["policy"] for p in result["policies"]}
    assert names == set(POLICIES)
    assert "ntn_latency_ms" in result["sweeps"]
    sweep_policies = {row["policy"] for row in result["sweeps"]["ntn_latency_ms"]}
    assert sweep_policies == set(POLICIES)
    assert result["findings"]["ntn_always_better"] is False
    assert result["findings"]["hypothesis_rejected"] is True
    assert result["findings"]["when_ntn_does_not_help"]["static_ntn_geo_worse_than_terrestrial"] is True
    assert result["decision_grids"]["latency_x_visibility"]
    assert any("operator" in n.lower() for n in result["non_claims"])
    assert result["wrote"]
