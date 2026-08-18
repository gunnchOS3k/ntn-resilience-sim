"""RQ3 digital experiment engine: seeds, sweeps, recovery, compound failures.

All numeric radio/delay/capacity values come from documented assumptions or
scenario YAML. Outputs are labeled simulation — not operator KPIs.
"""
from __future__ import annotations

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
from .fallback_policy import POLICIES, PolicyName, select_policy_path
from .metrics import full_metric_bundle
from .scenario_loader import load_scenario

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
        "disclaimer": "research simulation only — not operator, emergency, or satellite service performance",
    }


def sweep_dimension(
    name: str,
    values: Iterable[float],
    base: dict[str, Any],
    policy: PolicyName,
    seeds: list[int],
) -> list[dict[str, Any]]:
    rows = []
    for value in values:
        params = dict(base)
        params[name] = value
        for seed in seeds:
            run = simulate_run(policy=policy, seed=seed, **params)
            rows.append({"sweep": name, "sweep_value": value, **run})
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
    for policy in policies:
        seed_runs = [simulate_run(policy=policy, seed=seed, **base) for seed in seeds]
        policy_runs.append(
            {
                "policy": policy,
                "n_seeds": len(seeds),
                "mean_uptime": round(sum(r["uptime_fraction"] for r in seed_runs) / len(seed_runs), 4),
                "mean_min_service": round(
                    sum(r["min_service_fraction"] for r in seed_runs) / len(seed_runs), 4
                ),
                "runs": seed_runs,
            }
        )
    sweeps = {}
    if spec.get("sweeps"):
        for dim, values in spec["sweeps"].items():
            sweeps[dim] = sweep_dimension(dim, values, base, policies[0], seeds)
    result = {
        "experiment_id": experiment_id,
        "research_question": spec.get("research_question", "RQ3"),
        "scenario_family": spec.get("scenario_family"),
        "scenario_families_catalog": list(SCENARIO_FAMILIES),
        "scenario_id": spec.get("scenario_id"),
        "delay_class": delay_class,
        "assumptions_used": {
            "ntn_latency_ms": ntn_lat,
            "ntn_capacity_mbps": ntn_cap,
            "ntn_availability": ntn_vis,
            "geo_rtt_ms_configured": CONFIGURED_GEO_RTT_MS if delay_class == "geo_configured" else None,
        },
        "policies": policy_runs,
        "sweeps": sweeps,
        "non_claims": spec.get(
            "non_claims",
            [
                "Not operator performance",
                "Not University of Oulu affiliation",
                "Not a field NTN measurement",
            ],
        ),
        "evidence_status": "synthetic_simulation",
    }
    dest = out_dir or Path("results/experiments")
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"{experiment_id}.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    result["wrote"] = str(path)
    return result
