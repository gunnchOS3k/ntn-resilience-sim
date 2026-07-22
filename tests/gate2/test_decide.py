"""NTN Gate 2 decision tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ntn_resilience.gate2.decide import decide, sha256_file

FK = Path(__file__).resolve().parents[3] / "gunnchos-7gc-ai-ran-field-kit"
TWIN = FK / "fixtures/valid/twin_state_bundle.valid.json"
AIRAN = FK / "fixtures/valid/airan_decision_bundle.valid.json"
SCHEMA = FK / "contracts"


def _with_hashes(tmp_path, twin_doc, airan_doc):
    t = tmp_path / "twin.json"
    t.write_text(json.dumps(twin_doc))
    airan_doc = json.loads(json.dumps(airan_doc))
    airan_doc["run_id"] = twin_doc["run_id"]
    airan_doc["site_id"] = twin_doc["site_id"]
    airan_doc["input_twin_state_hash"] = sha256_file(t)
    a = tmp_path / "airan.json"
    a.write_text(json.dumps(airan_doc))
    return t, a


def test_terrestrial_selected_when_available(tmp_path):
    twin = json.loads(TWIN.read_text())
    airan = json.loads(AIRAN.read_text())
    twin["outage_state"]["values"]["terrestrial_outage"] = False
    for c in twin["connectivity_candidates"]:
        if c["network"] == "terrestrial":
            c["available"] = True
            c["estimated_latency_ms"] = 40
    t, a = _with_hashes(tmp_path, twin, airan)
    bundle = decide(t, a, tmp_path / "out.json", schema_dir=SCHEMA)
    assert bundle["selected_mode"] == "terrestrial"


def test_ntn_when_terrestrial_down_and_latency_ok(tmp_path):
    twin = json.loads(TWIN.read_text())
    airan = json.loads(AIRAN.read_text())
    twin["outage_state"]["values"]["terrestrial_outage"] = True
    twin["service_demand"]["values"]["latency_budget_ms"] = 200
    for c in twin["connectivity_candidates"]:
        if c["network"] == "terrestrial":
            c["available"] = False
        if c["network"] == "degraded_local":
            c["available"] = False
        if c["network"] == "local_edge_wifi":
            c["available"] = False
    t, a = _with_hashes(tmp_path, twin, airan)
    bundle = decide(t, a, tmp_path / "out.json", schema_dir=SCHEMA)
    assert bundle["selected_mode"] == "ntn_fallback"


def test_degraded_local_when_ntn_too_slow(tmp_path):
    twin = json.loads(TWIN.read_text())
    airan = json.loads(AIRAN.read_text())
    twin["outage_state"]["values"]["terrestrial_outage"] = True
    twin["service_demand"]["values"]["latency_budget_ms"] = 20  # below configured NTN 45ms
    for c in twin["connectivity_candidates"]:
        if c["network"] == "terrestrial":
            c["available"] = False
        if c["network"] == "local_edge_wifi":
            c["available"] = False
        if c["network"] == "degraded_local":
            c["available"] = True
            c["estimated_latency_ms"] = 15
    t, a = _with_hashes(tmp_path, twin, airan)
    # make ntn infeasible via assumption override
    import yaml
    from ntn_resilience.gate2.decide import load_assumption_registry

    reg = load_assumption_registry()
    reg["assumptions"]["ntn_latency_ms"]["value"] = 80
    reg_path = tmp_path / "reg.yaml"
    reg_path.write_text(yaml.safe_dump(reg))
    bundle = decide(
        t, a, tmp_path / "out.json", schema_dir=SCHEMA, assumption_registry_path=reg_path
    )
    assert bundle["selected_mode"] == "degraded_local"


def test_offline_when_no_mode_fits(tmp_path):
    twin = json.loads(TWIN.read_text())
    airan = json.loads(AIRAN.read_text())
    twin["outage_state"]["values"]["terrestrial_outage"] = True
    twin["service_demand"]["values"]["latency_budget_ms"] = 1
    twin["energy_constraints"]["values"]["energy_budget_j"] = 0.1
    for c in twin["connectivity_candidates"]:
        c["available"] = False
    # offline always considered
    t, a = _with_hashes(tmp_path, twin, airan)
    bundle = decide(t, a, tmp_path / "out.json", schema_dir=SCHEMA)
    assert bundle["selected_mode"] == "offline_continuation"


def test_mismatched_airan_rejected(tmp_path):
    twin = json.loads(TWIN.read_text())
    airan = json.loads(AIRAN.read_text())
    t = tmp_path / "twin.json"
    t.write_text(json.dumps(twin))
    airan["input_twin_state_hash"] = "0" * 64
    a = tmp_path / "airan.json"
    a.write_text(json.dumps(airan))
    with pytest.raises(ValueError, match="input_twin_state_hash"):
        decide(t, a, tmp_path / "out.json", schema_dir=SCHEMA)
