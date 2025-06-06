"""LangGraph orchestration for the research and content pipeline."""
from typing import TypedDict, List, Dict, Any, Literal, Annotated, Optional
from enum import Enum

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from models import ResearchRequest, ResearchResponse, ContentRequest, ContentResponse, ImageRequest, ImageResponse
from agents import ResearchAgent, ContentAgent, ImageAgent


class AgentState(TypedDict):
    """State for the LangGraph workflow."""
    research_request: ResearchRequest
    research_response: ResearchResponse
    content_request: ContentRequest
    content_response: ContentResponse
    image_request: ImageRequest
    image_response: ImageResponse
    platform: str
    tone: str
    

class Orchestrator:
    """Orchestrates the research and content generation pipeline."""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the orchestrator with agents.
        
        Args:
            openai_api_key: OpenAI API key. If None, will use OPENAI_API_KEY from environment.
        """
        self.research_agent = ResearchAgent(api_key=openai_api_key)
        self.content_agent = ContentAgent(api_key=openai_api_key)
        self.image_agent = ImageAgent(api_key=openai_api_key)
    
    def research_node(self, state: AgentState) -> AgentState:
        """Node that runs the research agent."""
        research_request = state["research_request"]
        research_response = self.research_agent.research(research_request)
        
        # Get platform-specific defaults from the ContentAgent
        platform = state["platform"]
        platform_configs = self.content_agent.PLATFORM_CONFIGS
        
        # Set up content request parameters
        content_request_params = {
            "facts": [fact.dict() for fact in research_response.facts],
            "platform": platform,
            "tone": state["tone"]
        }
        
        # If user provided a custom max_length, use that
        # Otherwise use the platform-specific default
        max_length = state.get("max_length")
        if max_length is not None:
            content_request_params["max_length"] = max_length
        else:
            # Use platform default from ContentAgent configuration
            if platform in platform_configs:
                content_request_params["max_length"] = platform_configs[platform]["max_length"]
        
        content_request = ContentRequest(**content_request_params)
        
        return {
            **state,
            "research_response": research_response,
            "content_request": content_request
        }
    
    def content_node(self, state: AgentState) -> AgentState:
        """Node that runs the content agent."""
        content_request = state["content_request"]
        content_response = self.content_agent.generate_content(content_request)
        return {
            **state,
            "content_response": content_response
        }
        
    def image_node(self, state: AgentState) -> AgentState:
        """Node that runs the image agent."""
        # Create image request from content response
        image_request_params = {
            "content": state["content_response"].content,
            "platform": state["platform"],
            "topic": state["research_request"].topic
        }
        image_request = ImageRequest(**image_request_params)
        
        # Generate the image
        image_response = self.image_agent.generate_image(image_request)
        
        return {
            **state,
            "image_request": image_request,
            "image_response": image_response
        }
    
    def create_workflow(self):
        """Create and return the LangGraph workflow."""
        # Define a new graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("research", self.research_node)
        workflow.add_node("generate_content", self.content_node)
        workflow.add_node("generate_image", self.image_node)
        
        # Define edges
        workflow.add_edge(START, "research")
        workflow.add_edge("research", "generate_content")
        workflow.add_edge("generate_content", "generate_image")
        workflow.add_edge("generate_image", END)
        
        # Compile the workflow
        return workflow.compile()
    
    def run_workflow(
        self,
        topic: str,
        platform: str = "twitter",
        tone: str = "informative",
        max_facts: int = 5,
        max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """Run the complete workflow.
        
        Args:
            topic: The topic to research.
            platform: Target platform for the content.
            tone: Desired tone for the content.
            max_facts: Maximum number of facts to include.
            
        Returns:
            Dictionary containing the workflow results.
        """
        # Create initial state
        initial_state = {
            "research_request": ResearchRequest(
                topic=topic,
                max_facts=max_facts
            ),
            "platform": platform,
            "tone": tone,
            "research_response": None,
            "content_request": None,
            "content_response": None,
            "image_request": None,
            "image_response": None
        }
        
        # Create and run the workflow
        workflow = self.create_workflow()
        result = workflow.invoke(initial_state)
        
        # Return the final state
        return {
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "facts": [
                fact.dict() 
                for fact in result["research_response"].facts
            ],
            "content": result["content_response"].content,
            "hashtags": result["content_response"].hashtags,
            "word_count": result["content_response"].word_count,
            "image_path": result["image_response"].image_path,
            "image_prompt": result["image_response"].prompt
        }
