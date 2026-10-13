# Claim-to-evidence links (archive relative)

| Claim | Retained evidence | Bound |
|---|---|---|
| TN.7375; NTN-aware.8292 | [raw JSON](artifacts/rq3_gary_failover_sweeps.json), policies[].runs/statistics; [table](tables/base.csv) | 30 synthetic timelines |
| Gain.09166; CI[.07575726,.10756274], dz2.15223274 | [independent stats](verification/statistics_audit.json), independent_statistics.adaptive.paired_vs_tn | Paired Monte Carlo uncertainty |
| Three NTN-aware policies equal | raw JSON, policies[].statistics.seed_min_service; preprint Eq14 | Both paths qualify; no switch cost |
| Harmful.1083 versus retained.7375 | raw JSON, delay_class_contrast/stress_probes; [negative table](tables/negative.csv) |550ms or.5Mbps; same qualification bit/stream |
| Shared-power expectation ceiling.85 | [eight-state audit](verification/statistics_audit.json), exact_8_state_expectation_check; [experiment source](source/src/ntn_resilience/experiment.py); preprint Eq17 | Population only; finite sample can exceed |
| Latency grid20/40/60; capacity1/5/20 | raw JSON, decision_grids; [plot source](scripts/generate_artifacts.py) | Flat within qualifying region |
| Full37 focused9 tests | [full log](verification/tests_full.txt), [focused log](verification/tests_rq3.txt) | Historical software checks with sibling fixtures; not standalone suite |
| Frozen source/protocol | [original snapshot manifest](source/MANIFEST.json), [protocol](artifacts/experiment_protocol.yaml), [execution YAML](source/configs/experiments/rq3_gary_failover_sweeps.yaml) | No retrospective registration claim |

No physical NTN, adaptive superiority, validated local/peer path, externally calibrated parameters or established originality is claimed. The source/stats verifier operates from clean extraction with generated outputs separate from retained records.
