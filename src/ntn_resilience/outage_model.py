def sample_outage(p: float, rng=None) -> bool:
    import random
    r = rng or random
    return r.random() < p
