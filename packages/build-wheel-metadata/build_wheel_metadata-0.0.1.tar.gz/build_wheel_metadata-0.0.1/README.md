# Build-Wheel-Metadata

![PyPI](https://img.shields.io/pypi/v/build-wheel-metadata)
![PyPI - License](https://img.shields.io/pypi/l/build-wheel-metadata)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/build-wheel-metadata)
![Tests](https://github.com/dhiahmila/build-wheel-metadata/actions/workflows/quality.yaml/badge.svg)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Module to prepare a python package distribution metadata.

## Quick Start

```bash
pip install build-wheel-metadata
```

## Usage

```python
from build_wheel_metadata import prepare_metadata

metadata = prepare_metadata(
    project_root.as_posix(), isolate=True
)


print(metadata)
```

Result:

```json
{
  "Author": "Dhia Hmila",
  "Classifier": "Intended Audience :: Developers",
  "Description": "...",
  "Description-Content-Type": "text/markdown",
  "License": "MIT License",
  "Metadata-Version": "2.4",
  "Name": "build-wheel-metadata",
  "Project-URL": "Repository, https://github.com/dhiahmila/build-wheel-metadata",
  "Requires-Dist": "build>=1.2.2.post1",
  "Requires-Python": ">=3.9",
  "Summary": "Module to prepare a python package distribution metadata.",
  "Version": "0.0.1"
}
```
