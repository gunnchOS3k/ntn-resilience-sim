"""Campus resilience reports."""
import json
from pathlib import Path

from .campus_scenarios import list_campus_scenarios, load_campus_scenario
from .experiment import simulate_run
from .fallback_policy import POLICIES


def run_campus(scenario_id: str) -> dict:
    sc = load_campus_scenario(scenario_id)
    bad = sc["bad_day_assumptions"].get("terrestrial_up") is False
    outage_p = 0.15 if bad else 0.05
    vis = 0.7 if bad else 0.85
    run = simulate_run(
        policy="fallback",
        seed=42,
        steps=20,
        terrestrial_outage_p=outage_p,
        ntn_visibility=vis,
        compound=bad,
        power_outage_p=0.2 if bad else 0.0,
    )
    return {
        "scenario": sc,
        "metrics": run["metrics"],
        "simulation": {
            "uptime_fraction": run["uptime_fraction"],
            "min_service_fraction": run["min_service_fraction"],
            "recovery_steps_to_min_service": run["recovery_steps_to_min_service"],
            "policy": run["policy"],
        },
        "evidence_status": "synthetic_simulation",
        "needs_validation": sc.get("needs_validation", True),
        "disclaimer": run["disclaimer"],
    }


def compare_policies(scenario_id: str, seed: int = 42) -> dict:
    sc = load_campus_scenario(scenario_id)
    bad = sc["bad_day_assumptions"].get("terrestrial_up") is False
    outage_p = 0.15 if bad else 0.05
    vis = 0.7 if bad else 0.85
    policies = []
    for name in POLICIES:
        run = simulate_run(
            policy=name,
            seed=seed,
            steps=20,
            terrestrial_outage_p=outage_p,
            ntn_visibility=vis,
            compound=bad,
            power_outage_p=0.2 if bad else 0.0,
        )
        policies.append(
            {
                "name": name,
                "continuity": run["min_service_fraction"],
                "uptime_fraction": run["uptime_fraction"],
                "recovery_steps_to_min_service": run["recovery_steps_to_min_service"],
            }
        )
    return {
        "scenario_id": scenario_id,
        "policies": policies,
        "evidence_status": "synthetic_simulation",
        "disclaimer": "comparative simulation under documented assumptions — not operator KPIs",
    }


def write_report(scenario_id: str) -> None:
    out = Path("results/campus_resilience")
    out.mkdir(parents=True, exist_ok=True)
    run = run_campus(scenario_id)
    cmp = compare_policies(scenario_id)
    (out / f"{scenario_id}_metrics.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    (out / f"{scenario_id}_timeline.md").write_text(
        f"# Timeline — {scenario_id}\n\nEvidence: synthetic_simulation\n", encoding="utf-8"
    )
    (out / f"{scenario_id}_policy_comparison.md").write_text(
        f"# Policies\n\n```json\n{json.dumps(cmp, indent=2)}\n```\n", encoding="utf-8"
    )
    table = "| Policy | Continuity |\n|--------|------------|\n" + "\n".join(
        f"| {p['name']} | {p['continuity']} |" for p in cmp["policies"]
    )
    (out / f"{scenario_id}_conference_table.md").write_text(
        f"# Conference table\n\n{table}\n\n*Synthetic simulation under documented assumptions — not operator performance*\n",
        encoding="utf-8",
    )


def run_all_campus() -> None:
    for sid in list_campus_scenarios():
        write_report(sid)
