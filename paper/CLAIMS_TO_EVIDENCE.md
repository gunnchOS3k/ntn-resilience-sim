# Claims (Paper III)

| Claim | Allowed | Evidence |
|---|---|---|
| Seeded simulation of fallback policies | yes, SYNTHETIC_SIM | `make paper-reproduce` |
| NTN-aware policies beat terrestrial on the LEO latency×visibility grid | yes, SYNTHETIC_SIM | `paper/tables/rq3_decision_latency_visibility.tex` |
| NTN is not always better | yes (required) | GEO RTT and 0.5 Mbps capacity probes; `static_ntn` worse than terrestrial |
| Compound power+radio reduces min-service | yes, SYNTHETIC_SIM | `paper/tables/rq3_compound.tex` |
| NTN always better | **no** | rejected by protocol probes |
| Operator KPI | **no** | — |
| Device-measured Edge I/O pose | **no** | PHYSICAL_PENDING |
| SUBMITTED / ACCEPTED | **no** | `MANUSCRIPT_STATUS.md` |
