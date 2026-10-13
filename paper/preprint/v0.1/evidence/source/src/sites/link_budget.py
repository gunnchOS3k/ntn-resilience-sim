"""Link budget model for resilience simulations."""
from __future__ import annotations

from sites.site_registry import get_site


def estimate_margin_db(
    site_id: str,
    frequency_ghz: float = 12.0,
    distance_km: float = 500.0,
    eirp_dbw: float = 45.0,
    gt_dbk: float = 20.0,
) -> dict:
    """Synthetic link budget — not calibrated to live constellations."""
    site = get_site(site_id)
    fspl = 20 * __import__("math").log10(distance_km) + 20 * __import__("math").log10(frequency_ghz) + 92.45
    margin = eirp_dbw + gt_dbk - fspl - 10  # 10 dB implementation loss (assumption)
    if site_id == "graham_land":
        margin -= 5  # polar weather/obstruction assumption
    return {
        "site_id": site_id,
        "margin_db": round(margin, 2),
        "units": {"frequency_ghz": "GHz", "distance_km": "km", "margin_db": "dB"},
        "evidence_status": "synthetic simulation",
        "disclaimer": "research simulation only — not operational service",
    }
