# Gates 4–6 Soft Adapter Contract (ntn-resilience-sim)

Optional soft fields for the Oulu research repo
(`gunnchos-emergent-service-intent-protocols`). **No hard dependencies.**

## Non-goals

- No required import of Oulu packages
- No Gate 6 physical evidence from this document
- Missing sibling must not fail NTN CI

## Soft adapter fields (NTN → Oulu)

| Field | Type | Meaning |
|---|---|---|
| `scenario_id` | string | e.g. `gary_emergency` |
| `ntn_available` | number \| null | Soft availability hint in `[0, 1]` |
| `outage_profile_path` | string \| null | Path to outage / resilience result if present |
| `tn_ntn_failover` | boolean | Whether failover family is in play |
| `latency_budget_ms` | number \| null | Optional latency budget |
| `evidence_label` | string | Usually `SYNTHETIC_EXPERIMENT` for sim outputs |
| `adapter_status` | string | `AVAILABLE` \| `MISSING_SIBLING` \| `STUB` |

## Soft adapter fields (Oulu → NTN, optional)

| Field | Type | Meaning |
|---|---|---|
| `service_intent_id` | string \| null | Intent id from Oulu |
| `constraints` | string[] | May include `forbid_ntn` / `allow_ntn_failover` |
| `relay_preference` | string \| null | Soft preference only; never radio control |

## Integration rule

Oulu may soft-import `../ntn-resilience-sim` scenario summaries. This repo stays
standalone; adapters are documentation + optional future stubs only.
