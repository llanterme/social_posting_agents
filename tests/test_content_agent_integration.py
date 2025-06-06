"""Integration tests for the ContentAgent class."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from models import ContentRequest, PlatformType, ToneType
from agents import ContentAgent


class TestContentAgent:
    """Test suite for the ContentAgent class."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        with patch('openai.OpenAI') as mock_client:
            yield mock_client.return_value
    
    def test_generate_content_success(self, mock_openai_client):
        """Test successful content generation with valid API response."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test generated content #test #example"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Initialize the agent
        agent = ContentAgent(api_key="test_key")
        
        # Create a test request
        request = ContentRequest(
            facts=[{"fact": "Test fact", "source": "test"}],
            platform=PlatformType.TWITTER,
            tone=ToneType.INFORMATIVE
        )
        
        # Call the method under test
        response = agent.generate_content(request)
        
        # Assertions
        assert response.content == "Test generated content #test #example"
        assert response.platform == PlatformType.TWITTER
        assert response.tone == ToneType.INFORMATIVE
        assert response.length > 0
        
        # Verify the API was called with the correct parameters
        mock_openai_client.chat.completions.create.assert_called_once()
        _, kwargs = mock_openai_client.chat.completions.create.call_args
        assert kwargs["model"] == "gpt-4o"
        assert "Test fact" in kwargs["messages"][1]["content"]
    
    def test_generate_content_with_hashtags(self, mock_openai_client):
        """Test content generation with hashtag inclusion."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test content"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Initialize the agent
        agent = ContentAgent()
        
        # Create a test request with hashtags enabled
        request = ContentRequest(
            facts=[{"fact": "Test fact about technology", "source": "test"}],
            platform=PlatformType.TWITTER,
            include_hashtags=True
        )
        
        # Call the method under test
        response = agent.generate_content(request)
        
        # Should include hashtags in the response
        assert len(response.hashtags) > 0
    
    def test_generate_content_validation(self, mock_openai_client):
        """Test content validation with invalid input."""
        agent = ContentAgent()
        
        # Test with empty facts
        with pytest.raises(ValueError):
            agent.generate_content(ContentRequest(facts=[]))
        
        # Test with invalid platform
        with pytest.raises(ValueError):
            request = ContentRequest(
                facts=[{"fact": "Test"}],
                platform="invalid_platform"
            )
            agent.generate_content(request)
    
    def test_platform_specific_configs(self):
        """Test platform-specific configurations are applied correctly."""
        agent = ContentAgent()
        
        # Test Twitter config
        request = ContentRequest(
            facts=[{"fact": "Test"}],
            platform=PlatformType.TWITTER
        )
        assert "twitter" in agent._format_prompt(request).lower()
        
        # Test LinkedIn config
        request.platform = PlatformType.LINKEDIN
        assert "linkedin" in agent._format_prompt(request).lower()
