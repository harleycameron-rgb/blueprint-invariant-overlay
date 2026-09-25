"""Open environmental frame: daemon gate invariant extractor."""
import numpy as np
def coherence(trace): return float(np.mean(trace))
def local_triad(v):
    """Build orthonormal {u,n,e} from mean field vector samples (N,3)."""
    v = np.asarray(v, float); u = v.mean(0); u /= np.linalg.norm(u)
    ref = np.array([0,0,1.0]) if abs(u[2]) < .9 else np.array([1.0,0,0])
    e = np.cross(u, ref); e /= np.linalg.norm(e); n = np.cross(e, u)
    return u, n, e
def coherence_trace(v, window=16):
    """Rolling mean cosine similarity of consecutive unit vectors, in [0,1]."""
    v = np.asarray(v, float); w = v/np.linalg.norm(v, axis=1, keepdims=True)
    c = np.r_[1.0, np.clip(np.sum(w[1:]*w[:-1], 1), -1, 1)]
    c = 0.5*(1+c); k = np.ones(window)/window
    return np.convolve(np.pad(c, (window-1, 0), mode='edge'), k, 'valid')
def invariants(v):
    """H = mean resultant length of unit vectors; closure = |sum of steps| / path length."""
    v = np.asarray(v, float); w = v/np.linalg.norm(v, axis=1, keepdims=True)
    H = float(np.linalg.norm(w.mean(0)))
    d = np.diff(w, axis=0); path = np.linalg.norm(d, axis=1).sum()
    closure = float(np.linalg.norm(d.sum(0))/path) if path > 0 else 0.0
    return H, closure
def ring_events(trace, threshold=None):
    t = np.asarray(trace); th = t.mean()-2*t.std() if threshold is None else threshold
    below = t < th; return np.flatnonzero(below[1:] & ~below[:-1]) + 1
def run_gate(v):
    C = coherence_trace(v); H, cl = invariants(v)
    return {"triad": [x.tolist() for x in local_triad(v)], "coherence": C,
            "rings": ring_events(C), "H": H, "closure": cl}
