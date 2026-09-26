"""IHB seal. Digest = deterministic SHA-256; authenticity = sentinel_dot signature (Ed25519 / ML-DSA / hybrid)."""
import hashlib
from .invariant_hash import deterministic_hash
def sentinel_sha256(s): return hashlib.sha256(s.encode()).hexdigest()
def seal(ihb): return deterministic_hash(ihb)
def verify(ihb, sentinel):
    """Integrity only: detects accidental corruption, NOT forgery."""
    return seal(ihb) == sentinel
def sign(ihb, signer):
    """signer: sentinel_dot.signing.Signer. Returns (seal, signature_hex)."""
    s = seal(ihb); return s, signer.sign(s)
def verify_signed(ihb, signature_hex, verifier):
    """Authenticity: only the private-key holder can produce a passing signature."""
    return verifier.verify(seal(ihb), signature_hex)
