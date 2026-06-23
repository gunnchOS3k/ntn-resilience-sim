from sites.edge_cache import edge_cache_simulation


def test_gaza_high_cache():
    r = edge_cache_simulation("gaza")
    assert r["cache_hit_rate"] >= 0.85
