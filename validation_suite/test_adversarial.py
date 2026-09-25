"""Adversarial calibration of the v1.0.2 drift detector."""
import numpy as np, pytest
from blueprint_invariant import pipeline as p, differential_frame as d
C = lambda s, v: d.classify_drift(s, v)["classification"]
def test_false_positive_rate_on_noise():
    fp = sum(C(*p.synthetic(seed=k)) == "candidate" for k in range(100)); assert fp <= 4
def test_detects_small_linear_drift():
    assert sum(C(*p.synthetic(drift=0.005, seed=k)) == "candidate" for k in range(20)) >= 18
def test_power_increases_with_drift():
    r = [sum(C(*p.synthetic(drift=x, seed=k)) == "candidate" for k in range(20)) for x in (0.0, 0.002, 0.01)]
    assert r[0] < r[1] < r[2] or r[2] >= 19
def test_unknown_periodic_is_not_drift():
    for per in (7*3600, 20*3600):
        n = 0
        for k in range(20):
            s, v = p.synthetic(seed=k); v[:, 1] += 0.02*np.sin(2*np.pi*s/per); n += C(s, v) == "candidate"
        assert n <= 2
def test_random_walk_not_called_candidate():
    n = 0
    for k in range(20):
        s, v = p.synthetic(seed=k); v[:, 1] += np.cumsum(np.random.default_rng(k).standard_normal(len(s)))*5e-4
        n += C(s, v) == "candidate"
    assert n <= 3
def test_spike_does_not_trigger():
    s, v = p.synthetic(seed=1); v[100, 1] += 50; assert C(s, v) == "null"
def test_counter_drift_detected():
    s, v = p.synthetic(seed=2); v[:, 1] += .1*s/s[-1]; v[:, 2] -= .1*s/s[-1]; assert C(s, v) == "candidate"
def test_nan_rejected():
    s, v = p.synthetic(); v[5, 1] = np.nan
    with pytest.raises(ValueError): p.measure(s, v)
def test_source_flip_invalid():
    s, v = p.synthetic(); assert d.classify_drift(s, v, source_flip=True)["classification"] == "invalid"
