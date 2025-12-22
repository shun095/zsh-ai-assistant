"""Main module for zsh-ai-assistant."""

__all__ = [
    "AIConfig",
    "AIServiceInterface",
    "ChatHistoryInterface",
    "InMemoryChatHistory",
    "LangChainAIService",
    "setup_logging",
]

# Import modules to make them available as part of the package
from .config import AIConfig, setup_logging
from .interfaces import AIServiceInterface, ChatHistoryInterface
from .chat_history import InMemoryChatHistory
from .ai_service import LangChainAIService
