"""SVC metadata wrapper binding blueprint image to IHB."""
import hashlib
from .orrery import RATIO, DIALS, radial_partitions
def build_svc(image_bytes, ihb, sentinel, version="1.0.2", signature=None, public_key=None):
    return {"format": "SVC/1", "version": version,
            "geometry": {"frame": "tusi_couple", "ratio": RATIO, "dials": DIALS, "partitions": radial_partitions()},
            "invariants": {k: ihb[k] for k in ("H", "closure", "ring_count")},
            "binding": {"image_sha256": hashlib.sha256(image_bytes).hexdigest(), "sentinel_sha256": sentinel,
                        "sentinel_signature": signature, "signer_public_key": public_key},
            "provenance": {"generator": "blueprint_invariant", "timestamp": ihb["timestamp"]},
            "audit": {"device_hash": ihb["device_hash"]}}
