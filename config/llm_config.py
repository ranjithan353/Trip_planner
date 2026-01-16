"""
LLM Configuration for AutoGen agents
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")  # or "mistral", "llama2", etc.

# Agent Configuration
MAX_ITERATIONS = 2  # Further reduced for faster responses
TEMPERATURE = 0.5  # Lower temperature for faster, more deterministic responses

# Tool Configuration
WEATHER_API_TIMEOUT = 2  # Further reduced timeout for faster response
SEARCH_TIMEOUT = 3  # Further reduced timeout for faster response
MAX_SEARCH_RESULTS = 2  # Reduced to 2 for faster search

# Performance Optimization
ENABLE_CRITIQUE = False  # Set to True for higher quality (slower), False for faster planning
ENABLE_REFINEMENT = False  # Set to True for refined output (slower), False for faster planning


def get_llm_config():
    """
    Get LLM configuration for AutoGen agents with Ollama
    
    Returns:
        Dictionary with LLM configuration compatible with AutoGen 0.2.0
    """
    # Ollama provides OpenAI-compatible API at /v1/chat/completions
    # Configure as OpenAI-compatible endpoint
    base_url = OLLAMA_BASE_URL.rstrip('/')
    if not base_url.endswith('/v1'):
        base_url = f"{base_url}/v1"
    
    return {
        "config_list": [
            {
                "model": OLLAMA_MODEL,
                "base_url": base_url,
                "api_key": "ollama",  # Ollama doesn't require a real API key, but AutoGen expects this field
                # AutoGen 0.2.0 should auto-detect OpenAI-compatible endpoints
            }
        ],
        "temperature": TEMPERATURE,
    }

