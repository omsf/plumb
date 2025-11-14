# Developer documentation

## Installation

`plumbdb` can currently only be installed via its python source with its dependencies handled by `conda`.

```bash
conda create -n plumbdb_dev -f env.yaml
conda activate plumbdb_dev
pip install -e ".[dev]"
```

## Running tests

Tests are performed with [`pytest`](https://docs.pytest.org/), which is automatically installed as part of the `test` dependency group specified in `pyproject.toml`. With the test environment active and from within `plumb/pkg/`, run:

```bash
python -m pytest src/
```