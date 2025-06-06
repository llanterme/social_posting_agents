"""Pydantic models for the Research Agent component."""
from typing import List, Optional
from pydantic import BaseModel, Field


class Fact(BaseModel):
    """A single fact about the research topic with its source."""
    fact: str = Field(..., description="A single, verifiable fact about the topic")
    source: str = Field(..., description="Source URL or reference for the fact")
    relevance_score: float = Field(
        ..., 
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 to 1.0) indicating fact's relevance to the topic"
    )


class ResearchRequest(BaseModel):
    """Input model for the Research Agent."""
    topic: str = Field(..., description="The topic to research")
    max_facts: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of facts to return"
    )
    min_relevance: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score for including facts"
    )


class ResearchResponse(BaseModel):
    """Output model for the Research Agent."""
    topic: str = Field(..., description="The researched topic")
    facts: List[Fact] = Field(..., description="List of relevant facts about the topic")
    search_queries: List[str] = Field(
        ...,
        description="List of search queries used to find information about the topic"
    )
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp of when the research was conducted"
    )
    
    @property
    def relevant_facts(self) -> List[Fact]:
        """Return facts that meet the minimum relevance threshold."""
        return [fact for fact in self.facts if fact.relevance_score >= 0.7]
