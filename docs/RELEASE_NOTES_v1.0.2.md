# Release Notes — v1.0.2

## Overview
Adversarial-hardening release. The v1.0.1 detector had no measurable power (detection rate ≈ false-positive rate ≈ 16–25%, independent of drift size) and the seal was an unkeyed SHA-256 that any editor could recompute. Both are fixed.

## Seal: sentinel_dot signatures
- `sentinel_dot.sign()` / `verify_signed()` sign the IHB seal with the author's sentinel_dot signer (Ed25519, ML-DSA or hybrid) — authorised direct extension of sentinel_dot v0.3.0.
- `build_release` signs when `SENTINEL_DOT_SIGNING_KEY` (PEM path) is set; writes `sentinel_sig.txt`, `signer.pub`, and binds both into `blueprint.svc`.
- Optional OpenTimestamps anchoring of `manifest.json` (`BLUEPRINT_ANCHOR=1`, needs `ots`).
- `verify()` (unsigned) is retained and documented as integrity-only.
- `package_sha256.txt` now uses `sha256sum -c` format. `sentinel_sha256.txt` stays a bare digest because it hashes canonical JSON, not file bytes (verify with `sentinel_dot.verify`).

## Detector: `classify_drift`
- Operates on raw gate channels (the coherence trace cancels slow drift).
- Joint fit of offset + trend + facility lines + up to 6 frequency-refined unknown lines (period < T/2).
- Newey–West (HAC) trend test per channel plus a log-variance channel, Bonferroni-corrected, α = 0.01.
- KPSS trend-stationarity check → `inconclusive` for stochastic trends (random walks, steps).
- Rejects NaN/inf, non-monotonic time, n < 64. Outliers winsorised at 8·MAD.
- `source_flip=True` → `invalid`.

## Adversarial results (synthetic, n = 4096, dt = 60 s)
| Scenario | v1.0.1 candidate | v1.0.2 candidate |
|---|---|---|
| Noise only (300 seeds) | 25% | 1.7% (inconclusive 2.7%) |
| Drift 0.002 | ~16% | 72% |
| Drift 0.005 | ~16% | 96% |
| Drift 0.1 | 14% | 96% |
| Unknown 7 h / 20 h line | 18% | 0–2% |
| Random walk | 16% | 8% (92% inconclusive) |
| Single 50σ spike | null | null |
| Counter-drift across channels | null | candidate |
| NaN input | null (silent) | ValueError |
| Forged IHB + recomputed seal | verifies | signature fails |

## Known limits
- Periodic signals with period > T/2 are indistinguishable from secular drift within one run (96 h line in a 68 h run → candidate/inconclusive). Mitigate with longer runs or by adding the period to `FACILITY_PERIODS`.
- Calibration is on synthetic Gaussian noise; recalibrate α on real null runs before claims.
- The legacy `classify()` (coherence-trace) is retained for compatibility only; `measure()` now uses `classify_drift`.
