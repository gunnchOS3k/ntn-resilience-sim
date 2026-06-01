# Video Walkthrough — NTN resilience simulation

## Opening (30s)
This repo is a **research prototype** for community-scale 6G research. Not operational deployment.

## Code tour
Open: `src/ntn_resilience/cli.py`, `src/ntn_resilience/metrics.py`

Explain modules: ntn_resilience.cli, metrics, outage_model

## Diagram tour
Show `docs/diagrams/code_path_main_demo.mmd` and `sequence_main_demo.mmd`.

## Demo
```bash
make e2e
```
Show: `results/e2e/gary_emergency_metrics.json, ntn_research_card.md` — **synthetic toy data only**.

## Paper
Title in `paper/draft.md`. Toy results in `paper/preliminary_toy_results.md`.

## Closing
Complete for supervisor demo; field validation is future work.
