"""Configuration module for the zsh-ai-assistant.

Environment Variables:
    OPENAI_API_KEY: OpenAI API key (required)
    OPENAI_BASE_URL: Base URL for OpenAI API
    (default: https://api.openai.com/v1)
    AI_MODEL: LLM model to use (default: gpt-3.5-turbo)
    AI_TEMPERATURE: Temperature for AI responses (default: 0.7)
    AI_MAX_TOKENS: Maximum tokens for AI responses (default: 1000)
"""

import os


class AIConfig:
    """Configuration for AI service."""

    def __init__(self) -> None:
        """Initialize AI configuration from environment variables."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("AI_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "1000"))

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
            f"max_tokens={self.max_tokens})"
        )
