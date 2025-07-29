# esrf-pathlib

*esrf-pathlib* provides a drop-in clone of Python’s `pathlib` with ESRF-specific path utilities.

## Install

```bash
pip install esrf-pathlib
```

## Getting started

```python
from esrf_pathlib import Path
```

# Use your new ESRF-aware Path

```python
path = Path("/data/visitor/proposal/beamline/20250202")
print("Proposal:", path.proposal)
```

## Contributing

See CONTRIBUTING.md