import json, numpy as np
from blueprint_invariant import orrery, daemon_gate as g, differential_frame as d, sentinel_dot as sd, pipeline as pl
def test_tusi_straight_line():
    th = np.linspace(0, 2*np.pi, 100); _, y = orrery.tusi_position(th); assert np.allclose(y, 0)
def test_tusi_trace_bounded():
    c = orrery.tusi_trace(np.arange(0, 86400, 60.)); assert c.min() >= 0 and c.max() <= 1
def test_triad_orthonormal():
    u, n, e = g.local_triad(np.random.default_rng(1).normal(size=(50, 3)) + [3, 0, 0])
    M = np.array([u, n, e]); assert np.allclose(M@M.T, np.eye(3))
def test_H_closure_ranges():
    _, v = pl.synthetic(512); H, c = g.invariants(v); assert 0 < H <= 1 and 0 <= c <= 1
def test_periodic_removed():
    s = np.arange(0, 7*86400, 600.); x = np.sin(2*np.pi*s/86400) + 0.3*np.sin(2*np.pi*s/3600)
    assert np.std(d.remove_periodic(s, x)) < 1e-8
def test_classification():
    s = np.arange(0, 7*86400, 600.); r = np.random.default_rng(0).normal(0, .01, len(s))
    assert d.classify(s, r) == "null"
    assert d.classify(s, r + 1e-6*s) == "candidate"
    assert d.classify(s, r, source_flip=True) == "invalid"
def test_reproducible_seal_and_tamper():
    s, v = pl.synthetic(1024); a, sa, _ = pl.measure(s, v); b, sb, _ = pl.measure(s, v)
    assert sa == sb and sd.verify(a, sa); a["ring_count"] += 1; assert not sd.verify(a, sa)
def test_device_changes_seal():
    s, v = pl.synthetic(512); assert pl.measure(s, v, "A")[1] != pl.measure(s, v, "B")[1]
def test_release_bundle(tmp_path):
    import pathlib; root = pathlib.Path(__file__).resolve().parents[1]
    out, seal, pk, cls = pl.build_release(tmp_path/"rel", root)
    for f in ["blueprint.jpeg", "blueprint.svc", "invariant_hash_block.json", "sentinel_sha256.txt",
              "orrery.py", "daemon_gate.py", "manifest.json", "package_sha256.txt", "README.md"]:
        assert (out/f).exists(), f
    ihb = json.loads((out/"invariant_hash_block.json").read_text()); assert sd.verify(ihb, seal)
    assert cls == "null"
