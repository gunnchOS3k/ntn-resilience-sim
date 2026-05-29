from pathlib import Path
import yaml

def test_scenario_files():
    for p in Path("configs/scenarios").glob("*.yaml"):
        data = yaml.safe_load(p.read_text())
        assert "scenario_id" in data
