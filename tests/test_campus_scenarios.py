from ntn_resilience.campus_reports import run_all_campus
from ntn_resilience.campus_scenarios import list_campus_scenarios


def test_campus_scenarios():
    assert len(list_campus_scenarios()) == 7
    run_all_campus()
