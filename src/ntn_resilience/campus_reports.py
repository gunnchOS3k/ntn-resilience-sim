"""Campus resilience reports."""
import json
from pathlib import Path

from .campus_scenarios import list_campus_scenarios, load_campus_scenario
from .metrics import full_metric_bundle


def run_campus(scenario_id: str) -> dict:
    sc = load_campus_scenario(scenario_id)
    bad = sc["bad_day_assumptions"].get("terrestrial_up") is False
    bundle = full_metric_bundle(0.65 if bad else 0.9, 0.7 if bad else 0.95, 3 if bad else 1, 20, 0.15 if bad else 0.05)
    return {
        "scenario": sc,
        "metrics": bundle,
        "evidence_status": "smoke_test_only",
        "needs_validation": sc.get("needs_validation", True),
    }


def compare_policies(scenario_id: str) -> dict:
    return {
        "scenario_id": scenario_id,
        "policies": [
            {"name": "terrestrial_only", "continuity": 0.4},
            {"name": "ntn_fallback", "continuity": 0.72},
            {"name": "priority_class", "continuity": 0.81},
        ],
        "evidence_status": "smoke_test_only",
    }


def write_report(scenario_id: str) -> None:
    out = Path("results/campus_resilience")
    out.mkdir(parents=True, exist_ok=True)
    run = run_campus(scenario_id)
    cmp = compare_policies(scenario_id)
    (out / f"{scenario_id}_metrics.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    (out / f"{scenario_id}_timeline.md").write_text(
        f"# Timeline — {scenario_id}\n\nEvidence: smoke_test_only\n", encoding="utf-8"
    )
    (out / f"{scenario_id}_policy_comparison.md").write_text(
        f"# Policies\n\n```json\n{json.dumps(cmp, indent=2)}\n```\n", encoding="utf-8"
    )
    table = "| Policy | Continuity |\n|--------|------------|\n" + "\n".join(
        f"| {p['name']} | {p['continuity']} |" for p in cmp["policies"]
    )
    (out / f"{scenario_id}_conference_table.md").write_text(
        f"# Conference table\n\n{table}\n\n*Smoke only — needs validation*\n", encoding="utf-8"
    )


def run_all_campus() -> None:
    for sid in list_campus_scenarios():
        write_report(sid)
