import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ntn_resilience.tool_adapters.ns3_export import export
def test_ns3(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert export().exists()
