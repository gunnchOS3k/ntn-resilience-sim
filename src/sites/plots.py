"""Plot helpers (text/table exports for tests)."""
from __future__ import annotations

from sites.metrics import compute_metrics


def metrics_table(site_ids: list[str]) -> list[dict]:
    return [compute_metrics(s) for s in site_ids]
