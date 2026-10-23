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

# Local window before a fragment. Negated non-claims must not trip the firewall.
_NEGATION_MARKERS = ("not ", "no ", "never ", "without ", "non-", "isn't ", "is not ")
_TOP_LEVEL_CLAIM_KEYS = ("abstract", "claim", "claims", "conclusion", "summary", "narrative")


def _string_chunks(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        chunks: list[str] = []
        for item in value.values():
            chunks.extend(_string_chunks(item))
        return chunks
    if isinstance(value, (list, tuple)):
        chunks = []
        for item in value:
            chunks.extend(_string_chunks(item))
        return chunks
    return []


def claim_corpus(result: dict[str, Any]) -> str:
    """Claim-bearing text only. Non-claims and disclaimers are excluded."""
    chunks = _string_chunks(result.get("findings"))
    for key in _TOP_LEVEL_CLAIM_KEYS:
        chunks.extend(_string_chunks(result.get(key)))
    return "\n".join(chunks).lower()


def affirmative_forbidden_fragment(text: str, fragment: str) -> bool:
    """True when fragment appears without a nearby negation."""
    needle = fragment.lower()
    start = 0
    while True:
        index = text.find(needle, start)
        if index < 0:
            return False
        window = text[max(0, index - 32) : index]
        if not any(marker in window for marker in _NEGATION_MARKERS):
            return True
        start = index + len(needle)


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
    corpus = claim_corpus(result)
    for frag in FORBIDDEN_CLAIM_FRAGMENTS:
        if affirmative_forbidden_fragment(corpus, frag):
            violations.append(f"forbidden_claim:{frag}")
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
