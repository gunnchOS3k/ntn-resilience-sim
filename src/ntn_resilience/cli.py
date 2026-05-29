"""NTN resilience CLI."""
import argparse
import json
import sys
from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parents[2] / "configs" / "scenarios"


def list_scenarios() -> None:
    for p in sorted(CONFIG.glob("*.yaml")):
        print(p.stem)


def summarize(scenario_id: str) -> None:
    data = yaml.safe_load((CONFIG / f"{scenario_id}.yaml").read_text())
    print(json.dumps(data, indent=2))


def run_scenario(scenario_id: str, toy: bool) -> None:
    from ntn_resilience.outage_model import sample_outage
    from ntn_resilience.fallback_policy import select_path
    from ntn_resilience.metrics import resilience_score

    data = yaml.safe_load((CONFIG / f"{scenario_id}.yaml").read_text())
    p = float(data.get("outage_probability", 0.1))
    terrestrial_up = not sample_outage(p, rng=__import__("random").Random(42))
    path = select_path(terrestrial_up, data.get("ntn_fallback", True))
    score = resilience_score(0.9 if terrestrial_up else 0.4, 0.7 if path == "ntn" else 0.0)
    out = {"scenario": scenario_id, "path": path, "resilience_score_toy": score, "toy": toy}
    Path("results").mkdir(exist_ok=True)
    Path(f"results/{scenario_id}_toy.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list-scenarios")
    s = sub.add_parser("summarize")
    s.add_argument("scenario_id")
    r = sub.add_parser("run")
    r.add_argument("scenario_id")
    r.add_argument("--toy", action="store_true")
    args = p.parse_args()
    if args.cmd == "list-scenarios":
        list_scenarios()
    elif args.cmd == "summarize":
        summarize(args.scenario_id)
    elif args.cmd == "run":
        run_scenario(args.scenario_id, args.toy)


if __name__ == "__main__":
    main()
