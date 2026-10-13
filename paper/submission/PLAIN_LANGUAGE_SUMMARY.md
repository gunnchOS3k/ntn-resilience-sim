# A backup connection must be able to do the job

A satellite link can be visible yet too slow or too narrow for the task being requested. A satellite terminal can also depend on the same local power that a terrestrial connection needs. This paper uses a small, fully specified simulation to investigate those two ideas: service qualification and a shared power failure.

## How the study works

Thirty seeded timelines each contain 48 abstract steps. At each step the simulator draws whether terrestrial access is available, whether the satellite path is visible and whether terminal power is available. It assigns fixed capacity and delay values to each path. A path qualifies only when capacity is at least 1 Mbps and delay no more than 500 ms. Those requirements and input values are authored assumptions, not measurements or promises from a satellite provider. An abstract step has no duration in seconds.

In the favorable compound case, a qualifying satellite backup raises generated useful-service fraction from about 73.8% to 82.9%. Three satellite-aware rules obtain identical useful-service results. Naming one adaptive does not establish a better controller. The rules can still choose satellite access at different rates, so equal useful service does not mean equal potential cost or energy. Those costs are absent from the seeded engine.

## A worked example

Imagine a powered step with working terrestrial access at 25 ms and a visible satellite link at 550 ms. Under a 500 ms limit, terrestrial qualifies and satellite does not. A satellite-first policy chooses the visible satellite path and fails useful service. A terrestrial-first or qualifying-path selector keeps the qualifying terrestrial path. If local power fails, neither path can provide useful service. This hand calculation explains the model's decision rule; it is not a new field measurement.

In the preserved unfavorable probes, always preferring the unqualified satellite path reduces useful service to about 10.8%. Terrestrial-first and adaptive selection preserve terrestrial-only service in those cases. Delay 550 ms and capacity .5 Mbps create the same binary unqualified state on the same random stream. They illustrate different reasons for one mathematical failure, not two independent replications. This is not a conclusion that all GEO services are unusable: a different application delay budget can change qualification.

## What the results support

The study reproduces its own calculations and clarifies how an available path can fail a required service. Independent statistics use seed-level differences and 30 units; they do not treat all 1440 steps as real observations. The confidence interval describes Monte Carlo variability under the chosen model, with no uncertainty estimate for an operator or disaster population.

The model lacks real traffic, queues, correlated outage spells, orbital passes, attachment time, congestion after mass failover, battery behavior and physically independent backup power. More capacity above the qualifying threshold has no effect because demand and sharing are absent. Mathematical transparency is useful, but the elementary model and earlier richer simulators leave journal originality and external validity open for specialist review.

## Explore the idea

Draw a four-row table: terrestrial working/not working crossed with satellite visible/not visible. First assume both paths qualify and power works; mark whether at least one path can serve the task. Next make satellite fail the requirement and recompute each policy's choice. Finally set power down and check every row. Explain the difference between availability, selection and useful service. Use invented cases; do not test by disrupting a real emergency or important connection.

The unified registry links this companion to existing WAIKE networking, programming and data-analysis exercises, with prerequisites and assessment owned by that curriculum. To examine the research, open the Methods equations, analytical supplement, seed results and exact reproduction commands. The owner still needs to verify scientific conclusions, references, originality, rights and publication declarations. No human validation or journal submission is claimed.
