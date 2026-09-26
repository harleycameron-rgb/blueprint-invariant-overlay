import pytest
signing = pytest.importorskip("sentinel_dot.signing")
from blueprint_invariant import pipeline as p, sentinel_dot as sd
def _setup():
    s, v = p.synthetic(); ihb, _, _ = p.measure(s, v)
    k = signing.Signer.generate("ed25519"); return ihb, k, signing.Verifier.from_pem(k.public_pem())
def test_genuine_verifies():
    ihb, k, ver = _setup(); _, sig = sd.sign(ihb, k); assert sd.verify_signed(ihb, sig, ver)
def test_forged_block_with_recomputed_seal_fails():
    ihb, k, ver = _setup(); _, sig = sd.sign(ihb, k)
    f = dict(ihb); f["ring_count"] += 5
    assert sd.verify(f, sd.seal(f))            # unkeyed check is fooled
    assert not sd.verify_signed(f, sig, ver)   # signature is not
def test_attacker_own_key_fails():
    ihb, k, ver = _setup(); f = dict(ihb); f["H"] = 0.5
    _, sig = sd.sign(f, signing.Signer.generate("ed25519")); assert not sd.verify_signed(f, sig, ver)
def test_release_is_signed(tmp_path):
    import json, pathlib
    k = signing.Signer.generate("ed25519"); root = pathlib.Path(__file__).resolve().parents[1]
    out, seal, _, _ = p.build_release(tmp_path/"rel", root, signer=k)
    ihb = json.loads((out/"invariant_hash_block.json").read_text())
    ver = signing.Verifier.from_pem((out/"signer.pub").read_bytes())
    assert sd.verify_signed(ihb, (out/"sentinel_sig.txt").read_text().strip(), ver)
    assert json.loads((out/"blueprint.svc").read_text())["binding"]["sentinel_signature"]
