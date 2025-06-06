"""Content Agent implementation for generating social media content."""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from openai import OpenAI
from pydantic import ValidationError

from models import ContentRequest, ContentResponse, PlatformType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentAgent:
    """Agent responsible for generating social media content from research facts.
    
    Attributes:
        client: OpenAI client instance
        model: Name of the OpenAI model to use
        max_retries: Maximum number of retries for API calls
    """
    
    # Platform-specific configurations
    PLATFORM_CONFIGS = {
        PlatformType.TWITTER: {
            'max_length': 280,
            'default_hashtags': 2,
            'tone': 'concise and engaging',
        },
        PlatformType.LINKEDIN: {
            'max_length': 1300,
            'default_hashtags': 3,
            'tone': 'professional and insightful',
        },
        PlatformType.FACEBOOK: {
            'max_length': 800,
            'default_hashtags': 2,
            'tone': 'conversational and friendly',
        },
        PlatformType.INSTAGRAM: {
            'max_length': 2200,
            'default_hashtags': 5,
            'tone': 'visual and engaging',
        },
        PlatformType.BLOG: {
            'max_length': 2000,
            'default_hashtags': 0,  # Usually not used in blog posts
            'tone': 'informative and detailed',
        },
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        max_retries: int = 3,
    ):
        """Initialize the ContentAgent with OpenAI client and configuration.
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY from environment.
            model: Name of the OpenAI model to use.
            max_retries: Maximum number of retries for API calls.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
    
    def _generate_hashtags(self, facts: List[Dict[str, Any]], count: int = 3) -> List[str]:
        """Generate relevant hashtags based on the facts.
        
        Args:
            facts: List of facts to generate hashtags from.
            count: Number of hashtags to generate.
            
        Returns:
            List of generated hashtags.
        """
        if count <= 0:
            return []
            
        # Extract keywords from facts
        keywords = set()
        for fact in facts:
            # Simple keyword extraction - in a real app, you might want something more sophisticated
            words = fact.get('fact', '').lower().split()
            keywords.update(w.strip('.,!?') for w in words if len(w) > 4)  # Only longer words
        
        # Convert to hashtags (simple implementation)
        hashtags = [f"#{word}" for word in list(keywords)[:count] if word.isalnum()]
        return hashtags
    
    def _format_prompt(self, request: ContentRequest) -> str:
        """Format the prompt for the OpenAI API.
        
        Args:
            request: ContentRequest with generation parameters.
            
        Returns:
            Formatted prompt string.
        """
        platform_config = self.PLATFORM_CONFIGS[request.platform]
        max_length = platform_config["max_length"]
        
        # Base prompt with platform-specific guidance
        if request.platform == PlatformType.TWITTER:
            prompt = f"""Generate a {request.tone} Twitter post using the following facts: 
            
{json.dumps(request.facts, indent=2)}

IMPORTANT CONSTRAINTS:
1. The post MUST be less than {max_length} characters (Twitter's limit).
2. Be extremely concise while maintaining the key information.
3. Count the characters carefully before finalizing.
            """
        else:
            prompt = f"""Generate a {request.tone} {request.platform} post using the following facts:
            
{json.dumps(request.facts, indent=2)}

Keep the content under {max_length} characters.
            """
        
        # Add call to action if requested
        if request.call_to_action:
            prompt += f"\n\nInclude this call to action: {request.call_to_action}"
        
        # Add hashtag guidance    
        if request.include_hashtags and platform_config['default_hashtags'] > 0:
            if request.platform == PlatformType.TWITTER:
                prompt += f"\n\nInclude {platform_config['default_hashtags']} short, relevant hashtags. These count toward your {request.max_length} character limit."
            else:
                prompt += f"\n\nInclude {platform_config['default_hashtags']} relevant hashtags at the end."
        
        return prompt
    
    def _validate_content(self, content: str, request: ContentRequest) -> bool:
        """Validate content against platform requirements.
        
        Args:
            content: Generated content string.
            request: Original content request.
            
        Returns:
            True if valid, False otherwise.
        """
        # Check if content is empty
        if not content or not content.strip():
            logger.warning("Content is empty or whitespace only")
            return False
            
        # Get platform-specific config
        platform_config = self.PLATFORM_CONFIGS[request.platform]
        max_length = platform_config["max_length"]
        
        # Check content length
        if len(content) > max_length:
            logger.warning(f"Content exceeds max length: {len(content)} > {max_length}")
            return False
            
        # Add additional validation rules here as needed
        return True
    
    def generate_content(self, request: ContentRequest) -> ContentResponse:
        """Generate social media content based on the provided facts.
        
        Args:
            request: ContentRequest containing facts and generation parameters.
            
        Returns:
            ContentResponse with the generated content.
            
        Raises:
            ValueError: If the request is invalid or generation fails.
            openai.OpenAIError: For API-related errors.
        """
        # Make sure we have a valid request
        try:
            # If the request is a dict, convert it to a ContentRequest object
            if isinstance(request, dict):
                request = ContentRequest.model_validate(request)
            else:
                # Ensure it's a valid ContentRequest
                request = ContentRequest.model_validate(request)
        except ValidationError as e:
            logger.error(f"Invalid content request: {e}")
            raise ValueError(f"Invalid content request: {e}") from e
        
        # Get platform-specific config for other values like default hashtags
        platform_config = self.PLATFORM_CONFIGS[request.platform]
        
        # Log the requested max length
        logger.info(f"Content generation request with max_length: {request.max_length} for platform {request.platform}")
        
        # Generate hashtags if needed
        hashtags = []
        if request.include_hashtags and platform_config['default_hashtags'] > 0:
            hashtags = self._generate_hashtags(
                request.facts, 
                platform_config['default_hashtags']
            )
        
        # Format the prompt
        prompt = self._format_prompt(request)
        
        try:
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a social media content creator that generates engaging posts."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            # Extract the generated content
            content = response.choices[0].message.content.strip()
            
            # Validate the content
            if not self._validate_content(content, request):
                raise ValueError("Generated content failed validation")
            
            # Create and return the response
            return ContentResponse(
                content=content,
                platform=request.platform,
                tone=request.tone,
                length=len(content),
                hashtags=hashtags,
                created_at=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
