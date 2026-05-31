"""NTN resilience simulation CLI (toy scenarios)."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .fallback_policy import select_path
from .metrics import full_metric_bundle
from .outage_model import simulate_outage_timeline
from .scenario_loader import list_scenarios, load_scenario


def _run_toy(scenario_id: str, seed: int = 42) -> dict:
    cfg = load_scenario(scenario_id)
    rng = random.Random(seed)
    steps = 20
    timeline = simulate_outage_timeline(
        steps=steps,
        outage_probability=cfg.get("outage_probability", 0.1),
        rng=rng,
    )
    paths = [select_path(t["terrestrial_up"], cfg.get("ntn_fallback", False)) for t in timeline]
    uptime = sum(1 for p in paths if p != "offline") / len(paths)
    fallback_ok = sum(1 for p in paths if p == "ntn") / max(1, sum(1 for t in timeline if not t["terrestrial_up"]))
    offline = sum(1 for p in paths if p == "offline")
    metrics = full_metric_bundle(uptime, min(1.0, fallback_ok), offline, steps, cfg.get("outage_probability", 0.1))
    return {
        "scenario_id": scenario_id,
        "site_id": cfg.get("site_id"),
        "location_type": cfg.get("location_type"),
        "ethical_framing": cfg.get("ethical_framing"),
        **metrics,
        "uptime_fraction": round(uptime, 4),
        "paths_sample": paths[:5],
        "note": "simulation scaffold — not deployed NTN infrastructure",
    }


def _write_e2e(scenario_id: str, result: dict) -> None:
    e2e = Path("results/e2e")
    e2e.mkdir(parents=True, exist_ok=True)
    (e2e / f"{scenario_id}_resilience.md").write_text(
        f"# {scenario_id} resilience (toy)\n\n" + "\n".join(f"- **{k}**: {v}" for k, v in result.items()) + "\n",
        encoding="utf-8",
    )
    (e2e / f"{scenario_id}_metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def cmd_list(_: argparse.Namespace) -> int:
    for s in list_scenarios():
        print(s)
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    print(json.dumps(load_scenario(args.scenario_id), indent=2))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if not args.toy:
        raise SystemExit("Use --toy for synthetic run")
    result = _run_toy(args.scenario_id)
    print(json.dumps(result, indent=2))
    _write_e2e(args.scenario_id, result)
    print(f"Wrote results/e2e/{args.scenario_id}_resilience.md")
    return 0


def cmd_make_report(args: argparse.Namespace) -> int:
    result = _run_toy(args.scenario_id)
    card = [
        f"# NTN Research Card — {args.scenario_id}",
        "",
        f"**Ethical framing:** {result.get('ethical_framing', 'simulation only')}",
        "",
        "## Metrics",
    ] + [f"- **{k}**: {v}" for k, v in result.items() if k not in ("paths_sample",)] + [
        "",
        "## Limitation",
        result.get("note", ""),
    ]
    e2e = Path("results/e2e")
    e2e.mkdir(parents=True, exist_ok=True)
    path = e2e / "ntn_research_card.md"
    path.write_text("\n".join(card) + "\n", encoding="utf-8")
    _write_e2e(args.scenario_id, result)
    print(f"Wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list-scenarios").set_defaults(func=cmd_list)
    p_sum = sub.add_parser("summarize")
    p_sum.add_argument("scenario_id")
    p_sum.set_defaults(func=cmd_summarize)
    p_run = sub.add_parser("run")
    p_run.add_argument("scenario_id")
    p_run.add_argument("--toy", action="store_true")
    p_run.set_defaults(func=cmd_run)
    p_rep = sub.add_parser("make-report")
    p_rep.add_argument("scenario_id")
    p_rep.set_defaults(func=cmd_make_report)
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
