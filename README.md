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

# Run the API server
uvicorn api:app --reload
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for deploying to Google Cloud Run.

### API Endpoints

- **POST `/presentations/storybrand`** – Accepts StoryBrand schema JSON, creates a presentation, returns the URL.
- **POST `/presentations/from-prompt`** – Accepts `{"prompt": "brand description"}`, returns a link (dummy for now).

Or use the API programmatically:

```python
from aesop import create_presentation_from_storybrand_json, SlideContent, create_presentation

# From StoryBrand JSON
with open("examples/storybrand_example.json") as f:
    url = create_presentation_from_storybrand_json(f.read(), title="My Presentation")
```
