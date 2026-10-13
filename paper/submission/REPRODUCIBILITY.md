# Reproduction record and commands

Experimental source: `05aaa9aec16882f58bac6ce4ff47618d9812f69f` in `gunnchOS3k/ntn-resilience-sim`. Publication-development HEAD is distinct from this source. The seed expansion/statistical-parity source revision is `7afde2e`; recovery checkpoint `4608fc7` preserved the interrupted draft. Frozen protocol files are unmodified. No retrospective registration claim is made.

Environment actually used: Python 3.12.14, macOS 27.0.1 arm64. `artifacts/environment.lock.txt` records exact installed versions, including PyYAML 6.0.3, jsonschema 4.26.0, NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2, and pytest 9.1.1. The simulator itself needs only requirements.txt. Numerical reproduction is not promised across arbitrary Python or RNG versions.

## Clean reproduction

```sh
git clone https://github.com/gunnchOS3k/ntn-resilience-sim.git
cd ntn-resilience-sim
git checkout 05aaa9aec16882f58bac6ce4ff47618d9812f69f
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHONPATH=src .venv/bin/python -m ntn_resilience.cli run-experiment rq3_gary_failover_sweeps
```

Output: `results/experiments/rq3_gary_failover_sweeps.json` plus `rq3_statistical_report.csv` and `.md`. The paper package retains the full output in artifacts. Deterministic numerical payload equality was verified in this continuation, excluding the machine-dependent `wrote` and `statistical_artifacts` path fields. The recorded raw output SHA-256 is in `verification/reproduction_audit.json`; a payload comparison is more portable than a byte hash of paths.

## Recheck the current author-review package

Run from the repository root using a Python 3.12 environment containing the locked dependencies:

```sh
python -m pip install -r paper/submission/artifacts/environment.lock.txt
PYTHONPATH=src python paper/submission/scripts/verify_statistics.py
MPLCONFIGDIR=/tmp/paper-iii-mpl python paper/submission/scripts/generate_artifacts.py
PYTHONPATH=src python -m pytest -q tests/test_rq3_supervisor_digital.py tests/test_metrics.py tests/test_cli.py
```

The verification script re-executes unchanged engine code, compares every retained payload field, recomputes Student-t intervals and paired effects with SciPy, and independently enumerates eight power/radio/visibility states for all four qualification combinations. It writes fresh outputs under verification/fresh_reproduction and an audit JSON. The plotting script only reads retained synthetic JSON; it does not resample data or redefine protocols. The recovered_helpers directory is historical, not the supported current reproduction entry point.

For the full 37-test suite, place `gunnchos-7gc-ai-ran-field-kit` beside this repository at `9dfc326647880c244904dd50a47ea80c3d46748e`. Five Gate-2 contract tests otherwise fail from missing schema fixtures; these are separate adapter tests and are not evidence that local/peer fallback was validated in RQ3. Full test output is `verification/tests_full.txt`; focused output is `verification/tests_rq3.txt`.

## Inputs and units

Seeds: contiguous integers 1 through 30, common to each comparable policy. Each run has 48 abstract steps. Per step, RNG consumes terrestrial, NTN, then power draws, even in the simple condition. Fixed TN: 20 Mbps/25 ms; base NTN: 5 Mbps/40 ms/visibility 0.85; radio outage probability 0.12; power outage probability 0.15. Qualification: capacity >=1 Mbps AND delay <=500 ms. Grids: delay {20,40,60} ms, capacity {1,5,20} Mbps, visibility {0.5,0.85,0.99}. Unfavorable probes: 550 ms configured GEO or 0.5 Mbps capacity. These are configured assumptions, not measurements or standards-guaranteed values. No step-to-seconds mapping exists.

Source hashes are retained for experiment.py, fallback_policy.py, stats.py, executing YAML, frozen protocol YAML and registry YAML. A separate `source_snapshot/` contains the unchanged src, configs, config, requirements, and LICENSE from the audited commit; its manifest records all hashes. The snapshot supports the seeded engine, while full-repository tests still require repository test files and sibling fixtures.

## Compilation

The final PDF was built with TinyTeX, pdfLaTeX and BibTeX (TeX Live 2026). Run from paper/submission with those executables on PATH:

```sh
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
```

IEEEoj.cls, IEEEtran.bst and the official logo are included. Publisher date, volume and rights claims are suppressed in the manuscript preamble for this owner-review draft. Final compilation stdout and logs are retained under verification; all eight rendered pages were inspected. Header vbox and tiny-font substitution warnings arise from the official class; no overlap, clipped text, missing symbols or unresolved references were visible in the final pages. No shell escape is required.
