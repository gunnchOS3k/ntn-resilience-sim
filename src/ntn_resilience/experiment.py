"""RQ3 digital experiment engine: seeds, sweeps, recovery, compound failures.

All numeric radio/delay/capacity values come from documented assumptions or
scenario YAML. Outputs are labeled simulation — not operator KPIs.
"""
from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

from .channel_assumptions import (
    CONFIGURED_GEO_RTT_MS,
    MIN_SERVICE_DEFAULTS,
    SCENARIO_FAMILIES,
    assumption_value,
    load_registry,
)
from .claim_firewall import validate_claim_firewall
from .fallback_policy import POLICIES, PolicyName, select_policy_path
from .metrics import full_metric_bundle
from .scenario_loader import load_scenario
from .stats import (
    CI_SIM_VARIABILITY_WARNING,
    EVIDENCE_CLASS,
    mean_ci,
    paired_diff_ci,
)

EXPERIMENTS_DIR = Path(__file__).resolve().parents[2] / "configs" / "experiments"


@dataclass
class StepState:
    terrestrial_up: bool
    ntn_visible: bool
    power_up: bool
    path: str
    latency_ms: float | None
    capacity_mbps: float
    meets_min_service: bool


def list_experiments() -> list[str]:
    return sorted(p.stem for p in EXPERIMENTS_DIR.glob("*.yaml"))


def load_experiment(experiment_id: str) -> dict[str, Any]:
    path = EXPERIMENTS_DIR / f"{experiment_id}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("experiment_id") != experiment_id:
        raise ValueError(f"experiment_id mismatch in {path}")
    return data


def _sample_timeline(
    *,
    steps: int,
    rng: random.Random,
    terrestrial_outage_p: float,
    ntn_visibility: float,
    power_outage_p: float,
    compound: bool,
) -> list[dict[str, bool]]:
    out = []
    for _ in range(steps):
        terrestrial_up = rng.random() >= terrestrial_outage_p
        ntn_visible = rng.random() < ntn_visibility
        power_up = rng.random() >= power_outage_p
        if compound and not power_up:
            # Compound failure: power loss drops terrestrial radios; NTN terminal
            # may still be visible but is treated unavailable without power.
            terrestrial_up = False
            ntn_visible = False
        out.append(
            {
                "terrestrial_up": terrestrial_up,
                "ntn_visible": ntn_visible,
                "power_up": power_up,
            }
        )
    return out


def _path_kpis(
    path: str,
    *,
    terr_lat: float,
    ntn_lat: float,
    terr_cap: float,
    ntn_cap: float,
) -> tuple[float, float]:
    if path == "terrestrial":
        return terr_lat, terr_cap
    if path == "ntn":
        return ntn_lat, ntn_cap
    return float("inf"), 0.0


def recovery_steps(meets: list[bool]) -> int | None:
    """Steps from first min-service miss until min-service is restored."""
    try:
        first_miss = meets.index(False)
    except ValueError:
        return 0
    for i in range(first_miss + 1, len(meets)):
        if meets[i]:
            return i - first_miss
    return None


