"""Site registry for resilience network simulations."""
from __future__ import annotations

SITE_IDS = ["gary", "ghana", "guyana", "gaza", "geelong", "graham_land", "germany"]

SITE_PROFILES = {
    "gary": {
        "display_name": "WAIKE Gary UPNOW",
        "primary_path": "urban_edge_ai_ran",
        "ntn_role": "emergency_fallback",
        "offline_first": False,
    },
    "ghana": {
        "display_name": "WAIKE Ghana UPNOW",
        "primary_path": "mobile_first",
        "ntn_role": "optional_satellite_backhaul",
        "offline_first": False,
    },
    "guyana": {
        "display_name": "WAIKE Guyana UPNOW",
        "primary_path": "flood_resilient_terrestrial",
        "ntn_role": "interior_fallback",
        "offline_first": False,
    },
    "gaza": {
        "display_name": "WAIKE Gaza UPNOW",
        "primary_path": "offline_first_humanitarian",
        "ntn_role": "conceptual_fallback_only",
        "offline_first": True,
        "privacy_sensitive": True,
    },
    "geelong": {
        "display_name": "WAIKE Geelong UPNOW",
        "primary_path": "coastal_industrial_edge",
        "ntn_role": "backup_extension",
        "offline_first": False,
    },
    "graham_land": {
        "display_name": "WAIKE Graham Land UPNOW",
        "primary_path": "ntn_primary",
        "ntn_role": "deep_ntn_polar_model",
        "offline_first": True,
        "conceptual_only": True,
    },
    "germany": {
        "display_name": "WAIKE Germany UPNOW",
        "primary_path": "industrial_segmented",
        "ntn_role": "limited_emergency",
        "offline_first": False,
    },
}


def get_site(site_id: str) -> dict:
    if site_id not in SITE_PROFILES:
        raise KeyError(site_id)
    return {"site_id": site_id, **SITE_PROFILES[site_id]}
