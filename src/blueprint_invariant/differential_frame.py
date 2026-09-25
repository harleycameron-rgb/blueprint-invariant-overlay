"""Differential drift extractor, periodic removal, residual spectrum, classification."""
import numpy as np
FACILITY_PERIODS = {"cryogenic": 3600.0, "mains": 1/50, "beam_pulse": 1.2,
                    "rf_cavity": 1/352.2e6, "diurnal": 86400.0}
def differential(a, b): return np.asarray(a) - np.asarray(b)
def remove_periodic(s, x, periods=FACILITY_PERIODS.values()):
    """Least-squares removal of sinusoids at known facility periods (Nyquist-resolvable only)."""
    s = np.asarray(s, float); x = np.asarray(x, float)
    dt = np.median(np.diff(s)); T = s[-1]-s[0]
    cols = [np.ones_like(s)]
    for p in periods:
        if 2*dt < p < T:
            w = 2*np.pi/p; cols += [np.sin(w*s), np.cos(w*s)]
    A = np.column_stack(cols); coef, *_ = np.linalg.lstsq(A, x, rcond=None)
    return x - A[:, 1:] @ coef[1:] - coef[0]
def residual_spectrum(x, dt):
    x = np.asarray(x) - np.mean(x); f = np.fft.rfftfreq(len(x), dt)
    return f, np.abs(np.fft.rfft(x))**2/len(x)
def classify(s, resid, source_flip=False, z=5.0):
    """periodic->null, secular->candidate, source flip->invalid."""
    if source_flip: return "invalid"
    s = np.asarray(s, float); A = np.column_stack([s-s.mean(), np.ones_like(s)])
    (m, _), res, *_ = np.linalg.lstsq(A, resid, rcond=None)
    sig = np.sqrt(res[0]/(len(s)-2)/np.sum((s-s.mean())**2)) if len(res) else 0
    return "candidate" if sig > 0 and abs(m)/sig > z else "null"
