from enum import Enum
from typing import Optional, List, Union

from pydantic import BaseModel, Field, field_validator


class ImageRequest(BaseModel):
    """Request model for image generation."""
    
    content: str = Field(
        description="The content to generate an image for"
    )
    platform: str = Field(
        description="The social media platform this image is intended for"
    )
    topic: str = Field(
        description="The main topic of the content"
    )
    style: str = Field(
        default="photorealistic",
        description="The style of the image to generate"
    )
    size: str = Field(
        default="1024x1024",
        description="Image size, one of 1024x1024, 1024x1792 or 1792x1024"
    )
    
    @field_validator('size')
    def validate_size(cls, v):
        """Validate image size."""
        valid_sizes = ["1024x1024", "1024x1792", "1792x1024"]
        if v not in valid_sizes:
            raise ValueError(f"Size must be one of {valid_sizes}")
        return v


class ImageResponse(BaseModel):
    """Response model for image generation."""
    
    image_path: str = Field(
        description="Local path to the generated image"
    )
    prompt: str = Field(
        description="The prompt used to generate the image"
    )
