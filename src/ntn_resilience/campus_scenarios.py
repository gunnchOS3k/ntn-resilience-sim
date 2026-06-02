"""Campus NTN scenario loader."""
from pathlib import Path
import yaml

DIR = Path(__file__).resolve().parents[2] / "configs" / "campus_scenarios"


def list_campus_scenarios() -> list[str]:
    return sorted(p.stem for p in DIR.glob("*.yaml"))


def load_campus_scenario(scenario_id: str) -> dict:
    path = DIR / f"{scenario_id}.yaml"
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data.get("scenario_id") != scenario_id:
        raise ValueError("scenario_id mismatch")
    return data
