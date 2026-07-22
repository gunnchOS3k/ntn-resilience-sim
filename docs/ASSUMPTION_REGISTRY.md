# Assumption Registry

This registry lists non-measured parameters used by the Gate 2 resilience engine.

## Classes

- `measured` — from a validated measurement artifact
- `open_data` — from a cited open dataset
- `literature_backed` — from a verified citation (do not invent citations)
- `configured` — operator-chosen scenario parameter
- `synthetic` — synthetic proxy for comparative analysis only

## Current entries

See `config/assumption_registry.yaml`.

All NTN latency/capacity/availability values currently used in Gate 2 automated
runs are **configured** or **synthetic**. They are not field measurements and
must not be described as measured evidence.
