"""Store-and-forward delay model."""
from __future__ import annotations


def store_forward_delay(
    payload_kb: float,
    uplink_kbps: float,
    window_hours: float = 4.0,
) -> dict:
    if uplink_kbps <= 0:
        return {"delay_hours": window_hours, "delivered": False, "evidence_status": "synthetic simulation"}
    transmit_hours = (payload_kb * 8) / (uplink_kbps * 3600)
    return {
        "delay_hours": round(min(transmit_hours, window_hours), 3),
        "delivered": transmit_hours <= window_hours,
        "units": {"payload_kb": "kB", "uplink_kbps": "kbps", "delay_hours": "hours"},
        "evidence_status": "synthetic simulation",
    }
