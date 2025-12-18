"""Chat history implementation for the zsh-ai-assistant."""

from typing import List, Dict, Any
from .interfaces import ChatHistoryInterface


class InMemoryChatHistory(ChatHistoryInterface):
    """In-memory implementation of chat history."""
    
    def __init__(self):
        """Initialize empty chat history."""
        self.messages: List[Dict[str, Any]] = []
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to the chat history."""
        self.messages.append({"role": "user", "content": message})
    
    def add_ai_message(self, message: str) -> None:
        """Add an AI message to the chat history."""
        self.messages.append({"role": "assistant", "content": message})
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get the current chat history as a list of message dictionaries."""
        return self.messages.copy()
    
    def clear(self) -> None:
        """Clear the chat history."""
        self.messages.clear()
    
    def __len__(self) -> int:
        """Return the number of messages in the chat history."""
        return len(self.messages)
    
    def __bool__(self) -> bool:
        """Return True if chat history is not empty."""
        return len(self.messages) > 0
