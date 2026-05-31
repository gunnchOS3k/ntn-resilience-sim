import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def test_list_scenarios():
    r = subprocess.run(
        [sys.executable, "-m", "ntn_resilience.cli", "list-scenarios"],
        cwd=ROOT,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(SRC)},
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert "gary_emergency" in r.stdout
