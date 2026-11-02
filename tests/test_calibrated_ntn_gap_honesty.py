"""Paper III calibrated-gap honesty — never self-SUBMITTED."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAP = ROOT / "paper" / "CALIBRATED_NTN_GAP.json"
STATUS = ROOT / "paper" / "MANUSCRIPT_STATUS.md"
CLAIMS = ROOT / "paper" / "CLAIMS_TO_EVIDENCE.md"
FLOOR = "4aef716"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def test_gap_ledger_keeps_synthetic_and_no_submitted():
    gap = json.loads(GAP.read_text(encoding="utf-8"))
    tip = _git("rev-parse", "--short", "HEAD")
    assert gap["evidence_class_current"] == "SYNTHETIC_SIM"
    assert gap["calibrated_ntn_measurements_present"] is False
    assert gap["device_measured_edge_io_present"] is False
    assert gap["sim_to_measurement_transfer_present"] is False
    assert gap["independent_reproduction_present"] is False
    assert gap["operator_kpi_present"] is False
    assert gap["submitted_claim"] is False
    assert gap["accepted_claim"] is False
    assert gap["HUMAN"] is False
    assert gap["RC2"] is False
    assert gap["V1"] is False
    assert gap["floor_tip"].startswith(FLOOR)
    assert "prior_engineering_tip advances do not upgrade evidence_class" in " ".join(
        gap["non_claims"]
    )
    assert gap["engineering_guard"]["floor_preserved"].startswith(FLOOR)
    subprocess.check_call(["git", "merge-base", "--is-ancestor", gap["floor_tip"], "HEAD"], cwd=ROOT)
    # source_tip is the content deepen commit (≥floor); tip-stamp/test commits may follow.
    src = _git("rev-parse", gap["source_tip"])
    subprocess.check_call(["git", "merge-base", "--is-ancestor", src, "HEAD"], cwd=ROOT)
    subprocess.check_call(["git", "merge-base", "--is-ancestor", gap["floor_tip"], src], cwd=ROOT)
    assert tip  # HEAD readable
    assert "synthetic_evidence_bound" in gap
    gap_ids = {row["id"] for row in gap["gaps"]}
    assert {"NTN-GAP-001", "NTN-GAP-002", "NTN-GAP-003", "NTN-GAP-004", "NTN-GAP-005"} <= gap_ids
    assert any("SUBMITTED" in row["need"] for row in gap["gaps"])
    assert "HUMAN/RC2/V1 remain false" in gap["non_claims"]
    assert gap["engineering_guard"]["refuses_self_submitted"] is True


def test_synthetic_rq3_binding_matches_on_disk_evidence():
    gap = json.loads(GAP.read_text(encoding="utf-8"))
    bound = gap["synthetic_evidence_bound"]
    path = ROOT / bound["rq3_experiment_summary"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == bound["sha256"]
    summary = json.loads(path.read_text(encoding="utf-8"))
    assert summary["evidence_status"] == bound["evidence_status_expected"]
    assert summary["findings"]["ntn_always_better"] is bound["ntn_always_better_expected"]
    assert summary["findings"]["hypothesis_rejected"] is bound["hypothesis_rejected_expected"]
    assert summary["never"] == bound["never_expected"]
    assert "SUBMITTED" in summary["never"]
    assert "ACCEPTED" in summary["never"]


def test_manuscript_status_never_submitted():
    text = STATUS.read_text(encoding="utf-8")
    assert re.search(r"(?im)^\|\s*never\s*\|\s*SUBMITTED,\s*ACCEPTED\s*\|", text)
    assert "submission_ready | NO" in text.replace("`", "") or "| submission_ready | NO |" in text
    assert "independent_reproduction | PENDING" in text.replace("`", "") or "| independent_reproduction | PENDING" in text


def test_claims_table_forbids_submitted():
    text = CLAIMS.read_text(encoding="utf-8")
    assert "SUBMITTED / ACCEPTED" in text
    assert re.search(r"SUBMITTED\s*/\s*ACCEPTED\s*\|\s*\*\*no\*\*", text)
    assert "NTN always better" in text
    assert re.search(r"NTN always better\s*\|\s*\*\*no\*\*", text)
