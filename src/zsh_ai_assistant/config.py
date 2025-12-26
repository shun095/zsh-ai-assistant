"""Configuration module for the zsh-ai-assistant.

Environment Variables:
    OPENAI_API_KEY: OpenAI API key (required)
    OPENAI_BASE_URL: Base URL for OpenAI-compatible API
    (default: http://localhost:8080/v1)
    AI_MODEL: LLM model to use (default: gpt-3.5-turbo)
    AI_TEMPERATURE: Temperature for AI responses (default: 0.7)
    AI_MAX_TOKENS: Maximum tokens for AI responses (default: 1000)
    AI_DEBUG: Enable debug logging (default: False)
"""

import os
import logging


def setup_logging(debug: bool = False) -> logging.Logger:
    """Setup logging configuration.

    Args:
        debug: If True, enable debug-level logging

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("zsh_ai_assistant")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Clear any existing handlers to avoid duplicate logs
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if debug else logging.INFO)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


class AIConfig:
    """Configuration for AI service."""

    def __init__(self) -> None:
        """Initialize AI configuration from environment variables."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:8080/v1")
        self.model = os.getenv("AI_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "1000"))
        self.debug = os.getenv("AI_DEBUG", "").lower() in ("true", "1", "yes", "on")

    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return bool(self.api_key and self.base_url)

    def __str__(self) -> str:
        """Return string representation of configuration."""
        return (
            f"AIConfig(api_key={'*' * 8 if self.api_key else 'None'}, "
            f"base_url='{self.base_url}', model='{self.model}', "
            f"temperature={self.temperature}, "
            f"max_tokens={self.max_tokens}, debug={self.debug})"
        )
