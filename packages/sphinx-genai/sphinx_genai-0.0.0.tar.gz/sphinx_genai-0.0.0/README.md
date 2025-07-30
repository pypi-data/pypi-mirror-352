# sphinx-genai

## Setup

```
python3 -m venv venv
. venv/bin/activate.fish
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

## Build

```
python3 -m build
```

## Test

```
python3 -m unittest
```

## Distribute

### TestPyPI

```
python3 -m twine upload --repository testpypi dist/*
```

### PyPI

```
python3 -m twine upload dist/*
```
