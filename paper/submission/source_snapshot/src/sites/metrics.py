"""Resilience metrics bundle."""
from __future__ import annotations

from sites.edge_cache import edge_cache_simulation
from sites.link_budget import estimate_margin_db
from sites.outage_model import outage_timeline
from sites.site_registry import get_site


def compute_metrics(site_id: str, seed: int = 42) -> dict:
    site = get_site(site_id)
    timeline = outage_timeline(site_id, seed=seed)
    cache = edge_cache_simulation(site_id, seed=seed)
    lb = estimate_margin_db(site_id)
    up_steps = sum(1 for s in timeline if s["path"] != "offline")
    latencies = {"terrestrial": 25, "ntn": 550, "offline_cache": 5, "offline": 0}
    avg_lat = sum(latencies[s["path"]] for s in timeline) / len(timeline)
    p95 = sorted(latencies[s["path"]] for s in timeline)[int(0.95 * len(timeline)) - 1]

    privacy_risk = 0.8 if site.get("privacy_sensitive") else 0.2

    return {
        "site_id": site_id,
        "link_availability": round(up_steps / len(timeline), 3),
        "average_latency_ms": round(avg_lat, 1),
        "p95_latency_ms": p95,
        "packet_delivery_ratio": round(0.85 + 0.1 * (up_steps / len(timeline)), 3),
        "store_forward_delay_hours": 2.5 if site_id == "graham_land" else 0.5,
        "cache_hit_rate": cache["cache_hit_rate"],
        "lesson_continuity_score": cache["lesson_continuity_score"],
        "outage_recovery_time_steps": 2,
        "energy_aware_uptime": round(up_steps / len(timeline) * 0.95, 3),
        "cost_per_learning_hour_conceptual": 1.0,
        "resilience_score": round(cache["offline_continuity_score"] * 0.6 + (up_steps / len(timeline)) * 0.4, 3),
        "offline_continuity_score": cache["offline_continuity_score"],
        "privacy_risk_score": privacy_risk,
        "community_benefit_continuity_score": round(cache["lesson_continuity_score"] * 0.9, 3),
        "link_margin_db": lb["margin_db"],
        "units": {
            "latency": "ms",
            "link_margin_db": "dB",
            "scores": "0-1 normalized",
        },
        "evidence_status": "synthetic simulation",
        "disclaimer": "research simulation only — not operational carrier, emergency, satellite, or safety service",
    }
