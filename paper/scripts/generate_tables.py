#!/usr/bin/env python3
"""Generate Paper III policy table from experiment JSON."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "results" / "experiments" / "rq3_gary_failover_sweeps.json"
OUT = ROOT / "paper" / "tables"
OUT.mkdir(parents=True, exist_ok=True)
DEST = OUT / "rq3_policies.tex"


def main() -> int:
    if not SRC.exists():
        DEST.write_text(
            "\\textbf{RESULT\\_PENDING.} Run \\texttt{make paper-reproduce}.\\par\n",
            encoding="utf-8",
        )
        print("RESULT_PENDING")
        return 0
    data = json.loads(SRC.read_text(encoding="utf-8"))
    rows = []
    for p in data.get("policies") or []:
        name = p.get("policy", "?")
        up = p.get("mean_uptime", p.get("uptime_fraction", "n/a"))
        rows.append(f"{name} & {up} \\\\")
    body = "\n".join(rows) or "\\multicolumn{2}{c}{RESULT\\_PENDING} \\\\"
    DEST.write_text(
        "\\begin{table}[h]\\centering\n"
        "\\caption{RQ3 policy uptime fractions (SYNTHETIC\\_SIM; not operator KPIs).}\n"
        "\\begin{tabular}{lr}\\toprule policy & uptime fraction \\\\\\midrule\n"
        f"{body}\n\\bottomrule\\end{{tabular}}\\end{{table}}\n",
        encoding="utf-8",
    )
    print("wrote", DEST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
