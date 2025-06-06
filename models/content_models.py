"""Pydantic models for the Content Agent component."""
from typing import List, Literal, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ToneType(str, Enum):
    """Available tone options for content generation."""
    INFORMATIVE = "informative"
    PERSUASIVE = "persuasive"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    ENTHUSIASTIC = "enthusiastic"


class PlatformType(str, Enum):
    """Supported social media platforms."""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    BLOG = "blog"


class ContentRequest(BaseModel):
    """Input model for the Content Agent."""
    facts: List[dict] = Field(
        ...,
        description="List of facts to include in the content"
    )
    platform: PlatformType = Field(
        default=PlatformType.TWITTER,
        description="Target platform for the content"
    )
    tone: ToneType = Field(
        default=ToneType.INFORMATIVE,
        description="Desired tone for the content"
    )
    max_length: int = Field(
        default=280,
        ge=50,
        le=2000,
        description="Maximum length of the generated content in characters"
    )
    include_hashtags: bool = Field(
        default=True,
        description="Whether to include relevant hashtags"
    )
    call_to_action: Optional[str] = Field(
        default=None,
        description="Optional call to action to include at the end"
    )

    @field_validator('facts')
    def validate_facts(cls, v):
        """Ensure facts is a non-empty list."""
        if not v:
            raise ValueError("At least one fact is required")
        return v


class ContentResponse(BaseModel):
    """Output model for the Content Agent."""
    content: str = Field(..., description="Generated content text")
    platform: PlatformType = Field(..., description="Target platform")
    tone: ToneType = Field(..., description="Used tone")
    length: int = Field(..., description="Length of the content in characters")
    hashtags: List[str] = Field(
        default_factory=list,
        description="List of included hashtags"
    )
    created_at: str = Field(
        ...,
        description="ISO 8601 timestamp of content creation"
    )
    
    @property
    def word_count(self) -> int:
        """Return the approximate word count of the content."""
        return len(self.content.split())
