"""
Generate low-resolution images for StoryBrand presentation steps.
"""

from __future__ import annotations

import os


def generate_step_image(description: str, size: str = "256x256") -> str:
    """Generate a low-resolution image from a step description.

    Uses OpenAI DALL·E 2 when OPENAI_API_KEY is set. Returns a placeholder
    URL otherwise so the presentation flow is not broken.

    Args:
        description: Text description of the StoryBrand step (e.g. step content).
        size: Image dimensions. Use "256x256" for low-res, "512x512" for medium.

    Returns:
        URL of the generated or placeholder image.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return _placeholder_image_url(description)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.images.generate(
            model="dall-e-2",
            prompt=_to_image_prompt(description),
            size=size,
            n=1,
        )
        return response.data[0].url or ""
    except Exception:
        return _placeholder_image_url(description)


def _to_image_prompt(description: str) -> str:
    """Convert step description to an image generation prompt."""
    return (
        f"Simple, professional illustration for a business presentation slide. "
        f"Minimalist style, soft colors. Theme: {description[:500]}"
    )


def _placeholder_image_url(description: str) -> str:
    """Return a placeholder when generation is unavailable."""
    # Use placehold.co with a hash of the description for consistent per-step placeholders
    seed = abs(hash(description)) % 100000
    return f"https://placehold.co/256x256/e8e8e8/666?text=Step+{seed}"
