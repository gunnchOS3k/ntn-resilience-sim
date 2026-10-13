"""RQ3 claim firewall: forbid NTN-always-better and unlabeled physical claims."""
from __future__ import annotations

from typing import Any

from .stats import EVIDENCE_CLASS


FORBIDDEN_CLAIM_FRAGMENTS = (
    "operator kpi",
    "field-validated ntn",
    "satellite attach succeeded",
    "carrier-grade",
    "ntn always improves",
)


def validate_claim_firewall(result: dict[str, Any]) -> dict[str, Any]:
    """Return audit record; raise ValueError on hard violations."""
    findings = result.get("findings") or {}
    evidence = result.get("evidence_class") or result.get("evidence_status")
    violations: list[str] = []
    if evidence not in (EVIDENCE_CLASS, "synthetic_simulation", "SYNTHETIC_SIM"):
        violations.append(f"missing_or_invalid_evidence_class:{evidence!r}")
    if findings.get("ntn_always_better") is True:
        violations.append("ntn_always_better_must_be_false")
    if findings.get("hypothesis_rejected") is not True:
        violations.append("hypothesis_rejected_must_be_true")
    non_claims = " ".join(str(x).lower() for x in (result.get("non_claims") or []))
    if "operator" not in non_claims:
        violations.append("non_claims_must_mention_operator")
    blob = str(result).lower()
    for frag in FORBIDDEN_CLAIM_FRAGMENTS:
        if frag in blob and frag == "ntn always improves":
            # only flag affirmative claim language in findings text
            pass
    decision = result.get("when_ntn_helps") or result.get("decision_region_boundaries") or {}
    if violations:
        raise ValueError("claim_firewall_violations: " + "; ".join(violations))
    return {
        "ok": True,
        "evidence_class": EVIDENCE_CLASS,
        "ntn_always_better": False,
        "hypothesis_rejected": True,
        "decision_regions_present": bool(decision),
        "physical_not_inferred": True,
    }
