# Research & Content Generator

A multi-agent pipeline for researching topics and generating social media content using OpenAI's GPT models, Pydantic for data validation, and LangGraph for orchestration.

## Features

- **Research Agent**: Gathers facts and structured data about user-specified topics
- **Content Agent**: Generates platform-optimized content from research findings
- **LangGraph Orchestration**: Coordinates the workflow between agents
- **Multiple Platforms**: Supports Twitter, LinkedIn, Facebook, Instagram, and blog posts
- **Customizable Tone**: Choose from various tones like informative, persuasive, casual, etc.
- **Web Interface**: Streamlit-based web app for easy interaction
- **CLI**: Command-line interface for automation and scripting

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pydantic-langchain-demo.git
   cd pydantic-langchain-demo
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
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Command Line Interface

```bash
python cli.py "Your topic here" --platform twitter --tone informative --max-facts 5
```

### As a Library

```python
from orchestrator import Orchestrator
import asyncio

async def main():
    orchestrator = Orchestrator(openai_api_key="your-api-key")
    result = await orchestrator.run_workflow(
        topic="Benefits of renewable energy",
        platform="twitter",
        tone="informative",
        max_facts=5
    )
    print(result["content"])

asyncio.run(main())
```

## Project Structure

```
.
├── agents/                  # Agent implementations
│   ├── __init__.py
│   ├── research_agent.py     # Research agent implementation
│   └── content_agent.py      # Content agent implementation
├── models/                   # Pydantic models
│   ├── __init__.py
│   ├── research_models.py    # Research agent models
│   └── content_models.py     # Content agent models
├── tests/                    # Unit and integration tests
│   ├── __init__.py
│   ├── test_research_agent.py
│   ├── test_content_agent.py
│   ├── test_research_agent_integration.py
│   └── test_content_agent_integration.py
├── orchestrator.py           # LangGraph workflow orchestration
├── cli.py                    # Command-line interface
├── app.py                    # Streamlit web interface
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Configuration

Environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
