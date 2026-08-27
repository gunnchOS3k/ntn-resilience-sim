# Research artifact index — RQ3 statistical parity

| Field | Value |
|-------|-------|
| Repo | `ntn-resilience-sim` |
| Accepted base SHA | `916520919bea4d9957970d824045c32929bb80e5` |
| Branch | `research/rq3-statistical-parity-001` |
| Environment | `.venv` Python 3.11 Framework; docs 3.10+ |
| Exact command | `PYTHONPATH=src python -m ntn_resilience.cli run-experiment rq3_gary_failover_sweeps` |
| Seeds | `[1..30]` (n=30, predeclared contiguous; shared across policies; no outcome-based selection) |
| Seed runtime | ~0.28 s full experiment locally (trivial; n=30 retained) |
| Input provenance | Literature-backed channel assumptions + scenario YAML (not operator attach) |
| Outputs | `paper/artifacts/rq3_statistical_report.{csv,md}`, `rq3_statistical_summary.json` (+ local results/ on reproduce) |
| Evidence class | `SYNTHETIC_SIM` |
| CI method | Student-t 95% over seed means; paired diffs vs terrestrial with `d_z` |
| t-crit verification | SciPy 1.18.0 `scipy.stats.t.ppf(0.975, df)` (stdlib embedded table at runtime) |
| Negative results | GEO RTT / low capacity / compound power: NTN not always better; offline wins |
| Claim firewall | `claim_firewall` requires `ntn_always_better=false`, operator non-claims |
| Physical / external not performed | `NTN_OPERATOR_ATTACH=NOT_RUN`, `INDEPENDENT_REPRODUCTION=EXTERNAL_PENDING`, `CERTIFICATION=NOT_RUN`, `CARRIER_ACCEPTANCE=NOT_RUN` |
