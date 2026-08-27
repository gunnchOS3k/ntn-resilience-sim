"""Student-t CI helpers for RQ3 seed-wise statistical parity (stdlib only).

CIs quantify simulation-run variability across seeds, NOT operator RF uncertainty.

Trusted verification source (development): SciPy 1.18.0 ``scipy.stats.t.ppf(0.975, df)``
(cross-checked to published two-sided 95% Student-t critical values). SciPy is NOT a
runtime dependency of this module; tabulated/interpolated values are embedded below.
"""
from __future__ import annotations

import math
from typing import Any

# Two-sided 95% critical values P(|T_df| > t) = 0.05 ⇔ t = F^{-1}_{t_df}(0.975).
# Source: SciPy 1.18.0 scipy.stats.t.ppf(0.975, df), rounded to 10 decimals.
T_CRIT_975: dict[int, float] = {
    1: 12.7062047362,
    2: 4.3026527297,
    3: 3.1824463053,
    4: 2.7764451052,
    5: 2.5705818356,
    6: 2.4469118511,
    7: 2.3646242516,
    8: 2.3060041352,
    9: 2.2621571628,
    10: 2.2281388520,
    11: 2.2009851601,
    12: 2.1788128297,
    13: 2.1603686565,
    14: 2.1447866879,
    15: 2.1314495456,
    16: 2.1199052992,
    17: 2.1098155778,
    18: 2.1009220402,
    19: 2.0930240544,
    20: 2.0859634473,
    21: 2.0796138447,
    22: 2.0738730679,
    23: 2.0686576104,
    24: 2.0638985616,
    25: 2.0595385528,
    26: 2.0555294386,
    27: 2.0518305165,
    28: 2.0484071418,
    29: 2.0452296421,
    30: 2.0422724563,
    40: 2.0210753903,
    60: 2.0002978220,
    120: 1.9799304051,
}

_Z_975 = 1.959963984540054

CI_SIM_VARIABILITY_WARNING = (
    "95% Student-t CIs quantify simulation-run variability across seeds, "
    "NOT real-world RF or operator performance uncertainty."
)

EVIDENCE_CLASS = "SYNTHETIC_SIM"
MIN_SAMPLE_N = 2
SUPPORTED_CI_LEVEL = 0.95
T_CRIT_VERIFICATION_SOURCE = (
    "SciPy 1.18.0 scipy.stats.t.ppf(0.975, df); stdlib table + 1/df interpolation "
    "+ Cornish–Fisher for df>120 (no silent 1.96 substitution for finite missing df)"
)


def t_crit_975(df: int) -> float:
    """Two-sided 95% Student-t critical value for the given degrees of freedom.

    Never silently substitutes the normal 1.96 quantile for a finite df that is
    absent from the lookup table.
    """
    if df <= 0:
        raise ValueError(f"degrees of freedom must be positive, got {df}")
    if df in T_CRIT_975:
        return T_CRIT_975[df]
    keys = sorted(T_CRIT_975)
    if df > keys[-1]:
        z = _Z_975
        inv = 1.0 / float(df)
        return float(
            z
            + (z**3 + z) * inv / 4.0
            + (5.0 * z**5 + 16.0 * z**3 + 3.0 * z) * inv * inv / 96.0
        )
    lo = max(k for k in keys if k < df)
    hi = min(k for k in keys if k > df)
    w = (1.0 / df - 1.0 / lo) / (1.0 / hi - 1.0 / lo)
    return float(T_CRIT_975[lo] + w * (T_CRIT_975[hi] - T_CRIT_975[lo]))


def assert_finite(values: list[float], *, label: str = "values") -> None:
    for i, v in enumerate(values):
        if v is None:
            continue
        if not math.isfinite(float(v)):
            raise ValueError(f"{label}[{i}] is not finite: {v!r}")


def mean_ci(values: list[float], level: float = SUPPORTED_CI_LEVEL) -> dict[str, float]:
    """Mean with Student-t CI. Only level=0.95 is supported."""
    if abs(float(level) - SUPPORTED_CI_LEVEL) > 1e-15:
        raise ValueError(
            f"Only confidence level {SUPPORTED_CI_LEVEL} is supported; got {level}. "
            "Refusing to silently reuse the 95% t table for other levels."
        )
    arr = [float(v) for v in values]
    assert_finite(arr)
    n = len(arr)
    nan = float("nan")
    if n == 0:
        return {"n": 0, "mean": nan, "std": nan, "ci_low": nan, "ci_high": nan}
    m = float(sum(arr) / n)
    if n < MIN_SAMPLE_N:
        return {"n": n, "mean": m, "std": nan, "ci_low": nan, "ci_high": nan}
    var = sum((x - m) ** 2 for x in arr) / (n - 1)
    sd = math.sqrt(var)
    half = t_crit_975(n - 1) * sd / math.sqrt(n)
    return {"n": n, "mean": m, "std": sd, "ci_low": m - half, "ci_high": m + half}


def cohens_d(a: list[float], b: list[float]) -> float:
    """Unpaired pooled-SD Cohen's d. Do not use for paired seed-wise contrasts."""
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va = sum((x - ma) ** 2 for x in a) / (len(a) - 1)
    vb = sum((x - mb) ** 2 for x in b) / (len(b) - 1)
    pooled = math.sqrt(((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2))
    if pooled == 0:
        return 0.0
    return (ma - mb) / pooled


def paired_cohens_d_z(diffs: list[float]) -> float:
    """Paired standardized effect size d_z = mean(diffs) / sd(diffs)."""
    if len(diffs) < 2:
        return float("nan")
    assert_finite(diffs, label="diffs")
    m = sum(diffs) / len(diffs)
    var = sum((x - m) ** 2 for x in diffs) / (len(diffs) - 1)
    sd = math.sqrt(var)
    if sd < 1e-15:
        return 0.0
    return float(m / sd)


def paired_diff_ci(treatment: list[float], baseline: list[float]) -> dict[str, Any]:
    if len(treatment) != len(baseline):
        raise ValueError("paired_diff_ci requires equal-length seed-aligned series")
    diffs = [float(t) - float(b) for t, b in zip(treatment, baseline)]
    stats = mean_ci(diffs)
    d_z = paired_cohens_d_z(diffs)
    return {
        **stats,
        "diffs": diffs,
        "paired_cohens_d_z": d_z,
        "effect_size_definition": "d_z = mean(pairwise_differences) / sd(pairwise_differences)",
        "paired": True,
    }
