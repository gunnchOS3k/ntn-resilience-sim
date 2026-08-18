"""Fallback policies for terrestrial / NTN path selection.

Policies are comparative simulation rules. They are not operator-performance claims.
"""
from __future__ import annotations

from typing import Literal

PathName = Literal["terrestrial", "ntn", "offline"]
PolicyName = Literal["terrestrial_baseline", "static_ntn", "fallback", "adaptive"]

POLICIES: tuple[PolicyName, ...] = (
    "terrestrial_baseline",
    "static_ntn",
    "fallback",
    "adaptive",
)


def select_path(terrestrial_up: bool, ntn_available: bool) -> str:
    """Historical two-input fallback (kept for CLI toy path)."""
    if terrestrial_up:
        return "terrestrial"
    return "ntn" if ntn_available else "offline"


def select_policy_path(
    policy: PolicyName,
    *,
    terrestrial_up: bool,
    ntn_visible: bool,
    terrestrial_capacity_mbps: float,
    ntn_capacity_mbps: float,
    terrestrial_latency_ms: float,
    ntn_latency_ms: float,
    min_capacity_mbps: float,
    max_latency_ms: float,
) -> PathName:
    terr_ok = terrestrial_up
    ntn_ok = ntn_visible
    if policy == "terrestrial_baseline":
        return "terrestrial" if terr_ok else "offline"
    if policy == "static_ntn":
        if ntn_ok:
            return "ntn"
        return "terrestrial" if terr_ok else "offline"
    if policy == "fallback":
        if terr_ok:
            return "terrestrial"
        return "ntn" if ntn_ok else "offline"
    # adaptive: among available paths meeting min-service, pick lower latency;
    # if none meet min-service, pick any available path (still may be degraded).
    candidates: list[tuple[PathName, float, float]] = []
    if terr_ok:
        candidates.append(("terrestrial", terrestrial_latency_ms, terrestrial_capacity_mbps))
    if ntn_ok:
        candidates.append(("ntn", ntn_latency_ms, ntn_capacity_mbps))
    if not candidates:
        return "offline"
    qualifying = [
        c for c in candidates if c[2] >= min_capacity_mbps and c[1] <= max_latency_ms
    ]
    pool = qualifying or candidates
    pool.sort(key=lambda c: (c[1], -c[2]))
    return pool[0][0]
