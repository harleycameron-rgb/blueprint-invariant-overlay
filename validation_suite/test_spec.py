import numpy as np, pytest
from blueprint_invariant import daemon_gate as g
def test_hierarchy_ratio(): assert g.hierarchy_ratio(520, [10, 2, 1]) == 52
def test_closure_bounds():
    assert g.closure_from_H(260) == 1.0
    for H in [1e-3, 1, 100, 1e5]: assert 0 < g.closure_from_H(H) <= 1
def test_hill_warns():
    with pytest.warns(UserWarning): g.hill_ratio(1.0, 1.0, 1.0, 0.1)
def test_phase_coherence_ratio():
    s = np.linspace(0, 10, 1000); a, b = g.gate_phases(s, lambda x: x, lambda x: x)
    assert np.allclose(b / np.where(a == 0, 1, a)[..., None].ravel()[:len(a)], np.where(a == 0, 0, 1.37))
    C = g.phase_coherence(a, b); assert C.min() >= -1 and C.max() <= 1
def test_ring_peaks(): assert list(g.ring_events_peak([0, .95, 0, .5, 0, .99, 0])) == [1, 5]
