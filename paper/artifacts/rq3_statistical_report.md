# RQ3 statistical report (SYNTHETIC_SIM)

- seeds: `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]`
- n_seeds: 30
- runtime_seconds: 0.2849
- evidence_class: `SYNTHETIC_SIM`
- ci_method: student_t_over_seed_means

> 95% Student-t CIs quantify simulation-run variability across seeds, NOT real-world RF or operator performance uncertainty.

| policy | mean min_service | std | 95% CI | paired Δ vs terrestrial |
|---|---:|---:|---|---:|
| terrestrial_baseline | 0.7375 | 0.0603 | [0.7150, 0.7600] |  |
| static_ntn | 0.8292 | 0.0497 | [0.8106, 0.8477] | 0.09166000000000002 |
| fallback | 0.8292 | 0.0497 | [0.8106, 0.8477] | 0.09166000000000002 |
| adaptive | 0.8292 | 0.0497 | [0.8106, 0.8477] | 0.09166000000000002 |

