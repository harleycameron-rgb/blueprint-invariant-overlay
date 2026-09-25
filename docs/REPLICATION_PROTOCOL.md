# Replication Protocol — Blueprint Invariant Overlay v1.0.0

## Setup
Two synchronized devices:
- **Inside ring** — within the facility boundary
- **Outside ring** — beyond the facility boundary

Clocks synchronized to UTC; identical firmware and pipeline version (v1.0.0).

## Duration
7–30 days continuous, covering at least one full cryogenic cycle and multiple diurnal cycles.

## Data logged (per device)
- H, closure
- Ring count
- Coherence traces
- Tusi traces
- Differential traces
- Residual spectra
- Source (magnetic / solar)

## Procedure
1. Run `python -m blueprint_invariant.pipeline` on each device's data.
2. Remove facility periodic terms (cryogenic, mains, beam pulse, RF cavity, diurnal).
3. Seal each run: IHB + Sentinel_dot SHA-256.
4. Complete `compliance_report_template.json` with both devices' hashes and invariants.

## Classification
- **Periodic** → environmental → **null**
- **Secular** → **candidate**
- **Source flip** → **invalid**

A candidate requires a secular residual present inside and absent (or distinct) outside, with matching source on both devices.
