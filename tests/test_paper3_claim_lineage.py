"""Paper III lineage: committed tables/CSVs equal a fresh regeneration, and Results prose matches the data."""
from __future__ import annotations

import importlib.util
from collections import defaultdict
from pathlib import Path

import pytest

from ntn_resilience.experiment import run_experiment

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
EXPERIMENT = "rq3_gary_failover_sweeps"


@pytest.fixture(scope="module")
def regen(tmp_path_factory):
    out = tmp_path_factory.mktemp("paper3")
    data = run_experiment(EXPERIMENT, out_dir=out / "results")
    spec = importlib.util.spec_from_file_location("p3_generate_tables", PAPER / "scripts" / "generate_tables.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    gen.SRC = out / "results" / f"{EXPERIMENT}.json"
    for name in ("TABLES", "FIGURES", "ARTIFACTS"):
        target = out / name.lower()
        target.mkdir()
        setattr(gen, name, target)
    gen._try_png = lambda *a, **k: None
    gen._write = lambda path, text: path.write_text(text, encoding="utf-8")
    assert gen.main() == 0
    return data, out


def _norm(p: Path) -> str:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n")


@pytest.mark.parametrize("name", sorted(p.name for p in (PAPER / "tables").glob("*.tex")))
def test_committed_table_matches_regeneration(regen, name):
    _, out = regen
    assert _norm(PAPER / "tables" / name) == _norm(out / "tables" / name), f"stale table {name}: run make paper-reproduce"


@pytest.mark.parametrize("name", sorted(p.name for p in (PAPER / "figures").glob("*.csv")))
def test_committed_figure_csv_matches_regeneration(regen, name):
    _, out = regen
    assert _norm(PAPER / "figures" / name) == _norm(out / "figures" / name), f"stale figure data {name}"


def _policy(data, name):
    return next(p for p in data["policies"] if p["policy"] == name)


NTN_AWARE = ("static_ntn", "fallback", "adaptive")


def test_prose_ntn_aware_beats_terrestrial_in_base_case(regen):
    data, _ = regen
    terr = _policy(data, "terrestrial_baseline")["mean_min_service"]
    assert all(_policy(data, p)["mean_min_service"] > terr for p in NTN_AWARE)


def test_prose_every_latency_visibility_cell_positive_and_gain_grows_with_visibility(regen):
    data, _ = regen
    text = _norm(PAPER / "sections" / "results.tex")
    assert "every adaptive-minus-terrestrial cell is positive" in text
    assert "gain grows with visibility" in text
    cells = defaultdict(dict)
    for c in data["decision_grids"]["latency_x_visibility"]:
        cells[(c["ntn_latency_ms"], c["ntn_visibility"])][c["policy"]] = c["mean_min_service"]
    vis = sorted({v for _, v in cells})
    for lat in sorted({latency for latency, _ in cells}):
        gains = [cells[(lat, v)]["adaptive"] - cells[(lat, v)]["terrestrial_baseline"] for v in vis]
        assert all(g > 0 for g in gains), (lat, gains)
        assert gains == sorted(gains) and gains[0] < gains[-1], (lat, gains)


def test_prose_recovery_shorter_for_ntn_aware(regen):
    data, _ = regen
    def mean_recovery(name):
        steps = [r["recovery_steps_to_min_service"] for r in _policy(data, name)["runs"]]
        assert None not in steps, f"{name}: prose says every seed recovers"
        return sum(steps) / len(steps)
    terr = mean_recovery("terrestrial_baseline")
    assert all(mean_recovery(p) < terr for p in NTN_AWARE)


def test_prose_geo_and_low_capacity_probes(regen):
    data, _ = regen
    f = data["findings"]
    geo = f["geo_min_service_vs_leo_adaptive"]
    assert geo["geo_rtt_ms"] == 550.0 and geo["max_latency_ms"] == 500.0 and geo["geo_exceeds_max_latency"]
    nh = f["when_ntn_does_not_help"]
    assert nh["static_ntn_geo_min_service"] < nh["terrestrial_min_service"]
    assert nh["fallback_geo_min_service"] == nh["terrestrial_min_service"]
    probes = {s["policy"]: s["mean_min_service"] for s in data["stress_probes"] if s["probe"] == "ntn_capacity_below_or_near_min"}
    assert probes["static_ntn"] < probes["terrestrial_baseline"]
    assert probes["fallback"] == probes["adaptive"] == probes["terrestrial_baseline"]


def test_prose_compound_failure_hurts_every_policy_and_ntn_aware_more(regen):
    data, _ = regen
    rows = {r["policy"]: r for r in data["compound_contrast"]}
    loss = {p: r["simple"]["mean_min_service"] - r["compound"]["mean_min_service"] for p, r in rows.items()}
    assert all(v > 0 for v in loss.values())
    assert all(loss[p] > loss["terrestrial_baseline"] for p in NTN_AWARE)
    assert data["findings"]["ntn_always_better"] is False
