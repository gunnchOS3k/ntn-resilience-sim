"""NTN resilience simulation CLI (toy scenarios)."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .fallback_policy import select_path
from .metrics import full_metric_bundle
from .outage_model import simulate_outage_timeline
from .campus_reports import compare_policies, run_all_campus, run_campus, write_report
from .campus_scenarios import list_campus_scenarios
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


def cmd_decide(args: argparse.Namespace) -> int:
    from .gate2.decide import decide

    bundle = decide(
        Path(args.twin_state),
        Path(args.airan_decision),
        Path(args.output),
        policy_name=args.policy,
        schema_dir=Path(args.schema_dir) if args.schema_dir else None,
    )
    print(json.dumps({"wrote": args.output, "selected_mode": bundle["selected_mode"]}, indent=2))
    return 0


def cmd_validate_decision(args: argparse.Namespace) -> int:
    from .gate2.decide import validate_decision

    result = validate_decision(
        Path(args.path),
        schema_dir=Path(args.schema_dir) if args.schema_dir else None,
    )
    print(json.dumps(result, indent=2))
    return 0


def cmd_sensitivity(args: argparse.Namespace) -> int:
    import csv

    from .gate2.decide import run_sensitivity

    rows = run_sensitivity(
        Path(args.twin_state),
        Path(args.airan_decision),
        schema_dir=Path(args.schema_dir) if args.schema_dir else None,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(str(out))
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

    sub.add_parser("list-campus-scenarios").set_defaults(
        func=lambda a: [print(s) for s in list_campus_scenarios()] or 0
    )
    p_cr = sub.add_parser("run-campus")
    p_cr.add_argument("scenario_id")
    def _run_cr(a):
        print(json.dumps(run_campus(a.scenario_id), indent=2))
        write_report(a.scenario_id)
        return 0

    p_cr.set_defaults(func=_run_cr)
    sub.add_parser("run-all-campus").set_defaults(func=lambda a: run_all_campus() or 0)
    p_cmp = sub.add_parser("compare-policies")
    p_cmp.add_argument("scenario_id")
    p_cmp.set_defaults(func=lambda a: print(json.dumps(compare_policies(a.scenario_id), indent=2)) or 0)
    p_mcr = sub.add_parser("make-campus-report")
    p_mcr.add_argument("scenario_id")
    p_mcr.set_defaults(func=lambda a: write_report(a.scenario_id) or 0)

    # Gate 2
    p_dec = sub.add_parser("decide")
    p_dec.add_argument("--twin-state", required=True)
    p_dec.add_argument("--airan-decision", required=True)
    p_dec.add_argument("--output", required=True)
    p_dec.add_argument("--schema-dir", default=None)
    p_dec.add_argument("--policy", default="service_aware_multi_access")
    p_dec.set_defaults(func=cmd_decide)

    p_vd = sub.add_parser("validate-decision")
    p_vd.add_argument("path")
    p_vd.add_argument("--schema-dir", default=None)
    p_vd.set_defaults(func=cmd_validate_decision)

    p_sens = sub.add_parser("sensitivity")
    p_sens.add_argument("--twin-state", required=True)
    p_sens.add_argument("--airan-decision", required=True)
    p_sens.add_argument("--output", required=True)
    p_sens.add_argument("--schema-dir", default=None)
    p_sens.set_defaults(func=cmd_sensitivity)

    def _list_exp(_: argparse.Namespace) -> int:
        from .experiment import list_experiments

        for eid in list_experiments():
            print(eid)
        return 0

    def _run_exp(a: argparse.Namespace) -> int:
        from .experiment import run_experiment

        result = run_experiment(a.experiment_id)
        print(json.dumps({"wrote": result.get("wrote"), "experiment_id": result["experiment_id"]}, indent=2))
        return 0

    sub.add_parser("list-experiments").set_defaults(func=_list_exp)
    p_re = sub.add_parser("run-experiment")
    p_re.add_argument("experiment_id")
    p_re.set_defaults(func=_run_exp)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
