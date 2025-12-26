"""Interfaces for the zsh-ai-assistant."""

from abc import ABC, abstractmethod
from typing import List


class AIServiceInterface(ABC):
    """Interface for AI services."""

    @abstractmethod
    def generate_command(self, prompt: str) -> str:
        """Generate a shell command from a natural language prompt."""
        pass

    @abstractmethod
    def chat(self, messages: List[dict]) -> str:
        """Generate a response from a chat history."""
        pass

    @abstractmethod
    def translate(self, text: str, target_language: str) -> str:
        """Translate text to a target language."""
        pass


class ChatHistoryInterface(ABC):
    """Interface for chat history management."""

    @abstractmethod
    def add_user_message(self, message: str) -> None:
        """Add a user message to the chat history."""
        pass

    @abstractmethod
    def add_ai_message(self, message: str) -> None:
        """Add an AI message to the chat history."""
        pass

    @abstractmethod
    def get_messages(self) -> List[dict]:
        """Get the current chat history as a list of message dictionaries."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the chat history."""
        pass
