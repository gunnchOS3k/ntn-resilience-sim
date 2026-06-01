# Problem → Solution Map — NTN Resilience Simulation

## The human problem
Emergencies and rural gaps isolate people when one link fails.

Who is harmed: Gary emergency users, rural Ghana/Guyana scenarios, humanitarian remote-first cases.

## The technical problem
Need source-backed link budgets and fallback policies—not toy outage curves alone.

## The research gap
Existing tools rarely combine **equity**, **open reproducibility**, and **cross-repo evidence** for under-connected communities at Gary-scale fidelity.

## This repo's solution
Scenario YAML, CLI timelines, resilience metrics, Gary emergency config (assumption-based smoke).

## What runs today
`make smoke` → `results/e2e/ outage timeline`

## What the output means
Smoke-test artifact for CI and portfolio review.

## What the output does NOT prove
Validated NTN operator performance.

## How a researcher can extend it
Pick one `next_evidence` item; document benchmark or field protocol; link PR to `[Evidence TODO]` issue.

## How a WAIKE learner can contribute
Run smoke test · file reproduction issue · fix docs/tests · pair with mentor on one evidence issue.
