"""NTN Gate 2 multi-access resilience decisions."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml


MODES = [
    "terrestrial",
    "local_edge_wifi",
    "device_to_device",
    "degraded_local",
    "delayed_synchronization",
    "ntn_fallback",
    "offline_continuation",
]

POLICIES = [
    "terrestrial_only",
    "terrestrial_then_offline",
    "always_ntn_on_terrestrial_failure",
    "priority_class_fallback",
    "service_aware_multi_access",
    "oracle_hindsight_analysis_only",
]


def resolve_schema_dir(schema_dir: str | Path | None = None) -> Path:
    if schema_dir is not None:
        return Path(schema_dir).expanduser().resolve()
    env = os.environ.get("GATE2_CONTRACTS_DIR")
    if env:
        return Path(env).expanduser().resolve()
    sibling = (
        Path(__file__).resolve().parents[4]
        / "gunnchos-7gc-ai-ran-field-kit"
        / "contracts"
    )
    if sibling.is_dir():
        return sibling
    raise FileNotFoundError("Pass --schema-dir or set GATE2_CONTRACTS_DIR")


def load_validator(schema_dir: Path):
    candidate = schema_dir.parent / "scripts" / "validate_contract.py"
    spec = importlib.util.spec_from_file_location("gate2_validate_contract", candidate)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {candidate}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(repo_root: Path | None = None) -> str:
    root = repo_root or Path(__file__).resolve().parents[3]
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def load_assumption_registry(path: Path | None = None) -> dict[str, Any]:
    cfg = path or Path(__file__).resolve().parents[3] / "config" / "assumption_registry.yaml"
    return yaml.safe_load(cfg.read_text(encoding="utf-8"))


def _assumption(registry: dict[str, Any], key: str) -> dict[str, Any]:
    item = registry["assumptions"][key]
    return {
        "value": item["value"],
        "unit": item["unit"],
        "source_id": key,
        "range": item["range"],
        "assumption_class": item["assumption_class"],
    }


def _candidate_map(twin: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {c["network"]: c for c in twin.get("connectivity_candidates", [])}


def _score_mode(
    mode: str,
    twin: dict[str, Any],
    airan: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    cand = _candidate_map(twin)
    summary = twin["source_measurement"]["summary"]
    latency_budget = float(
        twin["service_demand"]["values"].get("latency_budget_ms")
        or twin["user_demands"][0]["latency_budget_ms"]
    )
    energy_budget = float(twin["energy_constraints"]["values"].get("energy_budget_j", 100))
    privacy_max = 0.6

    ntn_lat = float(registry["assumptions"]["ntn_latency_ms"]["value"])
    ntn_cap = float(registry["assumptions"]["ntn_capacity_mbps"]["value"])
    ntn_avail = float(registry["assumptions"]["ntn_availability"]["value"])
    handover = float(registry["assumptions"]["handover_delay_s"]["value"])
    ntn_energy = float(registry["assumptions"]["ntn_energy_cost_j"]["value"])
    terr_outage = float(registry["assumptions"]["terrestrial_outage_duration_s"]["value"])

    terrestrial_up = not bool(twin["outage_state"]["values"].get("terrestrial_outage"))

    if mode == "terrestrial":
        available = terrestrial_up and cand.get("terrestrial", {}).get("available", False)
        latency = float(summary["mean_latency_ms"])
        capacity = float(summary["mean_download_mbps"])
        energy = 10.0
        privacy = 0.2
        recovery = 0.0 if available else terr_outage
    elif mode == "local_edge_wifi":
        available = bool(cand.get("local_edge_wifi", {}).get("available"))
        latency = float(cand.get("local_edge_wifi", {}).get("estimated_latency_ms") or 20.0)
        capacity = float(cand.get("local_edge_wifi", {}).get("estimated_capacity_mbps") or 10.0)
        energy = 8.0
        privacy = 0.15
        recovery = handover * 0.5
    elif mode == "device_to_device":
        available = bool(cand.get("device_to_device", {}).get("available"))
        latency = float(cand.get("device_to_device", {}).get("estimated_latency_ms") or 30.0)
        capacity = float(cand.get("device_to_device", {}).get("estimated_capacity_mbps") or 2.0)
        energy = 6.0
        privacy = 0.25
        recovery = handover
    elif mode == "degraded_local":
        available = bool(cand.get("degraded_local", {}).get("available", True))
        latency = float(cand.get("degraded_local", {}).get("estimated_latency_ms") or summary["mean_latency_ms"] * 1.5)
        capacity = float(cand.get("degraded_local", {}).get("estimated_capacity_mbps") or 1.0)
        energy = 7.0
        privacy = 0.2
        recovery = 5.0
    elif mode == "delayed_synchronization":
        available = True
        latency = latency_budget * 2
        capacity = 0.5
        energy = 4.0
        privacy = 0.1
        recovery = 60.0
    elif mode == "ntn_fallback":
        available = bool(cand.get("ntn_fallback", {}).get("available", True)) and ntn_avail > 0.5
        latency = ntn_lat
        capacity = ntn_cap
        energy = ntn_energy
        privacy = 0.35
        recovery = handover + terr_outage * 0.1
    else:  # offline_continuation
        available = True
        latency = 0.0
        capacity = 0.0
        energy = 1.0
        privacy = 0.05
        recovery = terr_outage

    rejects = []
    if not available:
        rejects.append("unavailable")
    if mode != "offline_continuation" and latency > latency_budget:
        rejects.append("latency_budget")
    if energy > energy_budget:
        rejects.append("energy_budget")
    if privacy > privacy_max:
        rejects.append("privacy_budget")

    # Continuity utility computed, not hard-coded
    if mode == "offline_continuation":
        continuity = 0.25
        retained = ["local_cache"]
        suspended = ["realtime_sync", "interactive_uplink"]
    else:
        continuity = max(
            0.0,
            min(
                1.0,
                (1.0 if available else 0.0)
                * (1.0 - min(latency, latency_budget * 2) / (latency_budget * 2))
                * (0.5 + 0.5 * min(1.0, capacity / 5.0)),
            ),
        )
        retained = ["basic_service"]
        suspended = []
        if latency > latency_budget:
            suspended.append("latency_sensitive_features")

    feasible = available and "latency_budget" not in rejects and "energy_budget" not in rejects and "privacy_budget" not in rejects
    if mode == "offline_continuation":
        feasible = "energy_budget" not in rejects and "privacy_budget" not in rejects

    return {
        "mode": mode,
        "available": available,
        "feasible": feasible,
        "latency_ms": latency,
        "capacity_mbps": capacity,
        "energy_j": energy,
        "privacy_cost": privacy,
        "recovery_s": recovery,
        "continuity_score": continuity,
        "retained": retained,
        "suspended": suspended,
        "reject_reasons": rejects,
        "path_availability": 1.0 if available else 0.0,
    }


def decide(
    twin_path: Path,
    airan_path: Path,
    output: Path,
    *,
    policy_name: str = "service_aware_multi_access",
    schema_dir: Path | None = None,
    assumption_registry_path: Path | None = None,
) -> dict[str, Any]:
    if policy_name not in POLICIES:
        raise ValueError(f"Unknown policy: {policy_name}")

    schema_path = resolve_schema_dir(schema_dir)
    mod = load_validator(schema_path)
    twin = json.loads(twin_path.read_text(encoding="utf-8"))
    airan = json.loads(airan_path.read_text(encoding="utf-8"))
    mod.validate_document(twin, schema_path, expected_schema_name="gunnchos.twin_state_bundle", enforce_privacy=False)
    mod.validate_document(airan, schema_path, expected_schema_name="gunnchos.airan_decision_bundle", enforce_privacy=False)

    twin_hash = sha256_file(twin_path)
    airan_hash = sha256_file(airan_path)

    if airan.get("run_id") != twin.get("run_id"):
        raise ValueError(
            f"run_id mismatch: twin={twin.get('run_id')!r} airan={airan.get('run_id')!r}"
        )
    if airan.get("site_id") != twin.get("site_id"):
        raise ValueError("site_id mismatch between twin state and AI-RAN decision")
    if airan.get("input_twin_state_hash") != twin_hash:
        raise ValueError(
            "AI-RAN decision input_twin_state_hash does not match provided twin-state file"
        )

    registry = load_assumption_registry(assumption_registry_path)
    t0 = time.perf_counter()
    scores = [_score_mode(mode, twin, airan, registry) for mode in MODES]
    by_mode = {s["mode"]: s for s in scores}

    terrestrial_up = not bool(twin["outage_state"]["values"].get("terrestrial_outage"))
    latency_budget = float(twin["service_demand"]["values"].get("latency_budget_ms", 150))

    selected = None
    trigger = "policy_evaluation"
    deployable = True

    if policy_name == "terrestrial_only":
        selected = "terrestrial" if by_mode["terrestrial"]["feasible"] else "offline_continuation"
        trigger = "terrestrial_only"
    elif policy_name == "terrestrial_then_offline":
        selected = "terrestrial" if by_mode["terrestrial"]["feasible"] else "offline_continuation"
        trigger = "terrestrial_then_offline"
    elif policy_name == "always_ntn_on_terrestrial_failure":
        if by_mode["terrestrial"]["feasible"]:
            selected = "terrestrial"
            trigger = "terrestrial_available"
        else:
            selected = "ntn_fallback" if by_mode["ntn_fallback"]["feasible"] else "offline_continuation"
            trigger = "terrestrial_failure"
    elif policy_name == "priority_class_fallback":
        order = ["terrestrial", "local_edge_wifi", "ntn_fallback", "degraded_local", "offline_continuation"]
        for mode in order:
            if by_mode[mode]["feasible"]:
                selected = mode
                trigger = f"priority_select:{mode}"
                break
        selected = selected or "offline_continuation"
    elif policy_name == "oracle_hindsight_analysis_only":
        selected = max(scores, key=lambda s: s["continuity_score"])["mode"]
        trigger = "oracle_hindsight_analysis_only"
        deployable = False
    else:  # service_aware_multi_access
        if by_mode["terrestrial"]["feasible"] and terrestrial_up:
            selected = "terrestrial"
            trigger = "terrestrial_superior"
        elif by_mode["ntn_fallback"]["feasible"] and by_mode["ntn_fallback"]["latency_ms"] <= latency_budget:
            selected = "ntn_fallback"
            trigger = "ntn_within_latency_budget"
        elif by_mode["degraded_local"]["feasible"]:
            selected = "degraded_local"
            trigger = "ntn_violates_latency_or_unavailable"
        elif by_mode["local_edge_wifi"]["feasible"]:
            selected = "local_edge_wifi"
            trigger = "local_edge_fallback"
        else:
            selected = "offline_continuation"
            trigger = "no_communication_mode_meets_constraints"

    assert selected is not None
    best = by_mode[selected]
    rejected = []
    for s in scores:
        if s["mode"] == selected:
            continue
        reason = ", ".join(s["reject_reasons"]) if s["reject_reasons"] else (
            "lower_continuity_than_selected" if s["continuity_score"] <= best["continuity_score"] else "policy_ordering"
        )
        if s["feasible"] and s["continuity_score"] > best["continuity_score"] and policy_name != "oracle_hindsight_analysis_only":
            reason = "rejected_by_policy_even_if_higher_score"
        rejected.append({"mode": s["mode"], "reason": reason or "not_selected"})

    assumptions_used = [
        _assumption(registry, k)
        for k in (
            "ntn_latency_ms",
            "ntn_capacity_mbps",
            "ntn_availability",
            "handover_delay_s",
            "ntn_energy_cost_j",
            "terrestrial_outage_duration_s",
        )
    ]

    bundle = {
        "schema_name": "gunnchos.resilience_decision_bundle",
        "schema_version": "1.0.0",
        "run_id": twin["run_id"],
        "site_id": twin["site_id"],
        "policy_name": policy_name,
        "selected_mode": selected,
        "fallback_trigger": trigger,
        "input_twin_state_hash": twin_hash,
        "input_airan_decision_hash": airan_hash,
        "continuity_score": float(best["continuity_score"]),
        "expected_recovery_time_s": float(best["recovery_s"]),
        "estimated_latency_ms": float(best["latency_ms"]),
        "estimated_capacity_mbps": float(best["capacity_mbps"]),
        "estimated_energy_cost_j": float(best["energy_j"]),
        "estimated_privacy_cost": float(best["privacy_cost"]),
        "retained_service_features": list(best["retained"]),
        "suspended_service_features": list(best["suspended"]),
        "rejected_alternatives": rejected,
        "uncertainty": {
            "score": 0.5 if twin.get("evidence_level") == "synthetic" else 0.3,
            "notes": "Non-measured NTN parameters come from the assumption registry.",
        },
        "assumptions_used": assumptions_used,
        "runtime_s": float(time.perf_counter() - t0),
        "producer": {
            "repository": "ntn-resilience-sim",
            "commit": git_commit(),
        },
        "evidence_level": twin.get("evidence_level")
        if twin.get("evidence_level") in {"synthetic", "controlled_device_measurement", "mixed"}
        else "mixed",
        "deployable": deployable,
        "path_scores": {s["mode"]: s for s in scores},
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    mod.validate_document(
        bundle,
        schema_path,
        expected_schema_name="gunnchos.resilience_decision_bundle",
        enforce_privacy=False,
    )
    return bundle


def validate_decision(path: Path, schema_dir: Path | None = None) -> dict[str, Any]:
    schema_path = resolve_schema_dir(schema_dir)
    mod = load_validator(schema_path)
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    return mod.validate_document(
        doc,
        schema_path,
        expected_schema_name="gunnchos.resilience_decision_bundle",
        enforce_privacy=False,
    )


def run_sensitivity(
    twin_path: Path,
    airan_path: Path,
    *,
    schema_dir: Path | None = None,
) -> list[dict[str, Any]]:
    registry = load_assumption_registry()
    keys = [
        "ntn_latency_ms",
        "ntn_capacity_mbps",
        "ntn_availability",
        "handover_delay_s",
        "ntn_energy_cost_j",
        "terrestrial_outage_duration_s",
    ]
    rows = []
    base = decide(
        twin_path,
        airan_path,
        Path("/tmp/ntn_sens_base.json"),
        schema_dir=schema_dir,
    )
    rows.append(
        {
            "parameter": "baseline",
            "value": "",
            "selected_mode": base["selected_mode"],
            "continuity_score": base["continuity_score"],
            "estimated_latency_ms": base["estimated_latency_ms"],
        }
    )
    for key in keys:
        item = registry["assumptions"][key]
        low, high = item["range"]
        for label, value in (("low", low), ("high", high)):
            # mutate temp registry file
            reg = json.loads(json.dumps(registry))
            reg["assumptions"][key]["value"] = value
            tmp_reg = Path("/tmp") / f"assumption_{key}_{label}.yaml"
            tmp_reg.write_text(yaml.safe_dump(reg), encoding="utf-8")
            out = Path("/tmp") / f"ntn_sens_{key}_{label}.json"
            bundle = decide(
                twin_path,
                airan_path,
                out,
                schema_dir=schema_dir,
                assumption_registry_path=tmp_reg,
            )
            rows.append(
                {
                    "parameter": key,
                    "value": value,
                    "selected_mode": bundle["selected_mode"],
                    "continuity_score": bundle["continuity_score"],
                    "estimated_latency_ms": bundle["estimated_latency_ms"],
                }
            )
    # service-class requirements sensitivity via twin mutation
    twin = json.loads(twin_path.read_text(encoding="utf-8"))
    for budget in (50.0, 100.0, 300.0):
        doc = json.loads(json.dumps(twin))
        doc["service_demand"]["values"]["latency_budget_ms"] = budget
        if doc.get("user_demands"):
            doc["user_demands"][0]["latency_budget_ms"] = budget
        tmp_twin = Path("/tmp") / f"twin_latency_budget_{budget}.json"
        tmp_twin.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        # AI-RAN hash must match mutated twin — rebuild decision hash link by
        # rewriting airan input hash for sensitivity-only analysis.
        airan = json.loads(airan_path.read_text(encoding="utf-8"))
        airan["input_twin_state_hash"] = sha256_file(tmp_twin)
        tmp_airan = Path("/tmp") / f"airan_latency_budget_{budget}.json"
        tmp_airan.write_text(json.dumps(airan, indent=2) + "\n", encoding="utf-8")
        bundle = decide(tmp_twin, tmp_airan, Path("/tmp") / f"ntn_svc_{budget}.json", schema_dir=schema_dir)
        rows.append(
            {
                "parameter": "service_latency_budget_ms",
                "value": budget,
                "selected_mode": bundle["selected_mode"],
                "continuity_score": bundle["continuity_score"],
                "estimated_latency_ms": bundle["estimated_latency_ms"],
            }
        )
    return rows
