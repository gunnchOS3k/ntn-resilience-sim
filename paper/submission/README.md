# Paper III - complete owner-review package

Candidate title: **Service Qualification and Shared-Power Limits in Terrestrial-Non-Terrestrial Fallback: A Reproducible Synthetic Benchmark**.

Primary journal: IEEE Open Journal of the Communications Society (OJ-COMS), original manuscript. Backup: IEEE Systems Journal, regular paper, after template conversion. All evidence is SYNTHETIC_SIM. Files are technically complete for rigorous owner review; modest originality, calibration, and external validity remain scientific concerns. No manuscript has been submitted, publicly posted, or approved by the owner in this workflow.

The canonical manuscript is `paper/manuscript.tex`; the synchronized submission copy is `paper/submission/manuscript.tex`. Historical `main.tex`, section files, four-seed summaries, registry wording, and frozen protocols remain preserved. Current references are `references.bib`; historical `bibliography.bib` is not the current paper bibliography.

## Contents

- `manuscript.pdf`, `manuscript.tex`, `references.bib`, `manuscript.bbl`: compiled editable OJ-COMS manuscript and verified reference set.
- `figures/`: five retained exports, including the mandatory graphical abstract, PDF and 300 dpi PNG; `scripts/generate_artifacts.py` is their editable source. The corrected grid has independently labeled latency/capacity axes.
- `tables/`: four manuscript tables, LaTeX and CSV.
- `artifacts/`: full 30-seed result JSON, statistical reports, environment lock, frozen protocol copies and source hashes.
- `REPRODUCIBILITY.md`, `DATA_DICTIONARY.md`, `STATISTICAL_VERIFICATION.md`: exact commands, schema, units, rounding, seed structure, and independent calculations.
- `SUPPLEMENTAL_METHODS.md`, `REVIEWER_SUPPLEMENT.md`: algorithm, analytical proofs, and reviewer orientation.
- `CITATION_VERIFICATION.md`, `NOVELTY_ASSESSMENT.md`, `CLAIM_TO_EVIDENCE.md`, `LIMITATIONS.md`: reference identity, claim support, competing work, and unresolved science.
- `AI_USE_DISCLOSURE.md`, `AUTHOR_METADATA.json`, `AVAILABILITY_AND_RIGHTS.md`: disclosures and confirmed metadata, with unknown declarations pending.
- `COVER_LETTER_DRAFT.md`, `VENUE_COMPLIANCE.md`, `PORTAL_FIELDS.md`, `OWNER_REVIEW_WORKSHEET.md`, `PLAIN_LANGUAGE_SUMMARY.md`: publication preparation, with no submission authority.
- `QUALITY_GATES.json`, `verification/`: gate evidence, reproduction/statistics/test records, final PDF QA.
- `template/`: original publisher sample and provenance. IEEEoj.cls and logo are publisher-owned template assets, retained unmodified.

Start with the PDF, plain-language summary, limitations, and owner worksheet. Complete scientific/rights declarations before considering a venue submission. Do not interpret a passing software gate as human verification or journal acceptance.
