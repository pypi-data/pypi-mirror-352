# Schema for Text-to-Image generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


class BaseInput(BaseModel):
    """Input model for text-to-image generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        description="Text prompt for image generation.",
    )
    prompt_enhancer: bool = Field(
        default=False,
        json_schema_extra={"x-sr-order": 201},
        description="Whether to perform enhancer on the prompt. If active, automatically modifies the prompt for more creative generation."
    )
    seed: int = Field(
        default=None,
        json_schema_extra={"x-sr-order": 202},
        description="Seed for reproducibility.",
        examples=[42]
    )
    aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"] = Field(
        default="16:9",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio of the image between 21:9 and 9:21."
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        json_schema_extra={"x-sr-order": 404},
        description="Output format for the generated image. Can be 'jpeg' or 'png'."
    )
  

class TextToImageInput(BaseInput):
    """Input model for text-to-image generation."""
    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=6,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 500},
        description="Tolerance level for input and output moderation. Between 0 and 6, 0 being most strict, 6 being no moderation.",
    )


class ImageToImageInput(BaseInput):
    """Input model for image-to-image generation."""
    image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Image URL to use for image-to-image generation."
    )

    safety_tolerance: int = Field(
        default=2,
        ge=0,
        le=2,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 500},
        description="Tolerance level for input and output moderation. Between 0 and 2, 0 being most strict.",
    )