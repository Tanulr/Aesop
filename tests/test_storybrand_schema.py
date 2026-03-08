"""Tests for the StoryBrand schema."""

import pytest

from aesop.storybrand_schema import StoryBrandSchema, StoryBrandSlide


def test_from_json_parses_schema() -> None:
    """StoryBrandSchema.from_json parses valid JSON."""
    json_str = '''
    {
        "2_B": {"title": "Two", "description": "Desc two", "image_url": ""},
        "1_A": {"title": "One", "description": "Desc one", "image_url": "https://example.com/img.png"}
    }
    '''
    schema = StoryBrandSchema.from_json(json_str)
    assert len(schema.slides) == 2
    # Sorted by key, so 1_A then 2_B
    assert schema.slides[0].slide_id == "1_A"
    assert schema.slides[0].title == "One"
    assert schema.slides[0].description == "Desc one"
    assert schema.slides[0].image_url == "https://example.com/img.png"
    assert schema.slides[1].slide_id == "2_B"
    assert schema.slides[1].title == "Two"


def test_from_json_handles_missing_fields() -> None:
    """Missing fields get default values."""
    json_str = '{"slide_1": {}}'
    schema = StoryBrandSchema.from_json(json_str)
    assert schema.slides[0].title == ""
    assert schema.slides[0].description == ""
    assert schema.slides[0].image_url == ""
