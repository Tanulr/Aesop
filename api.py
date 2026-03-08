"""
FastAPI endpoints for Aesop presentation generation.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add backend to path so we can import run_agents
_backend_dir = Path(__file__).parent / "backend"
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from aesop import create_presentation_from_storybrand_json, create_presentation_from_strategy
from main import run_agents

app = FastAPI(title="Aesop API", description="Presentation generation from StoryBrand and prompts")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Credentials: use env vars on Cloud Run, defaults for local
CREDENTIALS_PATH = os.environ.get("AESOP_CREDENTIALS_PATH", "credentials.json")
TOKEN_PATH = os.environ.get("AESOP_TOKEN_PATH", "token.json")

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

    Runs the agent pipeline (brand analysis, ICP, StoryBrand strategy),
    then creates a Google Slides presentation with the first strategy.
    """
    def _run():
        orig_cwd = os.getcwd()
        try:
            os.chdir(_backend_dir)
            return run_agents([body.prompt])
        finally:
            os.chdir(orig_cwd)

    strategies = await asyncio.to_thread(_run)

    if not strategies:
        return {"url": "", "error": "Could not generate strategy from prompt"}

    strategy = strategies[0]
    url = await asyncio.to_thread(
        create_presentation_from_strategy,
        strategy,
        title=f"StoryBrand: {strategy.persona_name}",
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH,
    )
    return {"url": url}
