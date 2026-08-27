"""Student-t CI helpers for RQ3 seed-wise statistical parity (stdlib only).

CIs quantify simulation-run variability across seeds, NOT operator RF uncertainty.
"""
from __future__ import annotations

import math
from typing import Any

T_CRIT_975 = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    20: 2.086,
    30: 2.042,
    60: 2.000,
    120: 1.980,
}

CI_SIM_VARIABILITY_WARNING = (
    "95% Student-t CIs quantify simulation-run variability across seeds, "
    "NOT real-world RF or operator performance uncertainty."
)

EVIDENCE_CLASS = "SYNTHETIC_SIM"
MIN_SAMPLE_N = 2


def t_crit_975(df: int) -> float:
    if df <= 0:
        return float("nan")
    if df in T_CRIT_975:
        return T_CRIT_975[df]
    return 1.96


def assert_finite(values: list[float], *, label: str = "values") -> None:
    for i, v in enumerate(values):
        if v is None:
            continue
        if not math.isfinite(float(v)):
            raise ValueError(f"{label}[{i}] is not finite: {v!r}")


def mean_ci(values: list[float], level: float = 0.95) -> dict[str, float]:
    arr = [float(v) for v in values]
    assert_finite(arr)
    n = len(arr)
    if n == 0:
        return {
            "n": 0,
            "mean": float("nan"),
            "std": float("nan"),
            "ci_low": float("nan"),
            "ci_high": float("nan"),
        }
    m = float(sum(arr) / n)
    if n == 1:
        return {"n": 1, "mean": m, "std": 0.0, "ci_low": m, "ci_high": m}
    var = sum((x - m) ** 2 for x in arr) / (n - 1)
    sd = math.sqrt(var)
    _ = level
    half = t_crit_975(n - 1) * sd / math.sqrt(n)
    return {"n": n, "mean": m, "std": sd, "ci_low": m - half, "ci_high": m + half}


def cohens_d(a: list[float], b: list[float]) -> float:
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va = sum((x - ma) ** 2 for x in a) / (len(a) - 1)
    vb = sum((x - mb) ** 2 for x in b) / (len(b) - 1)
    pooled = math.sqrt(((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2))
    if pooled == 0:
        return 0.0
    return (ma - mb) / pooled


def paired_diff_ci(treatment: list[float], baseline: list[float]) -> dict[str, Any]:
    if len(treatment) != len(baseline):
        raise ValueError("paired_diff_ci requires equal-length seed-aligned series")
    diffs = [float(t) - float(b) for t, b in zip(treatment, baseline)]
    stats = mean_ci(diffs)
    return {
        **stats,
        "diffs": diffs,
        "cohens_d_vs_baseline": cohens_d(treatment, baseline),
        "paired": True,
    }
