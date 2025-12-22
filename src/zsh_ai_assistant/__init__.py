"""Main module for zsh-ai-assistant."""

__all__ = [
    "AIConfig",
    "AIServiceInterface",
    "ChatHistoryInterface",
    "InMemoryChatHistory",
    "LangChainAIService",
]

# Import modules to make them available as part of the package
from .config import AIConfig
from .interfaces import AIServiceInterface, ChatHistoryInterface
from .chat_history import InMemoryChatHistory
from .ai_service import LangChainAIService
