# ntn-resilience-sim

Simulation of terrestrial + **non-terrestrial network (NTN)** resilience for under-connected and disrupted communities.

> **Current release/state:** `DIGITALLY_VALIDATED` simulation — **not** operational NTN service; modem SKU ≠ NTN capability.

Ecosystem portal: [gunnchos-research-portal](https://github.com/gunnchOS3k/gunnchos-research-portal) · Product charter: [gunnchOS3k_PRODUCT_CHARTER.md](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/blob/main/program/charter/gunnchOS3k_PRODUCT_CHARTER.md)

## What is this?

Scenario YAML, CLI timelines, resilience metrics, and research configs for NTN fallback studies.

## Why does it exist?

Service continuity research when terrestrial links fail needs explicit simulation before field claims.

## Where does it fit?

Product Charter **layer 6** (connectivity research). Consumed by field-kit / portal connectivity docs.

## What is real today?

- CLI + scenario configs + `make smoke` / `make e2e` synthetic bundles
- Cross-repo NTN interface docs

## What is simulated / modelled?

- Entire resilience timelines are simulated/assumption-based unless labeled otherwise
- Gary emergency and comparative scenarios are research configurations

## What is physical / external pending?

- Operator-validated NTN performance
- Device/modem field campaigns
- Any claim that RM520N-GL alone proves NTN — **forbidden**

## Try / inspect in 5 minutes

```bash
pip install -r requirements.txt
make test
make smoke   # synthetic evidence only
```

## Architecture

Python sim + YAML scenarios → `results/e2e/` resilience bundles.

## Repo map

| Path | Role |
|---|---|
| `configs/` | Scenarios |
| package/src | Simulator |
| `results/` | Smoke outputs |
| `docs/` | Reality + readiness |

## Interfaces

Export contracts toward 7GC/field-kit research consumers — research only.

## Tests

```bash
make lint test contract-test
```

## Evidence

`results/e2e/` + reproducibility docs. Not carrier evidence.

## Known gaps

Calibrated operator data; physical NTN campaigns; honest non-inference from modem SKU.

## Beginner path

A **backup-generator simulator** for internet when the main link drops.

## Intern path

Run smoke; change one scenario parameter; compare metrics.

## Expert path

Sensitivity (`make sensitivity`) without overclaiming field truth.

## Contribution path

Scenarios, metrics, tests. Keep simulation_not_RM520_NTN boundary.

## Current release / state

**DIGITALLY_VALIDATED** sim. Not commercial 6G. Not operational NTN.

## Claim boundary

Simulation only · no commercial 6G · no RM520→NTN inference · Cursor DRAFT-only.

---

## Retained detail (post–Cycle 3A front door)

Full prior README: [docs/history/README_PRE_WP012.md](docs/history/README_PRE_WP012.md).

Retained: [docs/START_HERE.md](docs/START_HERE.md) · [docs/WHAT_IS_REAL_TODAY.md](docs/WHAT_IS_REAL_TODAY.md).
