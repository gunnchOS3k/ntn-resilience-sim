from sites.site_registry import SITE_IDS, get_site


def test_registry():
    assert len(SITE_IDS) == 7
    assert get_site("gary")["primary_path"] == "urban_edge_ai_ran"
