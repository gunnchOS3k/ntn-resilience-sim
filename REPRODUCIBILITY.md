# Reproducibility — NTN Resilience Simulator (RQ3)

This repository produces **synthetic disruption/fallback timelines** under documented assumptions (3GPP TR 38.821 ranges plus configured/synthetic entries). It does **not** report operator performance and does **not** claim University of Oulu affiliation.

## Clone / setup / run

```bash
git clone https://github.com/gunnchOS3k/ntn-resilience-sim.git
cd ntn-resilience-sim
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
make test
make smoke   # long e2e; synthetic only
make reproduce
```

Canonical independent digital path: `make reproduce` → `scripts/reproduce.py` → `results/experiments/rq3_gary_failover_sweeps.json`.

## Expected outputs

- `pytest -q` passes
- Experiment JSON includes `terrestrial_baseline`, `static_ntn`, `fallback`, `adaptive`
- Repeated seeds, recovery_steps_to_min_service, delay/capacity/visibility sweeps, compound-failure flag
- Every result carries `evidence_status: synthetic_simulation` and a non-operator disclaimer

## Tool versions

| Tool | Version guidance |
|------|------------------|
| Python | 3.10+ |
| Make | GNU Make |

## Fresh machine checklist

- [ ] Frozen SHA checkout
- [ ] Clean venv
- [ ] `make test` and `make reproduce`
- [ ] Do not relabel outputs as operator KPIs

## Evidence discipline

**Real today:** assumption registry, policies, seeded engine, tests.

**Synthetic / demo-only:** timelines, continuity fractions, sweep tables.

**Planned:** orbit-accurate visibility, consented field traces.

**Not claimed:** operational NTN service; operator SLA; Oulu affiliation.
