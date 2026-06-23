"""Generate resilience configs, docs, notebooks, and scenario results."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from sites.run_site_scenario import run_scenario
from sites.site_registry import SITE_IDS, get_site

ROOT = Path(__file__).resolve().parents[1]

TRAFFIC_CLASSES = [
    "safety_and_operations",
    "teacher_student_learning",
    "device_support_repair",
    "sensor_telemetry",
    "mentor_video",
    "bulk_dataset_sync",
]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_site_configs(site_id: str) -> None:
    site = get_site(site_id)
    base = ROOT / "configs" / "sites" / site_id
    configs = {
        "baseline.yaml": {
            "site_id": site_id,
            "seed": 42,
            "primary_path": site["primary_path"],
            "ntn_role": site["ntn_role"],
            "units": {"latency": "ms", "margin_db": "dB", "power": "W"},
            "evidence_status": "synthetic simulation",
            "disclaimer": "research simulation only — not operational service",
        },
        "outage_scenarios.yaml": {
            "site_id": site_id,
            "scenarios": ["normal", "bad_day", "worst_case", "recovery"],
        },
        "traffic_classes.yaml": {"site_id": site_id, "classes": TRAFFIC_CLASSES},
        "edge_cache.yaml": {
            "site_id": site_id,
            "enabled": True,
            "default_hit_rate": 0.85 if site.get("offline_first") else 0.75,
        },
        "security_scenarios.yaml": {
            "site_id": site_id,
            "scenarios": ["privacy_leak", "public_dashboard_exposure"],
        },
        "power_assumptions.yaml": {"site_id": site_id, "units": "W", "backup_hours": 4},
        "cost_assumptions.yaml": {"site_id": site_id, "units": "USD conceptual", "cost_per_gb": 1.0},
    }
    for name, data in configs.items():
        _write(base / name, yaml.dump(data, sort_keys=False))


def generate_site_docs(site_id: str) -> None:
    site = get_site(site_id)
    base = ROOT / "docs" / "sites" / site_id
    banner = "> Research simulation only — not operational carrier, emergency, satellite, or safety service.\n\n"
    if site.get("privacy_sensitive"):
        banner += "> Gaza: privacy, child protection, offline-first. No sensitive locations.\n\n"
    if site.get("conceptual_only"):
        banner += "> Graham Land: conceptual NTN sim only; no field operation claim.\n\n"

    for name, title in [
        ("README.md", f"{site['display_name']} Resilience"),
        ("_RESILIENCE_SPEC.md", "Resilience Spec"),
        ("_CONNECTIVITY_MODEL.md", "Connectivity Model"),
        ("_OUTAGE_SCENARIOS.md", "Outage Scenarios"),
        ("_EDGE_CACHE_MODEL.md", "Edge Cache Model"),
        ("_SECURITY_MODEL.md", "Security Model"),
        ("_VALIDATION_LIMITATIONS.md", "Validation Limitations"),
    ]:
        _write(base / name, f"# {title}\n\n{banner}Site: `{site_id}`\n")


def generate_canon_docs() -> None:
    base = ROOT / "docs" / "sites"
    _write(base / "README.md", "# 7GC Resilience Network Sites\n")
    for name in [
        "7GC_RESILIENCE_NETWORK_CANON.md",
        "7GC_LINK_BUDGET_AND_COVERAGE_GUIDE.md",
        "7GC_EDGE_CACHE_AND_OFFLINE_FIRST_GUIDE.md",
        "7GC_OUTAGE_SCENARIO_LIBRARY.md",
        "7GC_SECURITY_TABLETOP_LIBRARY.md",
        "7GC_VALIDATION_LIMITATIONS.md",
    ]:
        _write(base / name, f"# {name}\n\nSynthetic/conceptual simulations only.\n")


def generate_notebooks(site_id: str) -> None:
    base = ROOT / "notebooks" / "sites" / site_id
    notebooks = [
        "01_connectivity_baseline.ipynb",
        "02_outage_and_resilience.ipynb",
        "03_edge_cache_learning_continuity.ipynb",
        "04_security_tabletop.ipynb",
    ]
    for nb in notebooks:
        content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# {nb.replace('.ipynb','').replace('_',' ')} — {site_id}\n",
                        "Research simulation only — not operational service.\n",
                    ],
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "source": [
                        "import json, sys\n",
                        "sys.path.insert(0, 'src')\n",
                        f"from sites.run_site_scenario import run_scenario\n",
                        f"result = run_scenario('{site_id}')\n",
                        "print(json.dumps(result['metrics'], indent=2))\n",
                    ],
                    "outputs": [],
                    "execution_count": None,
                },
            ],
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        _write(base / nb, json.dumps(content, indent=2))


def generate_cross_repo() -> None:
    base = ROOT / "docs" / "7gc"
    for name in [
        "CROSS_REPO_HANDOFF.md",
        "7GC_MASTER_INDEX.md",
        "7GC_REPO_MAP.md",
        "7GC_EVIDENCE_MATRIX.md",
        "7GC_NON_CLAIM_POLICY.md",
        "7GC_SITE_COMPLETION_MATRIX.md",
    ]:
        _write(base / name, f"# {name}\n")
    for sid in SITE_IDS:
        _write(base / "sites" / sid / "CROSS_REPO_HANDOFF.md", f"# Handoff — {sid}\n")


def generate_all() -> None:
    generate_canon_docs()
    generate_cross_repo()
    for sid in SITE_IDS:
        generate_site_configs(sid)
        generate_site_docs(sid)
        generate_notebooks(sid)
        run_scenario(sid, ROOT / "configs" / "sites" / sid / "baseline.yaml")
    print(f"Generated resilience bundle for {len(SITE_IDS)} sites")


if __name__ == "__main__":
    generate_all()
