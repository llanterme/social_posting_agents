import os
import uuid
import logging
import requests
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List

from openai import OpenAI
from pydantic import ValidationError

from models.image_models import ImageRequest, ImageResponse
from utils.logging_config import configure_logging

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)
prompt_logger = logging.getLogger('prompts')


class ImageAgent:
    """Agent for generating images based on content."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-image-1",
        images_dir: str = "images"
    ):
        """Initialize the image agent.
        
        Args:
            api_key: OpenAI API key. If None, uses the OPENAI_API_KEY environment variable.
            model: OpenAI image generation model to use.
            images_dir: Directory to save generated images.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # Ensure images directory exists
        self.images_dir = Path(images_dir)
        self.images_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"ImageAgent initialized with model: {model}")
        
    def _format_prompt(self, request: ImageRequest) -> str:
        """Format the prompt for image generation.
        
        Args:
            request: ImageRequest with generation parameters.
            
        Returns:
            Formatted prompt string.
        """
        # Base prompt for image generation
        base_prompt = f"Create a high-quality {request.style} image for a {request.platform} post about \"{request.topic}\". "
        
        # Add content context - extract key visuals and themes
        content_prompt = f"The image should visually represent the following content: {request.content}"
        
        # Platform-specific guidance
        if request.platform.lower() == "instagram":
            platform_guidance = "Make sure the image is visually striking and aesthetic with good composition."
        elif request.platform.lower() == "linkedin":
            platform_guidance = "Create a professional-looking image suitable for a business audience."
        elif request.platform.lower() == "twitter":
            platform_guidance = "Create an eye-catching image that stands out in a fast-scrolling feed."
        elif request.platform.lower() == "facebook":
            platform_guidance = "Create an engaging image that encourages social interaction."
        elif request.platform.lower() == "blog":
            platform_guidance = "Create a detailed image relevant to the blog topic that enhances the written content."
        else:
            platform_guidance = f"Create an appropriate image for {request.platform}."
        
        # Combine prompts
        prompt = f"{base_prompt} {content_prompt} {platform_guidance}"
        
        return prompt
    
    def _save_image(self, image_data: str) -> str:
        """Save base64 image data to a file.
        
        Args:
            image_data: Base64-encoded image data.
            
        Returns:
            Path to saved image file.
        """
        # Generate a unique filename
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        filename = f"image_{timestamp}_{unique_id}.png"
        filepath = self.images_dir / filename
        
        # Decode and save image
        try:
            if image_data.startswith("data:image"):
                # Remove data URL prefix
                image_data = image_data.split(",")[1]
                
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(image_data))
            
            logger.info(f"Image saved to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            raise
    
    def _save_image_from_url(self, url: str) -> str:
        """Save image from URL.
        
        Args:
            url: URL of the image.
            
        Returns:
            Path to saved image file.
        """
        import requests
        
        # Generate a unique filename
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        filename = f"image_{timestamp}_{unique_id}.png"
        filepath = self.images_dir / filename
        
        # Download and save image
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Image saved to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            raise
    
    def _save_image_from_b64(self, b64_json: str) -> str:
        """Save an image from base64 encoded string.
        
        Args:
            b64_json: Base64 encoded image data.
            
        Returns:
            Path to the saved image file.
            
        Raises:
            ValueError: If the base64 data is invalid.
        """
        try:
            # Ensure images directory exists
            os.makedirs(self.images_dir, exist_ok=True)
            
            # Generate a unique filename
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(self.images_dir, filename)
            
            # Decode base64 and save to file
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(b64_json))
                
            return filepath
        except Exception as e:
            logger.error(f"Error saving base64 image: {e}")
            raise ValueError(f"Error saving base64 image: {e}")
    
    def generate_image(self, request: ImageRequest) -> ImageResponse:
        """Generate an image based on content.
        
        Args:
            request: ImageRequest with generation parameters.
            
        Returns:
            ImageResponse with path to generated image.
            
        Raises:
            ValueError: If the request is invalid or generation fails.
            openai.OpenAIError: For API-related errors.
        """
        # Validate the request
        try:
            if isinstance(request, dict):
                request = ImageRequest.model_validate(request)
            else:
                request = ImageRequest.model_validate(request)
        except ValidationError as e:
            logger.error(f"Invalid image request: {e}")
            raise ValueError(f"Invalid image request: {e}") from e
        
        # Format the prompt
        prompt = self._format_prompt(request)
        logger.info(f"Generating image with prompt: {prompt}")
        
        # Log the complete prompt with model information
        prompt_logger.info(f"IMAGE AGENT PROMPT:\nModel: {self.model}\nTopic: {request.topic}\nPlatform: {request.platform}\nStyle: {request.style}\nPrompt: {prompt}")
        
        try:
            # Parameters for image generation
            params = {
                "model": self.model,
                "prompt": prompt,
                "size": request.size,
                "n": 1,
            }
            
            # Add quality parameter with value appropriate for the model
            # gpt-image-1 uses different quality values than dall-e-3
            if self.model == "gpt-image-1":
                params["quality"] = "high"
            elif self.model == "dall-e-3":
                params["quality"] = "standard"
            
            # Call the OpenAI API for image generation
            response = self.client.images.generate(**params)
            
            # Get image information from response
            image_data = response.data[0]
            
            # Debug response format
            logger.debug(f"Image response keys: {dir(image_data)}")
            
            # Handle different response formats based on model
            if hasattr(image_data, 'url') and image_data.url:
                # For models like dall-e-3 that return a URL
                image_url = image_data.url
                image_path = self._save_image_from_url(image_url)
            elif hasattr(image_data, 'b64_json') and image_data.b64_json:
                # For models that return base64 encoded image
                image_path = self._save_image_from_b64(image_data.b64_json)
            elif hasattr(image_data, 'revised_prompt') and hasattr(image_data, 'url'):
                # Newer version of the API might include revised_prompt field
                image_url = image_data.url
                image_path = self._save_image_from_url(image_url)
            else:
                logger.error(f"No image data found in response object: {image_data}")
                logger.error(f"Response data attributes: {dir(image_data)}")
                raise ValueError("No image URL or data in response")
            
            # Return response
            return ImageResponse(
                image_path=image_path,
                prompt=prompt
            )
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise ValueError(f"Image generation failed: {e}") from e