def simulate_run(
    *,
    policy: PolicyName,
    seed: int,
    steps: int = 48,
    terrestrial_outage_p: float = 0.1,
    ntn_visibility: float = 0.85,
    ntn_latency_ms: float = 40.0,
    ntn_capacity_mbps: float = 5.0,
    terrestrial_latency_ms: float = 25.0,
    terrestrial_capacity_mbps: float = 20.0,
    power_outage_p: float = 0.0,
    compound: bool = False,
    min_capacity_mbps: float = MIN_SERVICE_DEFAULTS["min_capacity_mbps"],
    max_latency_ms: float = MIN_SERVICE_DEFAULTS["max_latency_ms"],
) -> dict[str, Any]:
    rng = random.Random(seed)
    raw = _sample_timeline(
        steps=steps,
        rng=rng,
        terrestrial_outage_p=terrestrial_outage_p,
        ntn_visibility=ntn_visibility,
        power_outage_p=power_outage_p,
        compound=compound,
    )
    steps_out: list[StepState] = []
    for row in raw:
        path = select_policy_path(
            policy,
            terrestrial_up=row["terrestrial_up"],
            ntn_visible=row["ntn_visible"],
            terrestrial_capacity_mbps=terrestrial_capacity_mbps,
            ntn_capacity_mbps=ntn_capacity_mbps,
            terrestrial_latency_ms=terrestrial_latency_ms,
            ntn_latency_ms=ntn_latency_ms,
            min_capacity_mbps=min_capacity_mbps,
            max_latency_ms=max_latency_ms,
        )
        lat, cap = _path_kpis(
            path,
            terr_lat=terrestrial_latency_ms,
            ntn_lat=ntn_latency_ms,
            terr_cap=terrestrial_capacity_mbps,
            ntn_cap=ntn_capacity_mbps,
        )
        meets = path != "offline" and cap >= min_capacity_mbps and lat <= max_latency_ms
        steps_out.append(
            StepState(
                terrestrial_up=row["terrestrial_up"],
                ntn_visible=row["ntn_visible"],
                power_up=row["power_up"],
                path=path,
                latency_ms=lat if lat != float("inf") else None,  # type: ignore[arg-type]
                capacity_mbps=cap,
                meets_min_service=meets,
            )
        )
    offline = sum(1 for s in steps_out if s.path == "offline")
    uptime = 1.0 - offline / max(steps, 1)
    ntn_used = sum(1 for s in steps_out if s.path == "ntn")
    terr_down = sum(1 for s in steps_out if not s.terrestrial_up)
    fallback_ok = ntn_used / max(terr_down, 1)
    meets = [s.meets_min_service for s in steps_out]
    rec = recovery_steps(meets)
    finite_lat = [s.latency_ms for s in steps_out if s.latency_ms is not None]
    bundle = full_metric_bundle(uptime, min(1.0, fallback_ok), offline, steps, terrestrial_outage_p)
    return {
        "policy": policy,
        "seed": seed,
        "steps": steps,
        "compound_failure": compound,
        "uptime_fraction": round(uptime, 4),
        "min_service_fraction": round(sum(meets) / max(steps, 1), 4),
        "recovery_steps_to_min_service": rec,
        "mean_on_path_latency_ms": round(sum(finite_lat) / max(len(finite_lat), 1), 4) if finite_lat else None,
        "ntn_path_fraction": round(ntn_used / max(steps, 1), 4),
        "offline_steps": offline,
        "metrics": bundle,
        "parameters": {
            "terrestrial_outage_p": terrestrial_outage_p,
            "ntn_visibility": ntn_visibility,
            "ntn_latency_ms": ntn_latency_ms,
            "ntn_capacity_mbps": ntn_capacity_mbps,
            "terrestrial_latency_ms": terrestrial_latency_ms,
            "terrestrial_capacity_mbps": terrestrial_capacity_mbps,
            "power_outage_p": power_outage_p,
            "min_capacity_mbps": min_capacity_mbps,
            "max_latency_ms": max_latency_ms,
        },
        "evidence_status": "synthetic_simulation",
        "evidence_class": EVIDENCE_CLASS,
        "disclaimer": "research simulation only — not operator, emergency, or satellite service performance",
    }


def sweep_dimension(
    name: str,
    values: Iterable[float],
    base: dict[str, Any],
    policies: list[PolicyName] | PolicyName,
    seeds: list[int],
) -> list[dict[str, Any]]:
    policy_list: list[PolicyName]
    if isinstance(policies, str):
        policy_list = [policies]
    else:
        policy_list = list(policies)
    rows = []
    for value in values:
        params = dict(base)
        params[name] = value
        for policy in policy_list:
            for seed in seeds:
                run = simulate_run(policy=policy, seed=seed, **params)
                rows.append({"sweep": name, "sweep_value": value, **run})
    return rows


def _mean(xs: list[float]) -> float:
    return round(sum(xs) / max(len(xs), 1), 4)


