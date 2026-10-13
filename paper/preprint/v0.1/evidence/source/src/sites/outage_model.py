"""Outage and resilience timeline model."""
from __future__ import annotations

import random
from typing import Any

from sites.site_registry import get_site


def outage_timeline(
    site_id: str,
    steps: int = 24,
    seed: int = 42,
    terrestrial_outage_prob: float | None = None,
) -> list[dict[str, Any]]:
    site = get_site(site_id)
    rng = random.Random(seed)
    defaults = {
        "gary": 0.08,
        "ghana": 0.12,
        "guyana": 0.18,
        "gaza": 0.35,
        "geelong": 0.07,
        "graham_land": 0.25,
        "germany": 0.06,
    }
    p = terrestrial_outage_prob if terrestrial_outage_prob is not None else defaults.get(site_id, 0.1)
    timeline = []
    for t in range(steps):
        terrestrial_up = rng.random() > p
        ntn_available = site_id == "graham_land" or (not terrestrial_up and rng.random() > 0.3)
        timeline.append(
            {
                "step": t,
                "terrestrial_up": terrestrial_up,
                "ntn_available": ntn_available,
                "path": _select_path(site_id, terrestrial_up, ntn_available),
            }
        )
    return timeline


def _select_path(site_id: str, terrestrial_up: bool, ntn_available: bool) -> str:
    site = get_site(site_id)
    if site.get("offline_first") and not terrestrial_up and not ntn_available:
        return "offline_cache"
    if terrestrial_up:
        return "terrestrial"
    if ntn_available:
        return "ntn"
    return "offline"
