# NTN Resilience Simulation
## End-to-End Research Artifact

| Item | Detail |
|------|--------|
| **Runs today** | Research prototype with smoke test (synthetic, non-evidence) |
| **Demo** | `make e2e (smoke test only — not readiness proof) (smoke test only — not readiness proof)` |
| **Data** | Synthetic only — no private IQ or PII |
| **Extend** | See [EXTERNAL_RESEARCHER_QUICKSTART.md](docs/EXTERNAL_RESEARCHER_QUICKSTART.md) |
| **Limits** | Not operational 6G; not Oulu affiliation; not carrier-grade |
| **Readiness** | [END_TO_END_READINESS.md](docs/END_TO_END_READINESS.md) |
| **Proof** | [E2E_RUN_RECORD.md](reproducibility/E2E_RUN_RECORD.md) |
| **Artifacts** | [results/e2e/](results/e2e/) |

Simulates **terrestrial + non-terrestrial network resilience** for under-connected and disrupted communities.

> Research simulation — not operational NTN service claims.

## Scenarios

- Gary emergency connectivity
- Ghana rural fallback
- Guyana flood resilience
- Gaza **remote-first humanitarian**
- Graham Land **seasonal polar research outpost**

```bash
pip install -r requirements.txt && pytest -q
```
