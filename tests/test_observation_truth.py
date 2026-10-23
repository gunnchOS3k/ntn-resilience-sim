import pytest

from ntn_resilience.observation_truth import reported_link_up


def test_stale_up_observation_does_not_clear_current_outage():
    report = reported_link_up(
        terrestrial_outage=True,
        observation_says_up=True,
        observation_delay_steps=3,
    )
    assert report["current_truth_up"] is False
    assert report["reported_up"] is False
    assert report["observation_is_current_truth"] is False
    assert report["evidence_class"] == "SYNTHETIC_SIM"


def test_current_observation_is_used_when_delay_is_zero():
    report = reported_link_up(
        terrestrial_outage=False,
        observation_says_up=False,
        observation_delay_steps=0,
    )
    assert report["observation_is_current_truth"] is True
    assert report["reported_up"] is False


def test_negative_delay_is_rejected():
    with pytest.raises(ValueError, match="observation_delay_steps"):
        reported_link_up(
            terrestrial_outage=False,
            observation_says_up=True,
            observation_delay_steps=-1,
        )
