"""Security tabletop scenario library."""
from __future__ import annotations

SCENARIOS = [
    "account_compromise",
    "local_ap_compromise",
    "malicious_data_injection",
    "corrupted_sensor_data",
    "gateway_power_loss",
    "misconfigured_access_control",
    "satellite_backup_outage",
    "privacy_leak",
    "public_dashboard_exposure",
    "sensitive_location_exposure",
]


def run_tabletop(site_id: str, scenario_id: str) -> dict:
    mitigations = {
        "sensitive_location_exposure": "No geo publish for Gaza; aggregate metrics only",
        "public_dashboard_exposure": "Privacy-first dashboards; no learner PII",
        "account_compromise": "MFA + staff segmentation",
    }
    return {
        "site_id": site_id,
        "scenario_id": scenario_id,
        "mitigation": mitigations.get(scenario_id, "Review access controls and incident plan"),
        "evidence_status": "design assumption",
    }
