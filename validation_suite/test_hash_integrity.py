from blueprint_invariant.invariant_hash import deterministic_hash
def test_hash(): assert deterministic_hash({"a":1})==deterministic_hash({"a":1})
