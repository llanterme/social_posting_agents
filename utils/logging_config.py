"""Logging configuration for the project."""
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

def configure_logging():
    """Configure logging for the project.
    
    Creates logs directory if it doesn't exist and configures handlers
    for both console and file logging.
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Configure formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler for general logs
    file_handler = RotatingFileHandler(
        'logs/agent_pipeline.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Special file handler just for prompts
    prompt_handler = RotatingFileHandler(
        'logs/prompts.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    prompt_handler.setFormatter(formatter)
    prompt_handler.setLevel(logging.INFO)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure prompt logger
    prompt_logger = logging.getLogger('prompts')
    prompt_logger.setLevel(logging.INFO)
    prompt_logger.addHandler(prompt_handler)
    
    return root_logger, prompt_logger
