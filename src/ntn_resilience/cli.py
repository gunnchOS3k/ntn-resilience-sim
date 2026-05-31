"""NTN resilience simulation CLI (toy scenarios)."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .fallback_policy import select_path
from .metrics import resilience_score
from .outage_model import simulate_outage_timeline
from .scenario_loader import list_scenarios, load_scenario


def _run_toy(scenario_id: str, seed: int = 42) -> dict:
    cfg = load_scenario(scenario_id)
    rng = random.Random(seed)
    timeline = simulate_outage_timeline(
        steps=20,
        outage_probability=cfg.get("outage_probability", 0.1),
        rng=rng,
    )
    paths = [
        select_path(t["terrestrial_up"], cfg.get("ntn_fallback", False))
        for t in timeline
    ]
    uptime = sum(1 for p in paths if p != "offline") / len(paths)
    fallback_ok = sum(1 for p in paths if p == "ntn") / max(1, sum(1 for t in timeline if not t["terrestrial_up"]))
    return {
        "scenario_id": scenario_id,
        "site_id": cfg.get("site_id"),
        "resilience_score": round(resilience_score(uptime, min(1.0, fallback_ok)), 4),
        "uptime_fraction": round(uptime, 4),
        "paths_sample": paths[:5],
        "note": "simulation scaffold — not deployed NTN infrastructure",
    }


def cmd_list(_: argparse.Namespace) -> int:
    for s in list_scenarios():
        print(s)
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    cfg = load_scenario(args.scenario_id)
    print(json.dumps(cfg, indent=2))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if not args.toy:
        raise SystemExit("Use --toy for synthetic run")
    result = _run_toy(args.scenario_id)
    print(json.dumps(result, indent=2))
    e2e = Path("results") / "e2e"
    e2e.mkdir(parents=True, exist_ok=True)
    md = e2e / f"{args.scenario_id}_resilience.md"
    md.write_text(
        f"# {args.scenario_id} resilience (toy)\n\n"
        + "\n".join(f"- **{k}**: {v}" for k, v in result.items())
        + "\n",
        encoding="utf-8",
    )
    (e2e / f"{args.scenario_id}_run.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {md}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-scenarios")
    p_list.set_defaults(func=cmd_list)

    p_sum = sub.add_parser("summarize")
    p_sum.add_argument("scenario_id")
    p_sum.set_defaults(func=cmd_summarize)

    p_run = sub.add_parser("run")
    p_run.add_argument("scenario_id")
    p_run.add_argument("--toy", action="store_true")
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
