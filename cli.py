"""Command-line interface for the research and content pipeline."""
import asyncio
import argparse
import json
import os
from typing import Optional

from dotenv import load_dotenv

from orchestrator import Orchestrator
from utils.logging_config import configure_logging

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
configure_logging()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Research and content generation pipeline")
    
    # Required arguments
    parser.add_argument(
        "topic",
        type=str,
        help="The topic to research and generate content about"
    )
    
    # Optional arguments
    parser.add_argument(
        "--platform",
        type=str,
        default="twitter",
        choices=["twitter", "linkedin", "facebook", "instagram", "blog"],
        help="Target platform for the content (default: twitter)"
    )
    
    parser.add_argument(
        "--tone",
        type=str,
        default="informative",
        choices=["informative", "persuasive", "casual", "professional", "enthusiastic"],
        help="Tone for the content (default: informative)"
    )
    
    parser.add_argument(
        "--max-facts",
        type=int,
        default=5,
        help="Maximum number of facts to include (default: 5)"
    )
    
    parser.add_argument(
        "--max-length",
        type=int,
        default=None,
        help="Maximum content length in characters (default: platform-specific, e.g. 280 for Twitter)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file to save results (JSON format)"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key (default: uses OPENAI_API_KEY environment variable)"
    )
    
    return parser.parse_args()


def main():
    """Run the CLI application."""
    args = parse_arguments()
    
    # Get API key from args or environment
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --api-key")
        return
    
    # Initialize the orchestrator
    orchestrator = Orchestrator(openai_api_key=api_key)
    
    # Inform about prompt logging
    print("All agent prompts will be logged to logs/prompts.log")
    print("General application logs available in logs/agent_pipeline.log")
    print()
    
    try:
        # Run the workflow
        print(f"Researching topic: {args.topic}")
        print(f"Platform: {args.platform}, Tone: {args.tone}")
        print("Generating content...\n")
        
        workflow_result = orchestrator.run_workflow(
            topic=args.topic,
            platform=args.platform,
            tone=args.tone,
            max_facts=args.max_facts,
            max_length=args.max_length
        )
        
        # Print the results
        print("\n==================================================\n"
              f"Generated {args.platform.capitalize()} Post:\n"
              "--------------------------------------------------\n"
              f"{workflow_result['content']}\n"
              "==================================================")
        
        if workflow_result['hashtags']:
            print(f"\nHashtags: {' '.join(workflow_result['hashtags'])}")
            
        # Print image information
        if 'image_path' in workflow_result:
            print(f"\nImage generated and saved to: {workflow_result['image_path']}")
            print(f"Image prompt: {workflow_result['image_prompt'][:100]}...")
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(workflow_result, f, indent=2)
            print(f"\nResults saved to {args.output}")
    
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"API Response: {e.response.text}")


if __name__ == "__main__":
    main()
