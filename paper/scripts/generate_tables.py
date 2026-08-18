#!/usr/bin/env python3
"""Generate Paper III tables/figures from experiment JSON. Never invent numbers."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "results" / "experiments" / "rq3_gary_failover_sweeps.json"
TABLES = ROOT / "paper" / "tables"
FIGURES = ROOT / "paper" / "figures"
ARTIFACTS = ROOT / "paper" / "artifacts"
TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def _tex(s: object) -> str:
    return str(s).replace("_", "\\_")


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    print("wrote", path)


def _table(caption: str, header: str, body: str, spec: str) -> str:
    return (
        "\\begin{table}[h]\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\begin{{tabular}}{{{spec}}}\\toprule\n"
        f"{header} \\\\\\midrule\n{body}\n"
        "\\bottomrule\\end{tabular}\\end{table}\n"
    )


def _pending() -> None:
    msg = "\\textbf{RESULT\\_PENDING.} Run \\texttt{make paper-reproduce}.\\par\n"
    for name in (
        "rq3_policies.tex",
        "rq3_compound.tex",
        "rq3_delay_class.tex",
        "rq3_stress_capacity.tex",
        "rq3_decision_latency_visibility.tex",
        "rq3_findings.tex",
    ):
        _write(TABLES / name, msg)


def _svg_heatmap(path: Path, rows: list[str], cols: list[str], values: list[list[float]], title: str, vmin: float, vmax: float) -> None:
    cell, left, top = 56, 130, 52
    width = left + cell * len(cols) + 16
    height = top + cell * len(rows) + 36
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        f'<text x="8" y="18" font-size="11">{title}</text>',
    ]
    for j, lab in enumerate(cols):
        parts.append(
            f'<text x="{left + j * cell + cell / 2}" y="{top - 8}" font-size="9" text-anchor="middle">{lab}</text>'
        )
    span = max(vmax - vmin, 1e-9)
    for i, lab in enumerate(rows):
        parts.append(f'<text x="6" y="{top + i * cell + cell / 2 + 3}" font-size="9">{lab}</text>')
        for j, val in enumerate(values[i]):
            t = max(0.0, min(1.0, (val - vmin) / span))
            r = int(200 * (1 - t))
            g = int(60 + 160 * t)
            b = int(90)
            x, y = left + j * cell, top + i * cell
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell - 3}" height="{cell - 3}" fill="rgb({r},{g},{b})" stroke="#222"/>'
            )
            parts.append(
                f'<text x="{x + cell / 2}" y="{y + cell / 2 + 3}" font-size="9" text-anchor="middle">{val:.3f}</text>'
            )
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print("wrote", path)


def _try_png(path: Path, rows: list[str], cols: list[str], values: list[list[float]], title: str, vmin: float, vmax: float) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib unavailable; SVG/CSV only for", path.name)
        return
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    im = ax.imshow(values, cmap="RdYlGn", vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(cols)), cols)
    ax.set_yticks(range(len(rows)), rows)
    ax.set_title(title)
    fig.colorbar(im, ax=ax)
    for i in range(len(rows)):
        for j in range(len(cols)):
            ax.text(j, i, f"{values[i][j]:.3f}", ha="center", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    print("wrote", path)


def _pivot(rows: list[dict], y_key: str, x_key: str, policy: str, metric: str) -> tuple[list[str], list[str], list[list[float]]]:
    ys = sorted({r[y_key] for r in rows if r.get("policy") == policy})
    xs = sorted({r[x_key] for r in rows if r.get("policy") == policy})
    lookup = {(r[y_key], r[x_key]): r[metric] for r in rows if r.get("policy") == policy}
    grid = [[float(lookup.get((y, x), 0.0)) for x in xs] for y in ys]
    return [str(y) for y in ys], [str(x) for x in xs], grid


def main() -> int:
    if not SRC.exists():
        _pending()
        return 0
    data = json.loads(SRC.read_text(encoding="utf-8"))
    findings = data.get("findings") or {}
    policies = data.get("policies") or []
    rows = []
    for p in policies:
        rec = p.get("recovery")  # unused; keep table from means
        recov = []
        for run in p.get("runs") or []:
            recov.append(run.get("recovery_steps_to_min_service"))
        rec_txt = ",".join("NA" if x is None else str(x) for x in recov)
        rows.append(
            f"{_tex(p.get('policy'))} & {p.get('mean_uptime')} & {p.get('mean_min_service')} & "
            f"{rec_txt} \\\\"
        )
    _write(
        TABLES / "rq3_policies.tex",
        _table(
            "RQ3 policy means across seeds (SYNTHETIC\\_SIM; not operator KPIs). "
            "Recovery column is steps-to-min-service per seed (NA = never recovered).",
            "policy & mean uptime & mean min-service & recovery steps by seed",
            "\n".join(rows) or "\\multicolumn{4}{c}{RESULT\\_PENDING} \\\\",
            "lccc",
        ),
    )

    c_body = "\n".join(
        f"{_tex(r.get('policy'))} & {r['simple']['mean_min_service']} & "
        f"{r['compound']['mean_min_service']} & {r['delta_min_service_compound_minus_simple']} \\\\"
        for r in (data.get("compound_contrast") or [])
    ) or "\\multicolumn{4}{c}{RESULT\\_PENDING} \\\\"
    _write(
        TABLES / "rq3_compound.tex",
        _table(
            "Compound power+radio failure versus simple radio outage (SYNTHETIC\\_SIM).",
            "policy & simple min-service & compound min-service & delta (compound$-$simple)",
            c_body,
            "lccc",
        ),
    )

    d_body = "\n".join(
        f"{_tex(r.get('policy'))} & {r['leo_tr38821']['ntn_latency_ms']} & "
        f"{r['leo_tr38821']['mean_min_service']} & {r['geo_configured']['ntn_latency_ms']} & "
        f"{r['geo_configured']['mean_min_service']} \\\\"
        for r in (data.get("delay_class_contrast") or [])
    ) or "\\multicolumn{5}{c}{RESULT\\_PENDING} \\\\"
    _write(
        TABLES / "rq3_delay_class.tex",
        _table(
            "LEO TR-backed latency versus configured GEO RTT (550~ms). GEO exceeds "
            "max\\_latency\\_ms=500, so NTN can be on-path without meeting min-service.",
            "policy & LEO RTT (ms) & LEO min-service & GEO RTT (ms) & GEO min-service",
            d_body,
            "lcccc",
        ),
    )

    s_body = "\n".join(
        f"{_tex(r.get('policy'))} & {r.get('ntn_capacity_mbps')} & {r.get('min_capacity_mbps')} & "
        f"{r.get('mean_min_service')} & {r.get('below_min_capacity')} \\\\"
        for r in (data.get("stress_probes") or [])
    ) or "\\multicolumn{5}{c}{RESULT\\_PENDING} \\\\"
    _write(
        TABLES / "rq3_stress_capacity.tex",
        _table(
            "Capacity probe below min\\_capacity\\_mbps (SYNTHETIC\\_SIM). NTN path may be selected "
            "without meeting min-useful service.",
            "policy & NTN cap (Mbps) & min cap (Mbps) & mean min-service & below min",
            s_body,
            "lcccc",
        ),
    )

    lat_grid = data.get("decision_grids", {}).get("latency_x_visibility") or []
    # Compact table: adaptive delta vs terrestrial
    adaptive = [r for r in lat_grid if r.get("policy") == "adaptive"]
    terr = {
        (r["ntn_latency_ms"], r["ntn_visibility"]): r
        for r in lat_grid
        if r.get("policy") == "terrestrial_baseline"
    }
    vis_vals = sorted({r["ntn_visibility"] for r in adaptive})
    lat_vals = sorted({r["ntn_latency_ms"] for r in adaptive})
    header = "NTN latency (ms) & " + " & ".join(str(v) for v in vis_vals) + " vis."
    body_lines = []
    for lat in lat_vals:
        cells = []
        for vis in vis_vals:
            a = next(r for r in adaptive if r["ntn_latency_ms"] == lat and r["ntn_visibility"] == vis)
            t = terr[(lat, vis)]
            delta = round(a["mean_min_service"] - t["mean_min_service"], 4)
            cells.append(str(delta))
        body_lines.append(f"{lat} & " + " & ".join(cells) + " \\\\")
    spec = "l" + "c" * len(vis_vals)
    _write(
        TABLES / "rq3_decision_latency_visibility.tex",
        _table(
            "Decision region: adaptive minus terrestrial min-service (positive = NTN-aware policy helps). "
            "SYNTHETIC\\_SIM.",
            header,
            "\n".join(body_lines) or "\\multicolumn{2}{c}{RESULT\\_PENDING} \\\\",
            spec,
        ),
    )

    when = data.get("when_ntn_helps") or {}
    geo = findings.get("geo_min_service_vs_leo_adaptive") or {}
    nohelp = findings.get("when_ntn_does_not_help") or {}
    pol_ms = findings.get("policy_mean_min_service") or {}
    findings_tex = (
        f"Base-case (compound, LEO) mean min-service: terrestrial {pol_ms.get('terrestrial_baseline')}, "
        f"static/fallback/adaptive {pol_ms.get('adaptive')}. "
        f"On the latency$\\times$visibility grid (capacity held at the LEO planning value) every NTN-aware "
        f"cell beat terrestrial ({when.get('n_cells_ntn_helps')} helps, "
        f"{when.get('n_cells_ntn_hurts_or_worse')} worse, {when.get('n_cells_tie')} ties). "
        f"NTN does \\emph{{not}} help when configured GEO RTT {geo.get('geo_rtt_ms')}~ms exceeds "
        f"max-latency {geo.get('max_latency_ms')}~ms: static\\_ntn min-service "
        f"{nohelp.get('static_ntn_geo_min_service')} versus terrestrial "
        f"{nohelp.get('terrestrial_min_service')}; fallback equals terrestrial "
        f"({nohelp.get('fallback_geo_min_service')}). "
        f"The same pattern appears at NTN capacity 0.5~Mbps $<$ min-capacity 1.0~Mbps: static\\_ntn "
        f"{nohelp.get('static_ntn_low_capacity_min_service')} versus terrestrial "
        f"{nohelp.get('terrestrial_min_service')}. "
        f"Hypothesis ``NTN always better'' rejected: {str(findings.get('hypothesis_rejected')).lower()}. "
        "All numbers are \\texttt{SYNTHETIC\\_SIM}.\n"
    )
    _write(TABLES / "rq3_findings.tex", findings_tex)

    if adaptive and terr:
        ys, xs, grid = _pivot(lat_grid, "ntn_latency_ms", "ntn_visibility", "adaptive", "mean_min_service")
        csv_path = FIGURES / "rq3_adaptive_min_service_heatmap.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["ntn_latency_ms", *xs])
            for y, row in zip(ys, grid):
                w.writerow([y, *row])
        print("wrote", csv_path)
        _svg_heatmap(
            FIGURES / "rq3_adaptive_min_service_heatmap.svg",
            [f"{y} ms" for y in ys],
            [f"vis {x}" for x in xs],
            grid,
            "Adaptive min-service (latency x visibility) SYNTHETIC_SIM",
            0.0,
            1.0,
        )
        _try_png(
            FIGURES / "rq3_adaptive_min_service_heatmap.png",
            [f"{y} ms" for y in ys],
            [f"vis {x}" for x in xs],
            grid,
            "Adaptive min-service (SYNTHETIC_SIM)",
            0.0,
            1.0,
        )
        delta_grid = []
        for lat in lat_vals:
            row = []
            for vis in vis_vals:
                a = next(r for r in adaptive if r["ntn_latency_ms"] == lat and r["ntn_visibility"] == vis)
                t = terr[(lat, vis)]
                row.append(round(a["mean_min_service"] - t["mean_min_service"], 4))
            delta_grid.append(row)
        dcsv = FIGURES / "rq3_adaptive_minus_terrestrial.csv"
        with dcsv.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["ntn_latency_ms", *vis_vals])
            for lat, row in zip(lat_vals, delta_grid):
                w.writerow([lat, *row])
        print("wrote", dcsv)
        _svg_heatmap(
            FIGURES / "rq3_adaptive_minus_terrestrial.svg",
            [f"{v} ms" for v in lat_vals],
            [f"vis {v}" for v in vis_vals],
            delta_grid,
            "Adaptive minus terrestrial min-service (positive = NTN helps)",
            min(min(row) for row in delta_grid) if delta_grid else -0.2,
            max(max(row) for row in delta_grid) if delta_grid else 0.2,
        )
        _try_png(
            FIGURES / "rq3_adaptive_minus_terrestrial.png",
            [f"{v} ms" for v in lat_vals],
            [f"vis {v}" for v in vis_vals],
            delta_grid,
            "When NTN-aware adaptive helps vs terrestrial",
            min(min(row) for row in delta_grid) if delta_grid else -0.2,
            max(max(row) for row in delta_grid) if delta_grid else 0.2,
        )

    cap_grid = data.get("decision_grids", {}).get("capacity_x_visibility") or []
    if cap_grid:
        ys, xs, grid = _pivot(cap_grid, "ntn_capacity_mbps", "ntn_visibility", "static_ntn", "mean_min_service")
        csv_path = FIGURES / "rq3_static_ntn_capacity_visibility.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["ntn_capacity_mbps", *xs])
            for y, row in zip(ys, grid):
                w.writerow([y, *row])
        print("wrote", csv_path)
        _svg_heatmap(
            FIGURES / "rq3_static_ntn_capacity_visibility.svg",
            [f"{y} Mbps" for y in ys],
            [f"vis {x}" for x in xs],
            grid,
            "static_ntn min-service (capacity x visibility) SYNTHETIC_SIM",
            0.0,
            1.0,
        )
        _try_png(
            FIGURES / "rq3_static_ntn_capacity_visibility.png",
            [f"{y} Mbps" for y in ys],
            [f"vis {x}" for x in xs],
            grid,
            "static_ntn min-service (SYNTHETIC_SIM)",
            0.0,
            1.0,
        )

    trade_csv = FIGURES / "rq3_policy_tradeoff.csv"
    with trade_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["policy", "mean_uptime", "mean_min_service"])
        for p in policies:
            w.writerow([p.get("policy"), p.get("mean_uptime"), p.get("mean_min_service")])
    print("wrote", trade_csv)

    slim = {
        "experiment_id": data.get("experiment_id"),
        "findings": findings,
        "when_ntn_helps": {
            "n_cells_ntn_helps": when.get("n_cells_ntn_helps"),
            "n_cells_ntn_hurts_or_worse": when.get("n_cells_ntn_hurts_or_worse"),
            "n_cells_tie": when.get("n_cells_tie"),
            "hypothesis_ntn_always_better": False,
        },
        "policies": [
            {"policy": p.get("policy"), "mean_uptime": p.get("mean_uptime"), "mean_min_service": p.get("mean_min_service")}
            for p in policies
        ],
        "evidence_status": "synthetic_simulation",
        "never": ["SUBMITTED", "ACCEPTED"],
    }
    slim_path = ARTIFACTS / "rq3_experiment_summary.json"
    slim_path.write_text(json.dumps(slim, indent=2) + "\n", encoding="utf-8")
    print("wrote", slim_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
