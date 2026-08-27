# RQ3 statistical report (SYNTHETIC_SIM)

- seeds: `[1, 2, 7, 42]`
- evidence_class: `SYNTHETIC_SIM`
- ci_method: student_t_over_seed_means

> 95% Student-t CIs quantify simulation-run variability across seeds, NOT real-world RF or operator performance uncertainty.

| policy | mean min_service | std | 95% CI | paired Δ vs terrestrial |
|---|---:|---:|---|---:|
| terrestrial_baseline | 0.7396 | 0.0361 | [0.6822, 0.7970] |  |
| static_ntn | 0.8281 | 0.0313 | [0.7784, 0.8779] | 0.08857499999999996 |
| fallback | 0.8281 | 0.0313 | [0.7784, 0.8779] | 0.08857499999999996 |
| adaptive | 0.8281 | 0.0313 | [0.7784, 0.8779] | 0.08857499999999996 |

