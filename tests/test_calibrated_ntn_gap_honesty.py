"""Paper III calibrated-gap honesty — never self-SUBMITTED."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAP = ROOT / "paper" / "CALIBRATED_NTN_GAP.json"
STATUS = ROOT / "paper" / "MANUSCRIPT_STATUS.md"
CLAIMS = ROOT / "paper" / "CLAIMS_TO_EVIDENCE.md"


def test_gap_ledger_keeps_synthetic_and_no_submitted():
    import subprocess

    gap = json.loads(GAP.read_text(encoding="utf-8"))
    tip = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    assert gap["evidence_class_current"] == "SYNTHETIC_SIM"
    assert gap["calibrated_ntn_measurements_present"] is False
    assert gap["device_measured_edge_io_present"] is False
    assert gap["submitted_claim"] is False
    assert gap["accepted_claim"] is False
    assert gap["source_tip"].startswith(tip[:7])
    assert any("SUBMITTED" in row["need"] for row in gap["gaps"])
    assert "HUMAN/RC2/V1 remain false" in gap["non_claims"]
    assert gap["engineering_guard"]["refuses_self_submitted"] is True


def test_manuscript_status_never_submitted():
    text = STATUS.read_text(encoding="utf-8")
    assert re.search(r"(?im)^\|\s*never\s*\|\s*SUBMITTED,\s*ACCEPTED\s*\|", text)
    assert "submission_ready | NO" in text.replace("`", "") or "| submission_ready | NO |" in text


def test_claims_table_forbids_submitted():
    text = CLAIMS.read_text(encoding="utf-8")
    assert "SUBMITTED / ACCEPTED" in text
    assert re.search(r"SUBMITTED\s*/\s*ACCEPTED\s*\|\s*\*\*no\*\*", text)
