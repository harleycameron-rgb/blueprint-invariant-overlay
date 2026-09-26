# Blueprint Invariant Overlay

A measurement and analysis system providing reproducible and falsifiable tests for invariant properties.

## Citation

If you use this project in your research or work, please cite it as:

```bibtex
@software{cameron2026blueprint,
  title={Blueprint Invariant Overlay},
  author={Cameron, Harley},
  url={https://github.com/harleycameron-rgb/blueprint-invariant-overlay},
  year={2026}
}
```

Or use the [CITATION.cff](CITATION.cff) file for citation metadata.

## Overview

Blueprint Invariant Overlay is a precision measurement system designed for applications requiring:

- **Falsifiability** — Clear, testable criteria for validation
- **Reproducibility** — Independent verification and replication
- **Auditability** — Cryptographically sealed audit trails
- **Precision** — High-fidelity measurement and analysis

## Quick Start

```bash
pip install -e .
pytest validation_suite
python -m blueprint_invariant.pipeline
```

## Development & Testing

```bash
pip install -e ".[dev]"
pytest validation_suite
```

## Documentation

For detailed technical documentation and specifications, see the `docs/` directory.

## License

MIT. See [LICENSE](LICENSE).

## Archive & Deposit

This project is archived and preserved at:
- **Zenodo**: [Link to be added upon deposit]

## Contact

For questions or inquiries about this project, please open an [issue](https://github.com/harleycameron-rgb/blueprint-invariant-overlay/issues) on GitHub.