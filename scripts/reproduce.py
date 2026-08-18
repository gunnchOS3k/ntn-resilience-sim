#!/usr/bin/env python3
"""Independent digital reproduction of the RQ3 synthetic path."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def _pytest_cmd() -> list[str]:
    exe = shutil.which("pytest")
    if exe:
        return [exe, "-q"]
    return [sys.executable, "-m", "pytest", "-q"]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(SRC)}
    start = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    steps = [
        [*_pytest_cmd(), "tests/test_rq3_supervisor_digital.py", "tests/test_metrics.py", "tests/test_cli.py"],
        [sys.executable, "-m", "ntn_resilience.cli", "run-experiment", "rq3_gary_failover_sweeps"],
    ]
    for cmd in steps:
        r = subprocess.run(cmd, cwd=ROOT, env=env)
        if r.returncode != 0:
            return r.returncode
    artifact = ROOT / "results/experiments/rq3_gary_failover_sweeps.json"
    if not artifact.exists():
        print("missing experiment artifact", file=sys.stderr)
        return 1
    record = {
        "repo": "ntn-resilience-sim",
        "research_question": "RQ3",
        "command": "make reproduce",
        "start": start,
        "end": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "result": "PASS",
        "artifact": str(artifact.relative_to(ROOT)),
        "output_hashes": {str(artifact.relative_to(ROOT)): _sha256(artifact)},
        "evidence_status": "synthetic_simulation",
        "non_claims": [
            "Not independent human sign-off",
            "Not operator performance",
            "Not University of Oulu affiliation",
        ],
    }
    out = ROOT / "results/reproduce/REPRODUCE_RECORD.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
