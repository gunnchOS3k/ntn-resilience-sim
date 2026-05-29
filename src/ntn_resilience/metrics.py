def resilience_score(uptime_frac: float, fallback_success: float) -> float:
    return 0.7 * uptime_frac + 0.3 * fallback_success
