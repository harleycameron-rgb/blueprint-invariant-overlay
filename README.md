# Blueprint Invariant Overlay

A dual-invariant measurement system for detecting drift across high-energy facility boundaries. It is falsifiable, reproducible and mechanism-agnostic: it supplies a test, not a mechanism.

## Components
- **Tusi-couple coherence overlay** — closed geometric frame (harmonic ratio 1.37:1, non-locking; concentric architecture; radial partitions; 260-dial invariant).
- **Daemon gate** — open environmental frame: local triad {u, n, e}, coherence trace, ring events, H and closure invariants, residual spectrum.
- **Differential frame** — drift-only signal ΔC(s) = C_gate(s) − C_tusi(s), with removal of facility harmonics (cryogenic, mains, beam pulse, RF cavity, diurnal).
- **Invariant Hash Block (IHB)** — hashes of all traces plus H, closure, ring count, timestamp and device hash, sealed by a **Sentinel_dot SHA-256**.
- **SVC wrapper** — metadata binding the blueprint image to geometry, invariants, seal, provenance and audit data.

## Quick start
```bash
pip install -e . pytest
pytest validation_suite
python -m blueprint_invariant.pipeline   # builds release/ bundle
```

## Classification
periodic → environmental → **null** · secular → **candidate** · source flip → **invalid**

See `docs/TECHNICAL_DATA.md`, `docs/REPLICATION_PROTOCOL.md` and `docs/compliance_report_template.json`. Licence: MIT.

## v1.0.2: signed seals and calibrated detector
```bash
pip install -e ".[signing]" pytest
export SENTINEL_DOT_SIGNING_KEY=writer.key   # sentinel_dot keygen --ed25519 writer
python -m blueprint_invariant.pipeline      # writes sentinel_sig.txt + signer.pub
```
Classification is now `null` / `candidate` / `inconclusive` / `invalid` from `classify_drift` (HAC trend test + KPSS). See `docs/RELEASE_NOTES_v1.0.2.md` for adversarial results and limits.
