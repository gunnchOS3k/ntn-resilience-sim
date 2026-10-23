"""Separate current outage truth from a delayed observation.

The seeded timeline in ``experiment.py`` still applies the current step's
outage draw. This helper is the firewall for a caller that also has a stale
link report. A delayed "up" observation does not clear a current outage.
Evidence class remains synthetic simulation.
"""
from __future__ import annotations


def reported_link_up(
    *,
    terrestrial_outage: bool,
    observation_says_up: bool,
    observation_delay_steps: int,
) -> dict:
    if observation_delay_steps < 0:
        raise ValueError("observation_delay_steps must be >= 0")
    current_truth_up = not bool(terrestrial_outage)
    observation_is_current = observation_delay_steps == 0
    reported_up = observation_says_up if observation_is_current else current_truth_up
    return {
        "current_truth_up": current_truth_up,
        "observation_says_up": bool(observation_says_up),
        "observation_delay_steps": observation_delay_steps,
        "observation_is_current_truth": observation_is_current,
        "reported_up": reported_up,
        "evidence_class": "SYNTHETIC_SIM",
    }
