# Release Notes — v1.0.1

## Overview
Patch release: the release bundle is now fully self-contained.

## Changes
- Bundle includes the full `blueprint_invariant` package (`src/`), `pyproject.toml`, `LICENSE`, `CITATION.cff` and all docs.
- Validation suite runs cleanly from the unzipped bundle (`pip install -e . pytest && pytest validation_suite`).
- No `__pycache__` or build clutter in the bundle.
- Fix (carried from v1.0.0 post-tag): Tusi-frame 1.37 harmonic removed from the residual; injected-drift test added.

## Versioning
Current version: v1.0.1
