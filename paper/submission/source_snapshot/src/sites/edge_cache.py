"""Edge cache and offline continuity model."""
from __future__ import annotations

from sites.outage_model import outage_timeline
from sites.site_registry import get_site


def edge_cache_simulation(
    site_id: str,
    cache_hit_rate: float = 0.75,
    steps: int = 24,
    seed: int = 42,
) -> dict:
    site = get_site(site_id)
    if site_id == "gaza":
        cache_hit_rate = max(cache_hit_rate, 0.85)
    timeline = outage_timeline(site_id, steps=steps, seed=seed)
    continuity_scores = []
    for step in timeline:
        if step["path"] == "terrestrial":
            continuity_scores.append(1.0)
        elif step["path"] == "ntn":
            continuity_scores.append(0.7)
        elif step["path"] == "offline_cache":
            continuity_scores.append(cache_hit_rate)
        else:
            continuity_scores.append(0.2)
    return {
        "site_id": site_id,
        "cache_hit_rate": cache_hit_rate,
        "offline_continuity_score": round(sum(continuity_scores) / len(continuity_scores), 3),
        "lesson_continuity_score": round(sum(continuity_scores) / len(continuity_scores) * 0.9, 3),
        "evidence_status": "synthetic simulation",
    }
