import hashlib,json
def deterministic_hash(o):
 return hashlib.sha256(json.dumps(o,sort_keys=True).encode()).hexdigest()
