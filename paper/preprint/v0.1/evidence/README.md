# Paper III v0.1 bounded reproducibility archive

No publication authorized. Experimental source 05aaa9aec16882f58bac6ce4ff47618d9812f69f; manuscript-development source f55c06aee3fbc0664dc8aac0c63f3ca5e030d2a7; candidate source revision is recorded separately in PROVENANCE.json. This archive includes unchanged source/configuration snapshot, frozen protocol, full existing 30-seed outputs and grids, independent statistics, data dictionary, figure sources and retained source MIT notices. No private measurements or IEEE template assets are included.

## Clean extraction verification

Use Python 3.12.14. From this extracted directory:

```sh
python scripts/verify_manifest.py
python -m venv .venv
.venv/bin/python -m pip install -r artifacts/environment.lock.txt
.venv/bin/python scripts/reproduce.py
MPLCONFIGDIR=generated/mpl .venv/bin/python scripts/generate_artifacts.py
```

The dependency lock is the original successful environment, not a vendored runtime or promise that every package wheel exists for every future platform. For local clean-extraction acceptance we use an existing environment with recorded exact versions rather than repeating downloads. The engine itself needs source/requirements.txt; the audit/plots also need NumPy/SciPy/Matplotlib. No absolute machine paths are needed. Reproduce.py reruns the unchanged bounded frozen protocol, compares every retained payload field except the two explicitly machine-dependent wrote/statistical_artifacts path keys, independently recomputes Student-t/paired statistics and enumerates all eight P/R/V states. Outputs go to generated/, leaving raw retained artifacts and verification records unchanged. No seed expansion or new experiment design occurs.

source/MANIFEST.json records exact original source hashes. SHA256SUMS covers every distributed payload file except itself. Verify before creating .venv or regenerating figures (exports may differ bytewise through timestamps/rendering library metadata while numeric values remain identical). The plotting script reads retained raw JSON and never resamples. The archive does not contain full-repository tests or the sibling field-kit fixtures; historical 37-test and focused 9-test logs are retained, not falsely presented as a standalone test suite.

Statistics use 30 timelines as units, not 1440 independent physical samples. All paths in CLAIM_TO_EVIDENCE.md are relative to this archive. Software consistency does not establish field validity, human approval, original novelty or deployment readiness. Generated scripts/docs/article license selection and final rights clearance remain owner decisions; existing software LICENSE is retained unchanged.
