# Social Posting Agents

A multi-agent pipeline for researching topics, generating social media content, and creating images using OpenAI's models, Pydantic for data validation, and LangGraph for orchestration.

## Features

- **Research Agent**: Gathers facts and structured data about user-specified topics
- **Content Agent**: Generates platform-optimized content from research findings
- **Image Agent**: Creates AI-generated images that complement the content
- **LangGraph Orchestration**: Coordinates the workflow between agents
- **Multiple Platforms**: Supports Twitter, LinkedIn, Facebook, Instagram, and blog posts
- **Customizable Tone**: Choose from various tones like informative, persuasive, casual, etc.
- **Web Interface**: Streamlit-based web app with image display
- **CLI**: Command-line interface for automation and scripting
- **Detailed Prompt Logging**: Records all prompts sent to AI models for debugging and transparency

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/llanterme/social_posting_agents.git
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Set up your OpenAI API key:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

## Usage

### Web Interface

Launch the Streamlit web app:

```bash
poetry run streamlit run app.py
```

Then open your browser to `http://localhost:8501`

The web interface allows you to:
- Enter your topic and customize platform, tone, and number of facts
- View the generated social media post
- See the AI-generated image alongside your content
- Explore the research facts used to create the content

### Command Line Interface

```bash
poetry run python cli.py "Your topic here" --platform twitter --tone informative --max-facts 5
```

The CLI provides options for automated content generation and will save generated images to the `images/` directory.

### As a Library

```python
from orchestrator import Orchestrator

def main():
    orchestrator = Orchestrator(openai_api_key="your-api-key")
    result = orchestrator.run_workflow(
        topic="Benefits of renewable energy",
        platform="twitter",
        tone="informative",
        max_facts=5
    )
    print(result["content"])
    print(f"Image saved to: {result['image_path']}")

if __name__ == "__main__":
    main()
```

## Project Structure

```
.
├── agents/                   # Agent implementations
│   ├── __init__.py
│   ├── research_agent.py      # Research agent implementation
│   ├── content_agent.py       # Content agent implementation
│   └── image_agent.py         # Image agent implementation
├── models/                    # Pydantic models
│   ├── __init__.py
│   ├── research_models.py     # Research agent models
│   ├── content_models.py      # Content agent models
│   └── image_models.py        # Image agent models
├── utils/                     # Utility functions
│   ├── __init__.py
│   └── logging_config.py      # Centralized logging configuration
├── tests/                     # Unit and integration tests
│   ├── __init__.py
│   ├── test_research_agent.py
│   ├── test_content_agent.py
│   └── test_image_agent.py
├── logs/                      # Log directory (created automatically)
│   ├── agent_pipeline.log     # General application logs
│   └── prompts.log            # Detailed prompt logging
├── images/                    # Generated images directory
├── orchestrator.py            # LangGraph workflow orchestration
├── cli.py                     # Command-line interface
├── app.py                     # Streamlit web interface
├── pyproject.toml             # Poetry dependency management
├── poetry.lock                # Poetry lock file
└── README.md                  # This file
```

## Configuration

Environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## Prompt Logging

All prompts sent to AI models are logged for transparency and debugging purposes:

- **General logs**: `logs/agent_pipeline.log` - Application logs, errors, and general info
- **Prompt logs**: `logs/prompts.log` - Detailed logging of all prompts sent to OpenAI

The logging system uses a rotating file handler to manage log sizes and prevent them from growing too large.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
