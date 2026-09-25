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

# --- v1.0.2 detector: raw-channel secular drift with HAC trend test -------------
from math import erf, sqrt, ceil
def _p_two_sided(z): return 1 - erf(abs(z)/sqrt(2))
def validate(s, v):
    s = np.asarray(s, float); v = np.asarray(v, float)
    if not (np.all(np.isfinite(s)) and np.all(np.isfinite(v))): raise ValueError("non-finite samples in input")
    if np.any(np.diff(s) <= 0): raise ValueError("time axis must be strictly increasing")
    if len(s) < 64: raise ValueError("need at least 64 samples")
    return s, v
def _winsorize(x, k=8.0):
    med = np.median(x); mad = 1.4826*np.median(np.abs(x-med)) or 1e-12
    out = np.abs(x-med) > k*mad; return np.clip(x, med-k*mad, med+k*mad), int(out.sum())
def _design(s, freqs):
    c = s - s.mean(); cols = [np.ones_like(s), c]
    for w in freqs: cols += [np.sin(w*s), np.cos(w*s)]
    return np.column_stack(cols)
def _remove_lines(s, x, periods=(), max_lines=6, snr=25.0):
    """Jointly fit offset + linear trend + known facility lines + up to max_lines unknown lines
    (frequency-refined, period < T/2). Returns x with only the periodic parts removed (trend kept)."""
    T = s[-1]-s[0]; dt = np.median(np.diff(s))
    ws = [2*np.pi/p for p in periods if 2*dt < p < T]
    for _ in range(max_lines):
        A = _design(s, ws); r = x - A @ np.linalg.lstsq(A, x, rcond=None)[0]
        f, P = residual_spectrum(r, dt); ok = f > 2.0/T
        if not ok.any(): break
        i = np.flatnonzero(ok)[np.argmax(P[ok])]
        if P[i] < snr*np.median(P[ok]): break
        df = f[1]-f[0]; best = None
        for fc in np.linspace(f[i]-df, f[i]+df, 41):
            A2 = _design(s, ws + [2*np.pi*fc]); e = x - A2 @ np.linalg.lstsq(A2, x, rcond=None)[0]; q = e@e
            if best is None or q < best[0]: best = (q, 2*np.pi*fc)
        ws.append(best[1])
    A = _design(s, ws); c = np.linalg.lstsq(A, x, rcond=None)[0]
    return x - A[:, 2:] @ c[2:]
def hac_trend(s, x, lag=None):
    """OLS slope with Newey-West standard error. Returns (slope, z, lag1_autocorr_of_detrended)."""
    s = np.asarray(s, float); t = (s-s.mean())/(s.std() or 1); n = len(t)
    X = np.column_stack([np.ones(n), t]); b = np.linalg.lstsq(X, x, rcond=None)[0]; e = x - X@b
    L = lag if lag is not None else int(ceil(4*(n/100)**(2/9)))*4
    u = t*e; S = u@u
    for k in range(1, L+1): S += 2*(1-k/(L+1))*(u[k:]@u[:-k])
    se = sqrt(S)/(t@t); rho = float((e[1:]@e[:-1])/(e@e)) if e@e > 0 else 0.0
    return float(b[1]), float(b[1]/se) if se > 0 else 0.0, rho
def kpss_trend(s, x, lag=None):
    """KPSS statistic vs trend-stationarity (1% critical value 0.216). Large => stochastic trend."""
    n = len(x); X = np.column_stack([np.ones(n), s-s.mean()]); e = x - X@np.linalg.lstsq(X, x, rcond=None)[0]
    L = lag if lag is not None else int(ceil(12*(n/100)**0.25)); S = e@e
    for k in range(1, L+1): S += 2*(1-k/(L+1))*(e[k:]@e[:-k])
    return float(np.sum(np.cumsum(e)**2)/(n**2*(S/n)))
KPSS_CRIT_1PCT = 0.216
def classify_drift(s, v, periods=None, alpha=0.01, source_flip=False, unit_root=0.97):
    """Secular-drift test on each raw channel + a variance channel, Bonferroni-corrected.
    Returns dict(classification in {null, candidate, inconclusive, invalid}, details)."""
    if source_flip: return {"classification": "invalid", "reason": "source flip"}
    s, v = validate(s, v); v = v.reshape(len(s), -1)
    periods = list(periods if periods is not None else FACILITY_PERIODS.values())
    chans, outliers, resid = [], 0, []
    for j in range(v.shape[1]):
        x, o = _winsorize(v[:, j]); outliers += o
        x = _remove_lines(s, x, periods); resid.append(x); chans.append(("mean[%d]" % j, x))
    # variance channel: log mean-square per block of detrended residuals
    B = 32; nb = len(s)//B; e2 = sum((r - np.polyval(np.polyfit(s, r, 1), s))**2 for r in resid)
    lv = np.log(e2[:nb*B].reshape(nb, B).mean(1) + 1e-300); sb = s[:nb*B].reshape(nb, B).mean(1)
    chans.append(("variance", lv))
    m = len(chans); rows = []; worst = None
    for name, x in chans:
        ss = sb if name == "variance" else s
        slope, z, rho = hac_trend(ss, x, lag=2 if name == "variance" else None)
        k = kpss_trend(ss, x) if name != "variance" else None
        p = min(1.0, _p_two_sided(z)*m); rows.append({"channel": name, "slope": slope, "z": z, "p_bonf": p, "rho1": rho, "kpss": k})
    sig = [r for r in rows if r["p_bonf"] < alpha]
    if any(r["kpss"] is not None and (r["kpss"] > KPSS_CRIT_1PCT or r["rho1"] > unit_root) for r in rows): cls = "inconclusive"
    else: cls = "candidate" if sig else "null"
    return {"classification": cls, "alpha": alpha, "outliers_clipped": outliers, "channels": rows}
