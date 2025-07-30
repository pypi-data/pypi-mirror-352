# Schema for Image-to-Video generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal
from sunra_apispec.base.output_schema import VideoOutput

class ImageToVideoInput(BaseModel):
    """Input model for image-to-video generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        max_length=2500,
        description="Text prompt for video generation"
    )
    
    start_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="URL of the image to use as the first frame"
    )
    
    resolution: Literal["keep_ratio", "adaptive"] = Field(
        "adaptive",
        json_schema_extra={"x-sr-order": 401},
        description="Resolution of the video, keep_ratio means keep the aspect ratio of the input image, adaptive means adapt to the aspect ratio of the input image"
    )
    
    aspect_ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "9:21"] = Field(
        default=None,
        json_schema_extra={"x-sr-order": 402},
        description="Aspect ratio of the video"
    )
    
    duration: Literal[5, 10] = Field(
        5,
        json_schema_extra={"x-sr-order": 403},
        description="Duration of the video in seconds"
    )

    seed: int = Field(
        default=None,
        ge=-1,
        le=2**32-1,
        json_schema_extra={"x-sr-order": 404},
        description="Seed of the video generation"
    )


class Seedance10LiteI2VOutput(VideoOutput):
    output_video_tokens: int = Field(
        ...,
        description="Video output tokens",
    )
