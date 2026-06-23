from sites.link_budget import estimate_margin_db


def test_graham_land_margin_penalty():
    g = estimate_margin_db("graham_land")
    n = estimate_margin_db("germany")
    assert g["margin_db"] < n["margin_db"]
