"""Resilience and continuity metrics (toy simulation)."""
from __future__ import annotations


def resilience_score(uptime_frac: float, fallback_success: float) -> float:
    return round(0.7 * uptime_frac + 0.3 * fallback_success, 4)


def service_continuity_score(uptime_frac: float) -> float:
    return round(uptime_frac, 4)


def recovery_score(fallback_success: float) -> float:
    return round(fallback_success, 4)


def unmet_demand_proxy(offline_steps: int, total_steps: int) -> float:
    return round(offline_steps / max(total_steps, 1), 4)


def latency_penalty_proxy(outage_probability: float) -> float:
    return round(min(1.0, outage_probability * 2), 4)


def full_metric_bundle(uptime: float, fallback_ok: float, offline_steps: int, steps: int, outage_p: float) -> dict:
    return {
        "resilience_score": resilience_score(uptime, fallback_ok),
        "service_continuity_score": service_continuity_score(uptime),
        "recovery_score": recovery_score(fallback_ok),
        "unmet_demand_proxy": unmet_demand_proxy(offline_steps, steps),
        "latency_penalty_proxy": latency_penalty_proxy(outage_p),
    }
