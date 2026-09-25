import hashlib
def sentinel_sha256(s): return hashlib.sha256(s.encode()).hexdigest()
