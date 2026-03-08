"""
StoryBrand framework schema for presentation content.

Matches the schema in storybrand_example.json: a collection of slides
keyed by identifiers (e.g. "1_A_Character") with title, description, and image_url.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class StoryBrandSlide:
    """A single slide in the StoryBrand framework.

    Attributes:
        slide_id: Unique identifier for the slide (e.g. "1_A_Character").
        title: Slide title.
        description: Body/description text.
        image_url: Optional image URL (empty string if none).
    """

    slide_id: str
    title: str
    description: str
    image_url: str = ""


@dataclass
class StoryBrandSchema:
    """StoryBrand presentation schema—a collection of slides in order.

    Attributes:
        slides: List of StoryBrandSlide, ordered by slide_id (1_, 2_, etc.).
    """

    slides: list[StoryBrandSlide] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_str: str) -> StoryBrandSchema:
        """Parse a JSON string into a StoryBrandSchema.

        Args:
            json_str: JSON string with slide objects keyed by slide_id.

        Returns:
            StoryBrandSchema populated from the JSON.
        """
        data = json.loads(json_str)
        slides = []
        for slide_id, slide_data in sorted(data.items()):
            slides.append(
                StoryBrandSlide(
                    slide_id=slide_id,
                    title=slide_data.get("title", ""),
                    description=slide_data.get("description", ""),
                    image_url=slide_data.get("image_url", ""),
                )
            )
        return cls(slides=slides)
