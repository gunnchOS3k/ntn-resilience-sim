from sites.outage_model import outage_timeline


def test_outage_paths():
    tl = outage_timeline("gaza", steps=20, seed=7)
    paths = {s["path"] for s in tl}
    assert "offline_cache" in paths or "offline" in paths
