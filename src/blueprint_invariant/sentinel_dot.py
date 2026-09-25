import hashlib
from .invariant_hash import deterministic_hash
def sentinel_sha256(s): return hashlib.sha256(s.encode()).hexdigest()
def seal(ihb): return deterministic_hash(ihb)
def verify(ihb, sentinel): return seal(ihb) == sentinel
