import hashlib, json
import numpy as np
from .schemas import IHB_REQUIRED_FIELDS
def _norm(o):
    if isinstance(o, np.ndarray): return np.round(o.astype(float), 12).tolist()
    if isinstance(o, (np.floating, np.integer)): return o.item()
    if isinstance(o, dict): return {k: _norm(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_norm(v) for v in o]
    return o
def deterministic_hash(o):
    return hashlib.sha256(json.dumps(_norm(o), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def build_ihb(tusi, gate, diff, spectrum, H, closure, ring_count, timestamp, device_id):
    ihb = {"tusi_trace_hash": deterministic_hash(tusi), "gate_trace_hash": deterministic_hash(gate),
           "differential_trace_hash": deterministic_hash(diff), "residual_spectrum_hash": deterministic_hash(spectrum),
           "H": round(float(H), 12), "closure": round(float(closure), 12), "ring_count": int(ring_count),
           "timestamp": timestamp, "device_hash": deterministic_hash(device_id)}
    assert set(ihb) == IHB_REQUIRED_FIELDS; return ihb
