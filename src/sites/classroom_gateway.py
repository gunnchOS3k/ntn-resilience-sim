"""Classroom gateway model."""
from __future__ import annotations

from sites.edge_cache import edge_cache_simulation
from sites.link_budget import estimate_margin_db


def classroom_gateway(site_id: str) -> dict:
    lb = estimate_margin_db(site_id)
    cache = edge_cache_simulation(site_id)
    return {
        "site_id": site_id,
        "gateway": {
            "local_ap": True,
            "edge_cache": True,
            "ntn_fallback": lb["margin_db"] > 0,
        },
        "link_budget": lb,
        "cache": cache,
        "disclaimer": "research simulation only — not operational service",
    }
