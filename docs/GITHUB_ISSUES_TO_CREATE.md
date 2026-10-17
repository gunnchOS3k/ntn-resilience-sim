# GitHub Issues to Create

## Issue 1: Implement reproducible experiment runner

**Labels**: enhancement, simulation

Implement a script or framework that executes simulation scenarios from configuration files and produces consistent, reproducible results. Should support parameterized runs, random seed control, and output to structured formats (CSV/JSON).

## Issue 2: Add formal metrics collection pipeline

**Labels**: enhancement, metrics

Build a metrics collection layer that captures latency, packet loss, throughput, handover delay, outage duration, recovery time, and availability windows during simulation runs. Output should be structured for analysis and visualization.

## Issue 3: Implement baseline comparison framework

**Labels**: enhancement, baselines

Create baseline simulation configurations (terrestrial-only, local-only, no-adaptation, cloud-only) and a comparison framework that evaluates NTN-adaptive approaches against these baselines across all scenarios.

## Issue 4: Add NTN channel model with configurable parameters

**Labels**: enhancement, simulation

Implement NTN channel models (LEO, HAPS, UAV) with configurable parameters for delay, Doppler, handover, and availability windows based on published specifications documented in `docs/ntn-assumptions.md`.

## Issue 5: Create scenario validation test suite

**Labels**: testing, scenarios

Build a test suite that validates each scenario configuration (Gary, Ghana, Guyana, Gaza, Graham Land) produces expected connectivity patterns and degradation behavior as documented in `docs/service-continuity-scenarios.md`.
