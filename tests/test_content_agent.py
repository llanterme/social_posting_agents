"""Unit tests for the Content Agent models and functionality."""
import pytest
from datetime import datetime
from pydantic import ValidationError

from models import ContentRequest, ContentResponse, PlatformType, ToneType


def test_content_request_validation():
    """Test that ContentRequest model validates input correctly."""
    # Valid request
    valid_request = ContentRequest(
        facts=[{"fact": "Test fact", "source": "test"}],
        platform=PlatformType.TWITTER,
        tone=ToneType.INFORMATIVE,
        max_length=280
    )
    assert valid_request.platform == PlatformType.TWITTER
    assert valid_request.tone == ToneType.INFORMATIVE

    # Test invalid platform
    with pytest.raises(ValidationError):
        ContentRequest(
            facts=[{"fact": "Test fact"}],
            platform="invalid_platform"
        )

    # Test empty facts
    with pytest.raises(ValidationError):
        ContentRequest(facts=[])


def test_content_response_creation():
    """Test creation and properties of ContentResponse."""
    response = ContentResponse(
        content="Test content",
        platform=PlatformType.TWITTER,
        tone=ToneType.INFORMATIVE,
        length=12,
        hashtags=["#test"],
        created_at="2023-01-01T12:00:00Z"
    )
    
    assert response.content == "Test content"
    assert response.platform == PlatformType.TWITTER
    assert response.word_count == 2  # "Test content" is 2 words
