# Aesop

An AI marketing agent that creates engaging brand marketing strategies and marketing material using storytelling principles.

## Project Structure

```
Aesop/
├── src/aesop/           # Main package
│   ├── __init__.py
│   ├── __main__.py      # Entry point for `python -m aesop`
│   ├── slides_builder.py
│   └── storybrand_schema.py
├── tests/
├── examples/
│   └── storybrand_example.json
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Installation

```bash
pip install -e .
# or with dev dependencies (pytest)
pip install -e ".[dev]"
```

## Usage

```bash
# Create a presentation from the StoryBrand example
python -m aesop
```

Or use the API:

```python
from aesop import create_presentation_from_storybrand_json, SlideContent, create_presentation

# From StoryBrand JSON
with open("examples/storybrand_example.json") as f:
    url = create_presentation_from_storybrand_json(f.read(), title="My Presentation")
```
