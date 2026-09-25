"""Closed geometric frame: Tusi-couple coherence overlay."""
import numpy as np
RATIO = 1.37      # non-locking harmonic ratio
DIALS = 260       # dial invariant
def tusi_position(theta, r=1.0):
    """Point on inner circle (radius r) rolling in circle 2r: traces a straight diameter."""
    return (r*np.cos(theta)+r*np.cos(-theta), r*np.sin(theta)+r*np.sin(-theta))
def tusi_trace(s, period=86400.0, ratio=RATIO):
    """Closed-frame reference coherence C_tusi(s) in [0,1] from two non-locking couples."""
    s = np.asarray(s, float); th = 2*np.pi*s/period
    x1, _ = tusi_position(th); x2, _ = tusi_position(ratio*th)
    return 0.5 + 0.125*(x1 + x2)  # x in [-2,2] each -> [0,1]
def dial_index(theta):
    return (np.floor((np.asarray(theta) % (2*np.pi))/(2*np.pi)*DIALS)).astype(int)
def radial_partitions(n_rings=7, ratio=RATIO):
    return [ratio**-k for k in range(n_rings)]
