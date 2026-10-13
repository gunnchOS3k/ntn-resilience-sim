"""Coverage model using AP placement, not wall leakage."""
from __future__ import annotations

from sites.site_registry import get_site


def coverage_zones(site_id: str, num_zones: int = 8) -> dict:
    site = get_site(site_id)
    zones = [
        {
            "zone_id": f"zone_{i+1}",
            "ap_indoor": True,
            "wired_backhaul": True,
            "rely_on_wall_leakage": False,
        }
        for i in range(num_zones)
    ]
    return {
        "site_id": site_id,
        "zones": zones,
        "primary_path": site["primary_path"],
        "evidence_status": "design assumption",
    }
