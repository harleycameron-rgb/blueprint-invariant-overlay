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

# --- TECHNICAL_DATA.md spec functions ---
WHEEL = 260
def hierarchy_ratio(T_focus, member_periods):
    """H = T_focus / T_boundary, boundary = longest member period (§2.1)."""
    return float(T_focus) / float(max(member_periods))
def closure_from_H(H, wheel=WHEEL):
    """closure = exp(-ln^2(H/260)), bounded in (0,1] (§2.2)."""
    return float(np.exp(-np.log(H / wheel) ** 2))
def hill_ratio(a, m, M, a_outer):
    """Keplerian Hill radius / outer separation; >=1 means unbound outer member (§2.3)."""
    import warnings
    rh = a * (m / (3.0 * M)) ** (1 / 3); r = rh / a_outer
    if r >= 1: warnings.warn("outer member unbound (Hill ratio >= 1)")
    return float(r)
def gate_phases(s, sA, sB, omegaA=1.0, ratio=1.37):
    """phiA = 2*pi*wA*sA(s), phiB = 2*pi*wB*sB(s), wB/wA = 1.37 (§3.1)."""
    return 2*np.pi*omegaA*np.asarray(sA(s)), 2*np.pi*omegaA*ratio*np.asarray(sB(s))
def phase_coherence(phiA, phiB):
    """C(s) = cos(phiA - phiB) (§3.2)."""
    return np.cos(np.asarray(phiA) - np.asarray(phiB))
def ring_events_peak(C, tau=0.9):
    """Ring event on local peak above threshold tau (§3.3)."""
    C = np.asarray(C); return np.flatnonzero((C[1:-1] > C[:-2]) & (C[1:-1] >= C[2:]) & (C[1:-1] > tau)) + 1
