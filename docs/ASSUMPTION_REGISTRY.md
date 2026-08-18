# Assumption Registry (Gate 3)

Load-bearing NTN parameters (`ntn_latency_ms`, `ntn_capacity_mbps`, `ntn_availability`) are labeled `literature_backed` and cite **3GPP TR 38.821**.

Configured/synthetic parameters remain explicit and do not alone qualify a scenario as `source_validated_simulation`.

See `config/assumption_registry.yaml` for source_id, source_location, and retrieval_date fields.

## Channel / network assumptions used by the RQ3 engine

| Parameter | Class | Role in `experiment.py` |
|-----------|-------|-------------------------|
| `ntn_latency_ms` [20, 60] | literature_backed (LEO-class TR 38.821) | delay sweep |
| `ntn_capacity_mbps` [1, 20] | literature_backed planning envelope | capacity sweep |
| `ntn_availability` [0.5, 0.99] | literature_backed planning envelope | visibility sweep |
| `handover_delay_s` | configured | Gate 2 ranking only |
| `terrestrial_outage_duration_s` | configured | Gate 2 ranking only |
| GEO RTT 550 ms | configured planning envelope | optional `delay_class: geo_configured` — **not** mixed silently with LEO |

Terrestrial baseline latency/capacity in the digital engine default to 25 ms / 20 Mbps **configured stubs**. They are transparent comparison anchors, not measured RAN KPIs.

## Gate 3 continuation (v1.2.0)

Load-bearing literature-backed parameters now record practical TR 38.821
Clause 5 / scenario section pointers. Configured and synthetic assumptions
remain explicitly non-literature-backed.
