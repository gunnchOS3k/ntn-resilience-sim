def sample_outage(p: float, rng=None) -> bool:
    import random
    r = rng or random
    return r.random() < p


def simulate_outage_timeline(steps: int = 20, outage_probability: float = 0.1, rng=None) -> list[dict]:
    import random
    r = rng or random.Random()
    timeline = []
    terrestrial_up = True
    for _ in range(steps):
        if sample_outage(outage_probability, rng=r):
            terrestrial_up = False
        else:
            terrestrial_up = True
        timeline.append({"terrestrial_up": terrestrial_up})
    return timeline
