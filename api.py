"""
FastAPI endpoints for Aesop presentation generation.
"""

import json
import os

from fastapi import FastAPI
from pydantic import BaseModel

from aesop import create_presentation_from_storybrand_json

app = FastAPI(title="Aesop API", description="Presentation generation from StoryBrand and prompts")

# Credentials: use env vars on Cloud Run, defaults for local
CREDENTIALS_PATH = os.environ.get("AESOP_CREDENTIALS_PATH", "credentials.json")
TOKEN_PATH = os.environ.get("AESOP_TOKEN_PATH", "token.json")

# Dummy link for prompt endpoint until wired up
DUMMY_SLIDES_LINK = "https://docs.google.com/presentation/d/DUMMY_ID/edit"


class PromptRequest(BaseModel):
    """Request body for the prompt endpoint."""

    prompt: str


@app.post("/presentations/storybrand")
async def create_from_story_schema(schema: dict) -> dict[str, str]:
    """Create a presentation from a StoryBrand schema JSON.

    Accepts the StoryBrand schema as a JSON object (slides keyed by id
    with title, description, image_url per slide). Returns the created
    presentation URL.
    """
    json_str = json.dumps(schema)
    url = create_presentation_from_storybrand_json(
        json_str,
        title="StoryBrand Presentation",
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH,
    )
    return {"url": url}


@app.post("/presentations/from-prompt")
async def create_from_prompt(body: PromptRequest) -> dict[str, str]:
    """Create a presentation from a brand description prompt.

    Accepts a prompt (brand description). Returns a link.
    Uses a dummy link for now—will be wired up later.
    """
    # TODO: Wire up LLM + presentation generation
    _ = body.prompt
    return {"url": DUMMY_SLIDES_LINK}
