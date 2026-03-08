"""
Aesop - Google Slides presentation builder with StoryBrand support.
"""

from aesop.slides_builder import (
    SlideContent,
    create_presentation,
    create_presentation_from_storybrand_json,
    create_presentation_from_strategy,
    strategy_to_slide_content,
)
from aesop.storybrand_schema import StoryBrandSchema, StoryBrandSlide, StoryBrandStrategy

__all__ = [
    "SlideContent",
    "StoryBrandSchema",
    "StoryBrandSlide",
    "StoryBrandStrategy",
    "create_presentation",
    "create_presentation_from_storybrand_json",
    "create_presentation_from_strategy",
    "strategy_to_slide_content",
]
