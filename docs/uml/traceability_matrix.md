# Traceability matrix — ntn-resilience-sim

| Diagram element | Source path |
|-----------------|-------------|
| Policies | `src/ntn_resilience/fallback_policy.py` |
| Experiment engine | `src/ntn_resilience/experiment.py` |
| Assumptions | `config/assumption_registry.yaml`, `docs/ASSUMPTION_REGISTRY.md`, `src/ntn_resilience/channel_assumptions.py` |
| Toy CLI | `src/ntn_resilience/cli.py` |
| Campus YAML | `configs/campus_scenarios/*.yaml` |
| Site outage model | `src/sites/outage_model.py` |
| Gate 2 decide | `src/ntn_resilience/gate2/decide.py` |
| Reproduce | `scripts/reproduce.py` |
| Non-claim: not operator KPIs | experiment `disclaimer` + `non_claims` |

[← UML README](README.md)