def _aggregate_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    uptime = [r["uptime_fraction"] for r in runs]
    min_service = [r["min_service_fraction"] for r in runs]
    ntn_frac = [r["ntn_path_fraction"] for r in runs]
    offline = [float(r["offline_steps"]) for r in runs]
    recovery = [float(r["recovery_steps_to_min_service"]) for r in runs if r.get("recovery_steps_to_min_service") is not None]
    lat = [r["mean_on_path_latency_ms"] for r in runs if r.get("mean_on_path_latency_ms") is not None]
    up_ci = mean_ci(uptime)
    ms_ci = mean_ci(min_service)
    return {
        "n": len(runs),
        "mean_uptime": round(up_ci["mean"], 4),
        "std_uptime": round(up_ci["std"], 6),
        "ci95_uptime": {"low": up_ci["ci_low"], "high": up_ci["ci_high"]},
        "mean_min_service": round(ms_ci["mean"], 4),
        "std_min_service": round(ms_ci["std"], 6),
        "ci95_min_service": {"low": ms_ci["ci_low"], "high": ms_ci["ci_high"]},
        "mean_ntn_path_fraction": _mean(ntn_frac),
        "mean_offline_steps": _mean(offline),
        "mean_recovery_steps_to_min_service": _mean(recovery) if recovery else None,
        "mean_on_path_latency_ms": _mean(lat) if lat else None,
        "seed_min_service": min_service,
        "seed_uptime": uptime,
        "ci_method": "student_t_over_seed_means",
        "ci_warning": CI_SIM_VARIABILITY_WARNING,
        "evidence_class": EVIDENCE_CLASS,
    }


