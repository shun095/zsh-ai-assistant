"""Main module for zsh-ai-assistant."""

__all__ = [
    "AIConfig",
    "AIServiceInterface",
    "LangChainAIService",
    "setup_logging",
]

# Import modules to make them available as part of the package
from .config import AIConfig, setup_logging
from .interfaces import AIServiceInterface
from .ai_service import LangChainAIService
