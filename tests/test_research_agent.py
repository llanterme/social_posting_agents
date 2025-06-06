"""Unit tests for the Research Agent models and functionality."""
import pytest
from datetime import datetime
from pydantic import ValidationError

from models.research_models import Fact, ResearchRequest, ResearchResponse


def test_fact_validation():
    """Test that Fact model validates input correctly."""
    # Valid fact
    valid_fact = Fact(
        fact="Electric cars produce zero tailpipe emissions.",
        source="https://www.epa.gov/greenvehicles/electric-vehicle-myths",
        relevance_score=0.9
    )
    assert valid_fact.fact == "Electric cars produce zero tailpipe emissions."
    assert valid_fact.relevance_score == 0.9

    # Test invalid relevance score
    with pytest.raises(ValidationError):
        Fact(
            fact="Test fact",
            source="https://example.com",
            relevance_score=1.1  # Above maximum allowed
        )


def test_research_request_defaults():
    """Test ResearchRequest default values and validation."""
    request = ResearchRequest(topic="Renewable Energy")
    assert request.topic == "Renewable Energy"
    assert request.max_facts == 5  # Default value
    assert request.min_relevance == 0.7  # Default value

    # Test bounds validation
    with pytest.raises(ValidationError):
        ResearchRequest(topic="Test", max_facts=0)  # Below minimum
    
    with pytest.raises(ValidationError):
        ResearchRequest(topic="Test", min_relevance=1.1)  # Above maximum


def test_research_response_creation():
    """Test creation and properties of ResearchResponse."""
    facts = [
        Fact(
            fact="Solar power is a renewable energy source.",
            source="https://www.energy.gov/eere/solar/solar-energy-wind",
            relevance_score=0.9
        ),
        Fact(
            fact="Wind turbines can generate electricity.",
            source="https://www.energy.gov/eere/wind/how-do-wind-turbines-work",
            relevance_score=0.8
        )
    ]
    
    response = ResearchResponse(
        topic="Renewable Energy",
        facts=facts,
        search_queries=["renewable energy sources", "solar and wind power"],
        timestamp="2023-01-01T12:00:00Z"
    )
    
    assert response.topic == "Renewable Energy"
    assert len(response.facts) == 2
    assert len(response.search_queries) == 2
    assert len(response.relevant_facts) == 2  # Both facts meet default 0.7 threshold


def test_research_response_relevant_facts():
    """Test the relevant_facts property filters correctly."""
    facts = [
        Fact(fact="High relevance", source="https://example.com/1", relevance_score=0.9),
        Fact(fact="Low relevance", source="https://example.com/2", relevance_score=0.6),
        Fact(fact="Medium relevance", source="https://example.com/3", relevance_score=0.8)
    ]
    
    response = ResearchResponse(
        topic="Test Topic",
        facts=facts,
        search_queries=["test query"],
        timestamp="2023-01-01T12:00:00Z"
    )
    
    # Only facts with relevance >= 0.7 should be included
    relevant = response.relevant_facts
    assert len(relevant) == 2
    assert all(fact.relevance_score >= 0.7 for fact in relevant)
    assert "High relevance" in [f.fact for f in relevant]
    assert "Medium relevance" in [f.fact for f in relevant]
    assert "Low relevance" not in [f.fact for f in relevant]
