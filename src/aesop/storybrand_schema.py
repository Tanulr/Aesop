"""
StoryBrand framework schema for presentation content.

Matches the schema in storybrand_example.json: a collection of slides
keyed by identifiers (e.g. "1_A_Character") with title, description, and image_url.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


@dataclass
class StoryBrandSlide:
    """A single slide in the StoryBrand framework.

    Attributes:
        slide_id: Unique identifier for the slide (e.g. "1_A_Character").
        title: Slide title.
        description: Body/description text.
        image_url: Optional image URL (empty string if none).
    """

    title: str
    description: str
    image_description: str = ""


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

# Hardcoded slide titles matching storybrand_example.json
STORYBRAND_SLIDE_TITLES = [
    "Your Customer Is the Hero",
    "Identify the Obstacles",
    "Your Brand as the Guide",
    "A Simple Path Forward",
    "The Call to Action",
    "Paint the Picture of Success",
    "The Stakes—What's at Risk",
]

# JSON key to strategy field mapping (ordered for slide 1-7)
_JSON_TO_STEP = [
    ("1_A_Character", "step_1_character"),
    ("2_Has_a_Problem", "step_2_problem"),
    ("3_Meets_a_Guide", "step_3_guide"),
    ("4_Who_Gives_Them_a_Plan", "step_4_plan"),
    ("5_That_Calls_Them_to_Action", "step_5_action"),
    ("6_That_Ends_in_Success", "step_7_success"),
    ("7_And_Helps_Them_Avoid_Failure", "step_6_failure"),
]



class StoryBrandStrategy(BaseModel):
    persona_name: str = Field(description="The name of the persona this strategy applies to.")
    step_1_character: str = Field(description="Identify what the customer wants in 1-2 short sentences.")
    step_2_problem: str = Field(description="Define their external, internal, and philosophical frustrations.")
    step_3_guide: str = Field(description="Position the brand as the guide with Empathy and Authority.")
    step_4_plan: str = Field(description="Provide a clear 3-4 step process or agreement plan to reduce their fear of buying.")
    step_5_action: str = Field(description="Use clear Direct (Buy Now) and Transitional (Free Trial/Lead Magnet) Call To Actions (CTAs).")
    step_6_failure: str = Field(description="Explicitly state the negative consequences of inaction if they don't buy.")

    @classmethod
    def from_storybrand_json(
        cls, json_str: str, persona_name: str = "Customer"
    ) -> "StoryBrandStrategy":
        """Parse storybrand_example.json format into a StoryBrandStrategy.

        Args:
            json_str: JSON string with slides keyed by 1_A_Character, etc.
            persona_name: Persona name for the strategy.

        Returns:
            StoryBrandStrategy populated from the JSON descriptions.
        """
        data = json.loads(json_str)
        step_values = {}
        for json_key, step_field in _JSON_TO_STEP:
            step_values[step_field] = data.get(json_key, {}).get("description", "")
        return cls(persona_name=persona_name, **step_values)

    @classmethod
    def generate_image_for_step(cls, step_description: str, size: str = "256x256") -> str:
        """Generate a low-resolution image for a presentation from a step description.

        Args:
            step_description: Content of one step (e.g. strategy.step_1_character).
            size: Image size. Default "256x256". Options: "256x256", "512x512".

        Returns:
            URL of the generated image, or placeholder if OPENAI_API_KEY is not set.
        """
        from aesop.image_generator import generate_step_image
        return generate_step_image(step_description, size=size)

    step_7_success: str = Field(description="Paint a picture of the customer’s life transformed after using the product.")