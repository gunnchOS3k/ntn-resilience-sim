# External / independent reproduction packet — ntn-resilience-sim

**Status:** `INDEPENDENT_REPRODUCTION_PENDING` for a second-person sign-off. The **digital command path** is ready.

Cursor cannot sign this on another person’s behalf.

## Scope

RQ3 disruption/fallback on a frozen commit. Documented assumptions only — not operator KPIs.

## Command

```bash
git clone https://github.com/gunnchOS3k/ntn-resilience-sim.git
cd ntn-resilience-sim
git checkout <frozen-sha>
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make test
make reproduce
```

## Expected evidence form

```text
system:
commit:
command: make reproduce
start:
end:
result:
output_hashes:
deviations:
PASS_FAIL:
notes: synthetic_simulation; not operator performance; not Oulu affiliation
```

Store under `artifacts/independent_reproduction/` (no extra PII).

## What success does not mean

Digital PASS is not `FIELD_VALIDATED` and is not an NTN service measurement.
