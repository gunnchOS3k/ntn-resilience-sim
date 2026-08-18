# Claims to evidence — ntn-resilience-sim

Thesis RQ3 = disruption/fallback. Simulation only.

| Claim | Evidence level | Artifact | Status |
|-------|----------------|----------|--------|
| Seeded terrestrial vs NTN path selection runs | 2 synthetic sim | `src/ntn_resilience/experiment.py` | PASS digital |
| Transparent terrestrial baseline | 2 synthetic sim | policy `terrestrial_baseline` | PASS digital |
| Fallback / static / adaptive comparison | 2 synthetic sim | `fallback_policy.py` | PASS digital |
| Delay / capacity / visibility sweeps | 2 synthetic sim | `configs/experiments/rq3_gary_failover_sweeps.yaml` | PASS digital |
| Repeated seeds + recovery + min-service | 2 synthetic sim | `recovery_steps_to_min_service`, `min_service_fraction` | PASS digital |
| Compound failure (power + terrestrial) | 2 synthetic sim | `compound_failure: true` | PASS digital |
| Assumptions documented (TR 38.821 + configured) | 2 literature/configured | `config/assumption_registry.yaml` | PASS digital |
| Independent second-person reproduction | pending | `docs/packets/EXTERNAL_REPRODUCTION_PACKET.md` | PENDING |
| Operator performance / SLA | not claimed | disclaimers | NOT CLAIMED |
| Oulu affiliation | not claimed | README / non_claims | NOT CLAIMED |
