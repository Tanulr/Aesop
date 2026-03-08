"""Entry point for `python -m aesop`."""

from pathlib import Path

from aesop import create_presentation_from_storybrand_json


def main() -> None:
    """Run the StoryBrand example."""
    project_root = Path(__file__).resolve().parent.parent.parent
    examples_path = project_root / "examples" / "storybrand_example.json"
    if not examples_path.exists():
        # Fallback: check project root
        examples_path = project_root / "storybrand_example.json"
    with open(examples_path) as f:
        storybrand_json = f.read()
    url = create_presentation_from_storybrand_json(
        storybrand_json,
        title="StoryBrand Framework",
    )
    print(f"Created: {url}")


if __name__ == "__main__":
    main()
