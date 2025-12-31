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
