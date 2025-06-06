"""Streamlit web interface for the research and content pipeline."""
import streamlit as st
import asyncio
import os
from typing import Dict, Any

from dotenv import load_dotenv
from orchestrator import Orchestrator

# Load environment variables from .env file if it exists
load_dotenv()

# Page config
st.set_page_config(
    page_title="Research & Content Generator",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        max-width: 800px;
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .result-box {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("📝 Research & Content Generator")
st.markdown("""
Generate research-based content for different social media platforms.
Enter a topic, choose your preferences, and let AI do the rest!
""")

# Sidebar for API key input
with st.sidebar:
    st.header("🔑 Settings")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Enter your OpenAI API key. Get one at https://platform.openai.com/"
    ) or os.getenv("OPENAI_API_KEY")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool uses AI to:
    1. Research a topic
    2. Generate key facts
    3. Create platform-optimized content
    """)

# Main form
with st.form("content_form"):
    st.header("Content Settings")
    
    # Input fields
    topic = st.text_input(
        "Topic to research",
        placeholder="e.g., Benefits of renewable energy",
        help="Enter a topic you'd like to research and generate content about"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        platform = st.selectbox(
            "Platform",
            ["twitter", "linkedin", "facebook", "instagram", "blog"],
            index=0,
            help="Select the target platform for the content"
        )
    
    with col2:
        tone = st.selectbox(
            "Tone",
            ["informative", "persuasive", "casual", "professional", "enthusiastic"],
            index=0,
            help="Select the tone for the content"
        )
    
    max_facts = st.slider(
        "Number of facts to include",
        min_value=1,
        max_value=10,
        value=5,
        help="Maximum number of facts to include in the research"
    )
    
    # Submit button
    submitted = st.form_submit_button("Generate Content")

# Handle form submission
if submitted:
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        st.stop()
    
    if not topic.strip():
        st.error("Please enter a topic to research.")
        st.stop()
    
    # Initialize the orchestrator
    orchestrator = Orchestrator(openai_api_key=api_key)
    
    # Show progress
    with st.spinner("Researching topic and generating content..."):
        try:
            # Run the workflow
            result = asyncio.run(
                orchestrator.run_workflow(
                    topic=topic,
                    platform=platform,
                    tone=tone,
                    max_facts=max_facts
                )
            )
            
            # Display results
            st.success("Content generated successfully!")
            
            # Show the generated content
            with st.expander("Generated Content", expanded=True):
                st.markdown(f"### {platform.capitalize()} Post")
                st.markdown("---")
                st.markdown(result["content"])
                
                if result.get("hashtags"):
                    st.markdown("\n" + " ".join(f"`{tag}`" for tag in result["hashtags"]))
            
            # Show research facts
            with st.expander("Research Facts", expanded=False):
                for i, fact in enumerate(result["facts"][:max_facts], 1):
                    st.markdown(f"**Fact {i}:** {fact['fact']}")
                    st.caption(f"Source: {fact.get('source', 'N/A')}")
                    st.progress(fact.get('relevance_score', 0.5))
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                st.text(f"API Response: {e.response.text}")
