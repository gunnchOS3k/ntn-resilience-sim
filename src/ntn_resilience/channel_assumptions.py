"""Documented channel/network assumptions for digital NTN experiments.

Values are literature-backed or configured ranges from
`config/assumption_registry.yaml`. They are **not** operator measurements.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "config" / "assumption_registry.yaml"

# GEO RTT planning envelope (configured, not TR-backed LEO). Used only when
# experiment family requests geo-class delay. Labeled separately from LEO.
CONFIGURED_GEO_RTT_MS = 550.0

SCENARIO_FAMILIES = (
    "urban_emergency",
    "rural_backhaul",
    "flood_disruption",
    "remote_first",
    "polar_visibility",
    "compound_failure",
)

MIN_SERVICE_DEFAULTS = {
    "min_capacity_mbps": 1.0,
    "max_latency_ms": 500.0,
}


def load_registry(path: Path | None = None) -> dict[str, Any]:
    cfg = path or REGISTRY_PATH
    return yaml.safe_load(cfg.read_text(encoding="utf-8"))


def assumption_value(registry: dict[str, Any], key: str) -> dict[str, Any]:
    item = registry["assumptions"][key]
    return {
        "key": key,
        "value": item["value"],
        "unit": item["unit"],
        "range": item["range"],
        "assumption_class": item["assumption_class"],
        "source_id": item.get("source_id"),
        "notes": item.get("notes", "").strip(),
    }
