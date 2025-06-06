"""Research Agent implementation for gathering facts about topics using OpenAI."""
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from openai import OpenAI
from pydantic import ValidationError

from models import ResearchRequest, ResearchResponse, Fact

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchAgent:
    """Agent responsible for researching topics and gathering structured facts.
    
    Attributes:
        client: OpenAI client instance
        model: Name of the OpenAI model to use
        max_retries: Maximum number of retries for API calls
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        max_retries: int = 3,
    ):
        """Initialize the ResearchAgent with OpenAI client and configuration.
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY from environment.
            model: Name of the OpenAI model to use.
            max_retries: Maximum number of retries for API calls.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
    
    def _generate_search_queries(self, topic: str) -> List[str]:
        """Generate search queries for the given topic.
        
        Args:
            topic: The topic to generate queries for.
            
        Returns:
            List of search query strings.
        """
        return [
            f"{topic} latest developments",
            f"{topic} key facts and statistics",
            f"{topic} recent news and updates"
        ]
    
    def _parse_facts_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse facts from the raw API response text.
        
        Args:
            response_text: Raw text response from the API.
            
        Returns:
            List of parsed fact dictionaries.
            
        Raises:
            ValueError: If the response cannot be parsed as valid JSON.
        """
        try:
            # Try to parse the response as JSON
            data = json.loads(response_text)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "facts" in data:
                return data["facts"]
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response as JSON: {e}")
            raise ValueError("Invalid response format: expected JSON") from e
    
    def _validate_facts(self, facts: List[Dict[str, Any]]) -> List[Fact]:
        """Validate and convert raw fact dictionaries to Fact models.
        
        Args:
            facts: List of raw fact dictionaries.
            
        Returns:
            List of validated Fact models.
        """
        validated_facts = []
        for fact_data in facts:
            try:
                # Ensure required fields are present
                if not all(k in fact_data for k in ["fact", "source", "relevance_score"]):
                    continue
                    
                # Create and validate the Fact model
                fact = Fact(
                    fact=fact_data["fact"],
                    source=fact_data["source"],
                    relevance_score=float(fact_data["relevance_score"])
                )
                validated_facts.append(fact)
            except (ValueError, ValidationError) as e:
                logger.warning(f"Skipping invalid fact: {e}")
                continue
                
        return validated_facts
    
    def research(self, request: ResearchRequest) -> ResearchResponse:
        """Conduct research on the given topic and return structured facts.
        
        Args:
            request: ResearchRequest containing the topic and parameters.
            
        Returns:
            ResearchResponse containing the gathered facts.
            
        Raises:
            ValueError: If the API response is invalid or cannot be processed.
            openai.OpenAIError: For API-related errors.
        """
        # Generate search queries based on the topic
        search_queries = self._generate_search_queries(request.topic)
        
        # Prepare the prompt for the OpenAI API
        prompt = f"""You are a research assistant. Provide {request.max_facts} key facts 
about "{request.topic}" in JSON format. Each fact should have:
- fact: The fact text
- source: A URL or reference
- relevance_score: A score from 0.0 to 1.0

Format as a JSON array of objects. Example:
[
  {{
    "fact": "Example fact text",
    "source": "https://example.com",
    "relevance_score": 0.95
  }}
]"""
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant that provides accurate, factual information in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Extract and validate the response
            response_text = response.choices[0].message.content
            raw_facts = self._parse_facts_from_response(response_text)
            validated_facts = self._validate_facts(raw_facts)
            
            # Filter facts by minimum relevance
            filtered_facts = [
                fact for fact in validated_facts 
                if fact.relevance_score >= request.min_relevance
            ][:request.max_facts]
            
            # Create and return the response
            return ResearchResponse(
                topic=request.topic,
                facts=filtered_facts,
                search_queries=search_queries,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error during research: {str(e)}")
            raise
