from pathlib import Path
import yaml

SCENARIOS_DIR = Path(__file__).resolve().parents[2] / "configs" / "scenarios"


def list_scenarios() -> list[str]:
    return sorted(p.stem for p in SCENARIOS_DIR.glob("*.yaml"))


def load_scenario(scenario_id: str) -> dict:
    path = SCENARIOS_DIR / f"{scenario_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Unknown scenario: {scenario_id}")
    with path.open() as f:
        data = yaml.safe_load(f)
    if data.get("scenario_id") != scenario_id:
        raise ValueError(f"scenario_id mismatch in {path}")
    return data
