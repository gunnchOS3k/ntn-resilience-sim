# Output dictionary

The JSON is synthetic, generated, and contains no participants, locations observed in the field, packets, or operator records. The named scenario is a configuration identifier. The retained full JSON is the numerical source for current figures/tables.

| Field | Type/unit | Interpretation |
|---|---|---|
| experiment_id, scenario_id | string | Configuration identifiers, not measurement geography |
| evidence_class | string | SYNTHETIC_SIM |
| seeds, n_seeds, steps | list/count | 1..30; 30 timelines; 48 abstract steps per timeline |
| policies[].policy | string | terrestrial_baseline, static_ntn, fallback, adaptive |
| policies[].runs[].seed | integer | Shared RNG seed for policy comparison |
| min_service_fraction | fraction [0,1] | Selected available path meeting both configured thresholds; rounded four decimals |
| uptime_fraction | fraction [0,1] | Selected path is online, regardless of qualification; rounded four decimals |
| offline_steps | count | Number of steps selecting offline |
| ntn_path_fraction | fraction [0,1] | Steps selecting NTN /48; not successful-fallback rate |
| mean_on_path_latency_ms | ms or null | Mean of scalar configured delays on selected online paths; excludes offline; no packets |
| recovery_steps_to_min_service | steps/count/null | First miss to first later restoration; 0 if no miss, null if never restored |
| parameters | dictionary | Input probabilities, delays, capacities, thresholds |
| statistics.n | count | Seed runs used for primary mean |
| mean_min_service, mean_uptime | fraction | Mean of rounded seed fractions, rounded again in reported aggregate |
| std_min_service | fraction | Sample SD over seed fractions, six decimals in engine |
| ci95_min_service.low/high | fraction | Student-t interval over seed means; model-conditional Monte Carlo variability |
| paired_vs_terrestrial | dictionary | Shared-seed difference statistics, intervals and d_z |
| sweeps | records | One varied input, common seed streams |
| decision_grids | records | Latency-visibility or capacity-visibility grid; repeated threshold states are not independent validation |
| compound_contrast | records | Simple versus shared power gated runs |
| delay_class_contrast | records | 40 ms vs configured 550 ms scalar delay |
| stress_probes | records | 0.5 Mbps configured NTN capacity |
| metrics | dictionary | Additional legacy derived indicators; not independent end-to-end measurements |
| findings, claim_firewall | dictionary | Software assertions and labels; no independent scientific certification |
| wrote, statistical_artifacts | paths | Host-specific output names excluded from portable payload comparison |

Policies[].runs is authoritative for base-case seed calculations. Grid/contrast/probe rows store aggregates rather than complete step-level trajectories; the engine can regenerate their runs from seeds and parameters. The rounded per-seed primary output, not unretained exact step totals, is the manuscript's statistical input. No recovery statistic is converted to seconds.
