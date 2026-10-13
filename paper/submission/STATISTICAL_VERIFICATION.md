# Independent statistical verification

`verification/statistics_audit.json` confirms exact fresh numerical-payload equality after dropping two output-path keys. Source/config/protocol hashes in `reproduction_audit.json` are unchanged. A separate SciPy implementation checks means, sample SDs and 95% Student-t endpoints; the largest original endpoint discrepancy is below 4e-13.

| Policy | Mean service from seed records | Sample SD | 95% interval |
|---|---:|---:|---|
| TN only | 0.73750333 | 0.06032988 | [0.71497579,0.76003088] |
| NTN first | 0.82916333 | 0.04967009 | [0.81061622,0.84771045] |
| TN first | 0.82916333 | 0.04967009 | [0.81061622,0.84771045] |
| Adaptive | 0.82916333 | 0.04967009 | [0.81061622,0.84771045] |

Paired adaptive-minus-TN mean: 0.09166000; SD of differences: 0.04258833093; 95% interval [0.07575725588,0.10756274412]; d_z=2.15223273624. The same paired result applies to the other NTN-aware policies. Their per-seed primary service arrays are exactly equal; no adaptive-versus-fallback superiority is inferred. All 30 feasible-case gains are positive.

The independent eight-state calculation enumerates P/R/V in {0,1}^3 with probability q^P(1-q)^(1-P)r^R(1-r)^(1-R)v^V(1-v)^(1-V). For each of the four qualification pairs it verifies the analytical expectations. At q=.85,r=.88,v=.85: TN=0.748, feasible NTN-aware=0.8347, satellite-first with unqualified NTN=0.1122. These are population expectations, distinct from seeded means. The 0.85 power ceiling applies to expectation; realizations may exceed it.

The experimental unit is one 48-step synthetic timeline. Intervals use n=30 and 29 degrees of freedom. No physical population, multiplicity-controlled grid inference, significance threshold, or device validation is claimed. Each fraction is rounded to four decimals before aggregation: absolute error <=0.00005 per fraction and <=0.0001 for a paired difference. Aggregates are rounded to four decimals for display. d_z is undefined when difference SD is zero; the source's zero-return convention is not interpreted as a scientific standardized effect.

The two unfavorable probes share one qualification state and one random stream. They are engineering counterexamples, not two independent statistical replications. Grid cells also reuse streams. No new seed experiment was substituted for the frozen 30-seed protocol. Old four-seed means 0.7396/0.8281 remain historical and never enter current tables.
