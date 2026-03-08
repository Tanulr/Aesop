"""Entry point for `python -m aesop`."""

from pathlib import Path

from aesop import create_presentation_from_strategy
from aesop.storybrand_schema import StoryBrandStrategy


def main() -> None:
    """Run the StoryBrand example: JSON -> Strategy -> Presentation with generated images."""
    project_root = Path(__file__).resolve().parent.parent.parent
    examples_path = project_root / "examples" / "storybrand_example.json"
    if not examples_path.exists():
        examples_path = project_root / "storybrand_example.json"
    with open(examples_path) as f:
        storybrand_json = f.read()
    strategy = StoryBrandStrategy.from_storybrand_json(storybrand_json)
    url = create_presentation_from_strategy(strategy, title="StoryBrand Framework")
    print(f"Created: {url}")


if __name__ == "__main__":
    main()
