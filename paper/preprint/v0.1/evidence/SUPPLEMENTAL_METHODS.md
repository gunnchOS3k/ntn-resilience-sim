# Supplemental methodology

## Exact policy behavior

1. Sample three raw random draws per step: terrestrial up if draw>=0.12; NTN visible if draw<visibility; power up if draw>=0.15.
2. For compound failure, power down disables both usable paths. Simple condition ignores power while still consuming its draw.
3. TN only selects usable TN else offline. NTN first selects usable NTN else TN else offline. TN first selects usable TN else NTN else offline.
4. Adaptive forms available candidates and filters them against capacity>=1 Mbps and latency<=500 ms. If at least one qualifies, rank those; otherwise rank all available candidates. Sort ascending latency, then descending capacity, retaining TN insertion order for exact ties. No candidate means offline.
5. Evaluate useful service on the selected path. Offline contributes zero. Aggregate rounded fractions over the 48 steps and then over seeds.

Each selection has O(1) work for two candidates. The adaptive name does not imply machine learning, forecasting, multipath operation, or optimization. All policies see identical random states; only adaptive explicitly uses the qualification rule in selection. Compute budgets and signaling delays are not measured. This is a behavior audit, not a fairness proof for a deployed control comparison.

## Derivations

Let raw power/TN/NTN probabilities be q,r,v, and fixed qualification bits g_T,g_N. Conditioning on path priority gives:

- E[S_TN]=q r g_T.
- E[S_NTNfirst]=q[v g_N +(1-v)r g_T].
- E[S_TNfirst]=q[r g_T +(1-r)v g_N].
- E[S_adaptive]=q[r g_T+v g_N-r v g_T g_N].

For adaptive, useful service occurs exactly when at least one qualifying path is available. Inclusion-exclusion supplies the last equation. When both paths qualify, all three NTN-aware policies yield P(R OR V) on every step. For qualifying TN, fallback/adaptive gain q(1-r)v g_N over TN only. NTN-first gain is qv(g_N-rg_T); when g_N=0 it is negative whenever qrv>0. M<=P gives E[S]<=q, without bounding every finite realization by q.

All derivations use the sampler's raw independence, fixed qualification, instantaneous state access, and absent switching penalty. No general theorem of real NTN superiority follows. A delayed or cost-aware policy could invalidate these equivalence and dominance properties.

## Scope of ancillary components

The separate Gate-2 fallback adapter references edge/peer/offline concepts and energy/handover proxies. Those quantities do not enter the seeded RQ3 engine. Full repository tests verify adapter contracts but do not validate local/peer continuity, battery dynamics, terminal power consumption, RF channels, attachment, commercial-carrier service, or emergency workloads.

## Prospective upgrade, not completed evidence

A new versioned protocol should justify service requirements, define delay semantics, add correlated temporal/spatial failures and independently powered backup, model traffic sharing and feeder limits, charge switching delay/energy, equalize policy observations, and hold out scenarios. Measurements should distinguish simulated availability from attachment, delivered goodput, delay, power, and application completion. The current frozen protocol is preserved as an analytical control. No future field study is portrayed as completed, preregistered, or ethically approved.
