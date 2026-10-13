"""CLI entry: run site resilience scenario."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from sites.classroom_gateway import classroom_gateway
from sites.metrics import compute_metrics
from sites.site_registry import SITE_IDS


def run_scenario(site_id: str, config_path: Path | None = None) -> dict:
    if site_id not in SITE_IDS:
        raise ValueError(f"Unknown site: {site_id}")
    config = {}
    if config_path and config_path.exists():
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    seed = config.get("seed", 42)
    metrics = compute_metrics(site_id, seed=seed)
    gateway = classroom_gateway(site_id)
    result = {
        "site_id": site_id,
        "config": config,
        "metrics": metrics,
        "gateway": gateway,
    }
    out = Path("results/site_scenarios") / site_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "scenario_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 7GC site resilience scenario")
    parser.add_argument("--site", required=True, choices=SITE_IDS)
    parser.add_argument("--config", type=Path, default=None)
    args = parser.parse_args()
    config = args.config or Path(f"configs/sites/{args.site}/baseline.yaml")
    result = run_scenario(args.site, config)
    print(json.dumps({"site_id": result["site_id"], "resilience_score": result["metrics"]["resilience_score"]}))


if __name__ == "__main__":
    main()