def _policy_stats_block(seed_runs: list[dict[str, Any]], baseline_runs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    agg = _aggregate_runs(seed_runs)
    block: dict[str, Any] = {
        **agg,
        "per_seed_primary": [
            {
                "seed": r["seed"],
                "min_service_fraction": r["min_service_fraction"],
                "uptime_fraction": r["uptime_fraction"],
                "recovery_steps_to_min_service": r["recovery_steps_to_min_service"],
                "offline_steps": r["offline_steps"],
            }
            for r in seed_runs
        ],
    }
    if baseline_runs is not None and len(baseline_runs) == len(seed_runs):
        # Align by seed order (callers use identical seed lists).
        t_ms = [r["min_service_fraction"] for r in seed_runs]
        b_ms = [r["min_service_fraction"] for r in baseline_runs]
        t_up = [r["uptime_fraction"] for r in seed_runs]
        b_up = [r["uptime_fraction"] for r in baseline_runs]
        block["paired_vs_terrestrial"] = {
            "min_service_fraction": paired_diff_ci(t_ms, b_ms),
            "uptime_fraction": paired_diff_ci(t_up, b_up),
        }
    return block


def serialize_decision_region_boundaries(grids: dict[str, Any], when: dict[str, Any]) -> dict[str, Any]:
    """Serialize regions where NTN helps / hurts / ties (offline-dominated under compound)."""
    return {
        "latency_x_visibility_n_cells": len(grids.get("latency_x_visibility") or []),
        "capacity_x_visibility_n_cells": len(grids.get("capacity_x_visibility") or []),
        "ntn_helps_count": when.get("n_cells_ntn_helps"),
        "ntn_hurts_count": when.get("n_cells_ntn_hurts_or_worse"),
        "ntn_tie_count": when.get("n_cells_tie"),
        "helps_examples": when.get("helps_examples"),
        "hurts_examples": when.get("hurts_examples"),
        "tie_examples": when.get("tie_examples"),
        "negative_result_rule": "Do not imply NTN always better; surface GEO/capacity/compound regions where terrestrial or offline wins.",
        "local_peer_not_in_paper_iii_engine": True,
        "evidence_class": EVIDENCE_CLASS,
    }


def decision_grids(
    spec: dict[str, Any],
    base: dict[str, Any],
    policies: list[PolicyName],
    seeds: list[int],
) -> dict[str, Any]:
    sweeps = spec.get("sweeps") or {}
    lats = list(sweeps.get("ntn_latency_ms") or [])
    vis = list(sweeps.get("ntn_visibility") or [])
    caps = list(sweeps.get("ntn_capacity_mbps") or [])
    grids: dict[str, list[dict[str, Any]]] = {"latency_x_visibility": [], "capacity_x_visibility": []}
    for lat in lats:
        for v in vis:
            cell_runs = []
            for policy in policies:
                runs = [
                    simulate_run(policy=policy, seed=seed, **{**base, "ntn_latency_ms": lat, "ntn_visibility": v})
                    for seed in seeds
                ]
                agg = _aggregate_runs(runs)
                cell_runs.append({"policy": policy, **agg})
                grids["latency_x_visibility"].append(
                    {"ntn_latency_ms": lat, "ntn_visibility": v, "policy": policy, **agg}
                )
            terr = next(c for c in cell_runs if c["policy"] == "terrestrial_baseline")
            for c in cell_runs:
                c["delta_min_service_vs_terrestrial"] = round(c["mean_min_service"] - terr["mean_min_service"], 4)
                c["ntn_helps"] = c["mean_min_service"] > terr["mean_min_service"] + 1e-12
    for cap in caps:
        for v in vis:
            cell_runs = []
            for policy in policies:
                runs = [
                    simulate_run(
                        policy=policy, seed=seed, **{**base, "ntn_capacity_mbps": cap, "ntn_visibility": v}
                    )
                    for seed in seeds
                ]
                agg = _aggregate_runs(runs)
                cell_runs.append({"policy": policy, **agg})
                grids["capacity_x_visibility"].append(
                    {"ntn_capacity_mbps": cap, "ntn_visibility": v, "policy": policy, **agg}
                )
    return grids


def summarize_when_ntn_helps(grids: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    rows = grids.get("latency_x_visibility") or []
    helps = []
    hurts = []
    ties = []
    for r in rows:
        if r["policy"] == "terrestrial_baseline":
            continue
        delta = r.get("delta_min_service_vs_terrestrial")
        if delta is None:
            terr = next(
                t
                for t in rows
                if t["policy"] == "terrestrial_baseline"
                and t.get("ntn_latency_ms") == r.get("ntn_latency_ms")
                and t.get("ntn_visibility") == r.get("ntn_visibility")
            )
            delta = round(r["mean_min_service"] - terr["mean_min_service"], 4)
            r["delta_min_service_vs_terrestrial"] = delta
            r["ntn_helps"] = delta > 1e-12
        record = {
            "policy": r["policy"],
            "ntn_latency_ms": r.get("ntn_latency_ms"),
            "ntn_visibility": r.get("ntn_visibility"),
            "mean_min_service": r["mean_min_service"],
            "delta_min_service_vs_terrestrial": r.get("delta_min_service_vs_terrestrial"),
        }
        if r.get("ntn_helps"):
            helps.append(record)
        elif (r.get("delta_min_service_vs_terrestrial") or 0) < -1e-12:
            hurts.append(record)
        else:
            ties.append(record)
    return {
        "n_cells_ntn_helps": len(helps),
        "n_cells_ntn_hurts_or_worse": len(hurts),
        "n_cells_tie": len(ties),
        "helps_examples": helps[:12],
        "hurts_examples": hurts[:12],
        "tie_examples": ties[:12],
        "hypothesis_ntn_always_better": False,
        "hypothesis_rejected": len(hurts) > 0 or len(ties) > 0,
    }


def compound_contrast(
    base: dict[str, Any],
    policies: list[PolicyName],
    seeds: list[int],
    power_p: float,
) -> list[dict[str, Any]]:
    rows = []
    for policy in policies:
        simple_runs = [
            simulate_run(policy=policy, seed=seed, **{**base, "compound": False, "power_outage_p": 0.0})
            for seed in seeds
        ]
        compound_runs = [
            simulate_run(policy=policy, seed=seed, **{**base, "compound": True, "power_outage_p": power_p})
            for seed in seeds
        ]
        simple = _aggregate_runs(simple_runs)
        compound = _aggregate_runs(compound_runs)
        rows.append(
            {
                "policy": policy,
                "simple": simple,
                "compound": compound,
                "delta_min_service_compound_minus_simple": round(
                    compound["mean_min_service"] - simple["mean_min_service"], 4
                ),
            }
        )
    return rows


def delay_class_contrast(
    base: dict[str, Any],
    policies: list[PolicyName],
    seeds: list[int],
    leo_latency: float,
) -> list[dict[str, Any]]:
    rows = []
    for policy in policies:
        leo = _aggregate_runs(
            [simulate_run(policy=policy, seed=seed, **{**base, "ntn_latency_ms": leo_latency}) for seed in seeds]
        )
        geo = _aggregate_runs(
            [
                simulate_run(policy=policy, seed=seed, **{**base, "ntn_latency_ms": CONFIGURED_GEO_RTT_MS})
                for seed in seeds
            ]
        )
        rows.append(
            {
                "policy": policy,
                "leo_tr38821": {"ntn_latency_ms": leo_latency, **leo},
                "geo_configured": {"ntn_latency_ms": CONFIGURED_GEO_RTT_MS, **geo},
                "geo_exceeds_max_latency": CONFIGURED_GEO_RTT_MS > float(base["max_latency_ms"]),
            }
        )
    return rows


def run_experiment(experiment_id: str, out_dir: Path | None = None) -> dict[str, Any]:
    spec = load_experiment(experiment_id)
    registry = load_registry()
    ntn_lat = assumption_value(registry, "ntn_latency_ms")
    ntn_cap = assumption_value(registry, "ntn_capacity_mbps")
    ntn_vis = assumption_value(registry, "ntn_availability")
    scenario = load_scenario(spec["scenario_id"]) if spec.get("scenario_id") else {}
    seeds = list(spec.get("seeds") or [1, 2, 7, 42])
    steps = int(spec.get("steps", 48))
    policies: list[PolicyName] = list(spec.get("policies") or list(POLICIES))
    min_cap = float(spec.get("min_capacity_mbps", MIN_SERVICE_DEFAULTS["min_capacity_mbps"]))
    max_lat = float(spec.get("max_latency_ms", MIN_SERVICE_DEFAULTS["max_latency_ms"]))
    terr_outage = float(spec.get("terrestrial_outage_p", scenario.get("outage_probability", 0.1)))
    compound = bool(spec.get("compound_failure", False))
    power_p = float(spec.get("power_outage_p", 0.2 if compound else 0.0))
    delay_class = spec.get("delay_class", "leo_tr38821")
    ntn_latency = CONFIGURED_GEO_RTT_MS if delay_class == "geo_configured" else float(ntn_lat["value"])
    base = {
        "steps": steps,
        "terrestrial_outage_p": terr_outage,
        "ntn_visibility": float(ntn_vis["value"]),
        "ntn_latency_ms": ntn_latency,
        "ntn_capacity_mbps": float(ntn_cap["value"]),
        "terrestrial_latency_ms": float(spec.get("terrestrial_latency_ms", 25.0)),
        "terrestrial_capacity_mbps": float(spec.get("terrestrial_capacity_mbps", 20.0)),
        "power_outage_p": power_p,
        "compound": compound,
        "min_capacity_mbps": min_cap,
        "max_latency_ms": max_lat,
    }
    policy_runs = []
    baseline_seed_runs: list[dict[str, Any]] | None = None
    for policy in policies:
        seed_runs = [simulate_run(policy=policy, seed=seed, **base) for seed in seeds]
        if policy == "terrestrial_baseline":
            baseline_seed_runs = seed_runs
        stats = _policy_stats_block(
            seed_runs,
            baseline_runs=None if policy == "terrestrial_baseline" else baseline_seed_runs,
        )
        policy_runs.append(
            {
                "policy": policy,
                "n_seeds": len(seeds),
                "mean_uptime": stats["mean_uptime"],
                "mean_min_service": stats["mean_min_service"],
                "statistics": stats,
                "runs": seed_runs,
            }
        )
    # Second pass for paired diffs if terrestrial was not first
    if baseline_seed_runs is None:
        for block in policy_runs:
            if block["policy"] == "terrestrial_baseline":
                baseline_seed_runs = block["runs"]
                break
    if baseline_seed_runs is not None:
        for block in policy_runs:
            if block["policy"] == "terrestrial_baseline":
                continue
            block["statistics"] = _policy_stats_block(block["runs"], baseline_runs=baseline_seed_runs)
    sweeps = {}
    if spec.get("sweeps"):
        for dim, values in spec["sweeps"].items():
            sweeps[dim] = sweep_dimension(dim, values, base, policies, seeds)
    grids = decision_grids(spec, base, policies, seeds) if spec.get("sweeps") else {}
    when = summarize_when_ntn_helps(grids) if grids else {}
    contrast = compound_contrast(base, policies, seeds, power_p)
    delay_rows = delay_class_contrast(base, policies, seeds, float(base["ntn_latency_ms"]))
    stress = []
    for cap in spec.get("stress_probes", {}).get("ntn_capacity_mbps") or []:
        for policy in policies:
            runs = [
                simulate_run(policy=policy, seed=seed, **{**base, "ntn_capacity_mbps": float(cap)})
                for seed in seeds
            ]
            stress.append(
                {
                    "probe": "ntn_capacity_below_or_near_min",
                    "ntn_capacity_mbps": float(cap),
                    "min_capacity_mbps": min_cap,
                    "policy": policy,
                    **_aggregate_runs(runs),
                    "below_min_capacity": float(cap) < min_cap,
                }
            )
    geo_adaptive = next((r for r in delay_rows if r["policy"] == "adaptive"), delay_rows[0] if delay_rows else {})
    geo_static = next((r for r in delay_rows if r["policy"] == "static_ntn"), {})
    geo_fallback = next((r for r in delay_rows if r["policy"] == "fallback"), {})
    leo_ms = geo_adaptive.get("leo_tr38821", {}).get("mean_min_service")
    geo_ms = geo_adaptive.get("geo_configured", {}).get("mean_min_service")
    terr_ms = next(p["mean_min_service"] for p in policy_runs if p["policy"] == "terrestrial_baseline")
    static_geo_ms = (geo_static.get("geo_configured") or {}).get("mean_min_service")
    fallback_geo_ms = (geo_fallback.get("geo_configured") or {}).get("mean_min_service")
    static_stress = next((r for r in stress if r["policy"] == "static_ntn"), {})
    fallback_stress = next((r for r in stress if r["policy"] == "fallback"), {})
    adaptive_stress = next((r for r in stress if r["policy"] == "adaptive"), {})
    static_geo_hurts = static_geo_ms is not None and static_geo_ms < terr_ms - 1e-12
    static_cap_hurts = static_stress.get("mean_min_service") is not None and static_stress["mean_min_service"] < terr_ms - 1e-12
    findings = {
        "ntn_always_better": False,
        "n_decision_cells_ntn_helps": when.get("n_cells_ntn_helps"),
        "n_decision_cells_ntn_worse": when.get("n_cells_ntn_hurts_or_worse"),
        "n_decision_cells_tie": when.get("n_cells_tie"),
        "compound_reduces_min_service": all(
            r["delta_min_service_compound_minus_simple"] <= 0 for r in contrast
        ),
        "geo_min_service_vs_leo_adaptive": {
            "leo": leo_ms,
            "geo_configured": geo_ms,
            "geo_worse_or_equal": (geo_ms is not None and leo_ms is not None and geo_ms <= leo_ms),
            "geo_rtt_ms": CONFIGURED_GEO_RTT_MS,
            "max_latency_ms": max_lat,
            "geo_exceeds_max_latency": CONFIGURED_GEO_RTT_MS > max_lat,
        },
        "when_ntn_does_not_help": {
            "static_ntn_geo_min_service": static_geo_ms,
            "fallback_geo_min_service": fallback_geo_ms,
            "terrestrial_min_service": terr_ms,
            "static_ntn_geo_worse_than_terrestrial": static_geo_hurts,
            "fallback_geo_equals_terrestrial": fallback_geo_ms == terr_ms,
            "static_ntn_low_capacity_min_service": static_stress.get("mean_min_service"),
            "fallback_low_capacity_min_service": fallback_stress.get("mean_min_service"),
            "adaptive_low_capacity_min_service": adaptive_stress.get("mean_min_service"),
            "static_ntn_low_capacity_worse_than_terrestrial": static_cap_hurts,
        },
        "hypothesis_rejected": bool(static_geo_hurts or static_cap_hurts or when.get("n_cells_ntn_hurts_or_worse")),
        "policy_mean_min_service": {p["policy"]: p["mean_min_service"] for p in policy_runs},
        "policy_mean_uptime": {p["policy"]: p["mean_uptime"] for p in policy_runs},
    }
    result = {
        "experiment_id": experiment_id,
        "research_question": spec.get("research_question", "RQ3"),
        "scenario_family": spec.get("scenario_family"),
        "scenario_families_catalog": list(SCENARIO_FAMILIES),
        "scenario_id": spec.get("scenario_id"),
        "delay_class": delay_class,
        "seeds": seeds,
        "assumptions_used": {
            "ntn_latency_ms": ntn_lat,
            "ntn_capacity_mbps": ntn_cap,
            "ntn_availability": ntn_vis,
            "geo_rtt_ms_configured": CONFIGURED_GEO_RTT_MS,
        },
        "policies": policy_runs,
        "sweeps": sweeps,
        "decision_grids": grids,
        "when_ntn_helps": when,
        "decision_region_boundaries": serialize_decision_region_boundaries(grids, when),
        "compound_contrast": contrast,
        "delay_class_contrast": delay_rows,
        "stress_probes": stress,
        "findings": findings,
        "non_claims": spec.get(
            "non_claims",
            [
                "Not operator performance",
                "Not University of Oulu affiliation",
                "Not a field NTN measurement",
            ],
        ),
        "evidence_status": "synthetic_simulation",
        "evidence_class": EVIDENCE_CLASS,
        "ci_warning": CI_SIM_VARIABILITY_WARNING,
        "ci_method": "student_t_over_seed_means",
    }
    result["claim_firewall"] = validate_claim_firewall(result)
    dest = out_dir or Path("results/experiments")
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"{experiment_id}.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    # Compact statistical table artifacts
    csv_path = dest / "rq3_statistical_report.csv"
    md_path = dest / "rq3_statistical_report.md"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "policy",
                "metric",
                "n",
                "mean",
                "std",
                "ci_low",
                "ci_high",
                "paired_mean_diff_vs_terr",
            ]
        )
        for block in policy_runs:
            st = block["statistics"]
            paired = (st.get("paired_vs_terrestrial") or {}).get("min_service_fraction") or {}
            w.writerow(
                [
                    block["policy"],
                    "min_service_fraction",
                    st["n"],
                    st["mean_min_service"],
                    st["std_min_service"],
                    st["ci95_min_service"]["low"],
                    st["ci95_min_service"]["high"],
                    paired.get("mean"),
                ]
            )
            w.writerow(
                [
                    block["policy"],
                    "uptime_fraction",
                    st["n"],
                    st["mean_uptime"],
                    st["std_uptime"],
                    st["ci95_uptime"]["low"],
                    st["ci95_uptime"]["high"],
                    ((st.get("paired_vs_terrestrial") or {}).get("uptime_fraction") or {}).get("mean"),
                ]
            )
    md_lines = [
        "# RQ3 statistical report (SYNTHETIC_SIM)",
        "",
        f"- seeds: `{seeds}`",
        f"- evidence_class: `{EVIDENCE_CLASS}`",
        f"- ci_method: student_t_over_seed_means",
        "",
        f"> {CI_SIM_VARIABILITY_WARNING}",
        "",
        "| policy | mean min_service | std | 95% CI | paired Δ vs terrestrial |",
        "|---|---:|---:|---|---:|",
    ]
    for block in policy_runs:
        st = block["statistics"]
        paired = (st.get("paired_vs_terrestrial") or {}).get("min_service_fraction") or {}
        ci = st["ci95_min_service"]
        md_lines.append(
            f"| {block['policy']} | {st['mean_min_service']:.4f} | {st['std_min_service']:.4f} | "
            f"[{ci['low']:.4f}, {ci['high']:.4f}] | {paired.get('mean', '')} |"
        )
    md_lines.append("")
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    result["wrote"] = str(path)
    result["statistical_artifacts"] = {"csv": str(csv_path), "md": str(md_path), "json": str(path)}
    return result
