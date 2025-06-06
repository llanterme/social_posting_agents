"""Integration tests for the ResearchAgent class."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from models import ResearchRequest, Fact
from agents import ResearchAgent


class TestResearchAgent:
    """Test suite for the ResearchAgent class."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        with patch('openai.OpenAI') as mock_client:
            yield mock_client.return_value
    
    def test_research_success(self, mock_openai_client):
        """Test successful research with valid API response."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "facts": [
                {
                    "fact": "Test fact 1",
                    "source": "https://example.com/1",
                    "relevance_score": 0.9
                },
                {
                    "fact": "Test fact 2",
                    "source": "https://example.com/2",
                    "relevance_score": 0.8
                }
            ]
        }
        '''
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Initialize the agent
        agent = ResearchAgent(api_key="test_key")
        
        # Create a test request
        request = ResearchRequest(
            topic="Test Topic",
            max_facts=2,
            min_relevance=0.7
        )
        
        # Call the method under test
        response = agent.research(request)
        
        # Assertions
        assert response.topic == "Test Topic"
        assert len(response.facts) == 2
        assert all(isinstance(fact, Fact) for fact in response.facts)
        assert len(response.search_queries) > 0
        assert response.timestamp is not None
        
        # Verify the API was called with the correct parameters
        mock_openai_client.chat.completions.create.assert_called_once()
        _, kwargs = mock_openai_client.chat.completions.create.call_args
        assert kwargs["model"] == "gpt-4o"
        assert "Test Topic" in kwargs["messages"][1]["content"]
    
    def test_research_with_invalid_facts(self, mock_openai_client):
        """Test research with invalid fact data in the response."""
        # Mock the API response with some invalid facts
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "facts": [
                {"fact": "Valid fact", "source": "https://example.com/1", "relevance_score": 0.9},
                {"fact": "Missing source", "relevance_score": 0.8},
                {"source": "https://example.com/3", "relevance_score": 0.7},
                {"fact": "Invalid score", "source": "https://example.com/4", "relevance_score": 1.5}
            ]
        }
        '''
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Initialize the agent
        agent = ResearchAgent()
        request = ResearchRequest(topic="Test Topic")
        
        # Call the method under test
        response = agent.research(request)
        
        # Only the valid fact should be included
        assert len(response.facts) == 1
        assert response.facts[0].fact == "Valid fact"
    
    def test_research_with_empty_response(self, mock_openai_client):
        """Test research with empty or invalid API response."""
        # Mock an empty response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{}'
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        agent = ResearchAgent()
        request = ResearchRequest(topic="Test Topic")
        
        # Should not raise an exception
        response = agent.research(request)
        assert len(response.facts) == 0
    
    def test_research_with_invalid_json(self, mock_openai_client):
        """Test research with invalid JSON in the API response."""
        # Mock an invalid JSON response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = 'not a valid json'
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        agent = ResearchAgent()
        request = ResearchRequest(topic="Test Topic")
        
        # Should raise a ValueError for invalid JSON
        with pytest.raises(ValueError, match="Invalid response format"):
            agent.research(request)
    
    def test_generate_search_queries(self):
        """Test the search query generation."""
        agent = ResearchAgent()
        queries = agent._generate_search_queries("Quantum Computing")
        
        assert len(queries) == 3
        assert all("Quantum Computing" in query for query in queries)
        assert isinstance(queries, list)
        assert all(isinstance(query, str) for query in queries)
