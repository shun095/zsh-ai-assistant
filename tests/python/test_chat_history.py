"""Test cases for InMemoryChatHistory."""

import pytest
from zsh_ai_assistant.chat_history import InMemoryChatHistory


class TestInMemoryChatHistory:
    """Test cases for InMemoryChatHistory class."""

    def test_add_user_message_to_empty_chat_history(self):
        """Test adding a user message to an empty chat history."""
        chat_history = InMemoryChatHistory()
        chat_history.add_user_message("Hello, AI!")
        
        assert len(chat_history) == 1
        messages = chat_history.get_messages()
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello, AI!"

    def test_add_ai_message_to_chat_history(self):
        """Test adding an AI message to the chat history."""
        chat_history = InMemoryChatHistory()
        chat_history.add_user_message("Hello, AI!")
        chat_history.add_ai_message("Hello, user!")
        
        assert len(chat_history) == 2
        messages = chat_history.get_messages()
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello, AI!"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Hello, user!"

    def test_get_messages_returns_a_copy(self):
        """Test that get_messages returns a copy, not the original list."""
        chat_history = InMemoryChatHistory()
        chat_history.add_user_message("Hello")
        
        messages = chat_history.get_messages()
        messages.append({"role": "user", "content": "modified"})
        
        assert len(chat_history) == 1
        assert len(messages) == 2

    def test_clear_chat_history(self):
        """Test clearing the chat history."""
        chat_history = InMemoryChatHistory()
        chat_history.add_user_message("Hello")
        chat_history.add_ai_message("Hi")
        
        assert len(chat_history) == 2
        
        chat_history.clear()
        
        assert len(chat_history) == 0
        assert chat_history.get_messages() == []

    def test_chat_history_length(self):
        """Test chat history length property."""
        chat_history = InMemoryChatHistory()
        
        assert len(chat_history) == 0
        
        chat_history.add_user_message("Hello")
        assert len(chat_history) == 1
        
        chat_history.add_ai_message("Hi")
        assert len(chat_history) == 2

    def test_chat_history_boolean_evaluation(self):
        """Test boolean evaluation of chat history."""
        chat_history = InMemoryChatHistory()
        
        assert not chat_history  # Empty chat history is falsy
        
        chat_history.add_user_message("Hello")
        assert chat_history  # Non-empty chat history is truthy

    def test_chat_history_starting_empty(self):
        """Test that chat history starts empty."""
        chat_history = InMemoryChatHistory()
        
        assert len(chat_history) == 0
        assert chat_history.get_messages() == []
        assert not chat_history

    def test_multiple_user_messages(self):
        """Test adding multiple user messages."""
        chat_history = InMemoryChatHistory()
        chat_history.add_user_message("First message")
        chat_history.add_user_message("Second message")
        
        assert len(chat_history) == 2
        messages = chat_history.get_messages()
        assert messages[0]["content"] == "First message"
        assert messages[1]["content"] == "Second message"

    def test_multiple_ai_messages(self):
        """Test adding multiple AI messages."""
        chat_history = InMemoryChatHistory()
        chat_history.add_ai_message("First response")
        chat_history.add_ai_message("Second response")
        
        assert len(chat_history) == 2
        messages = chat_history.get_messages()
        assert messages[0]["content"] == "First response"
        assert messages[1]["content"] == "Second response"

    def test_mixed_messages(self):
        """Test adding a mix of user and AI messages."""
        chat_history = InMemoryChatHistory()
        chat_history.add_user_message("User 1")
        chat_history.add_ai_message("AI 1")
        chat_history.add_user_message("User 2")
        chat_history.add_ai_message("AI 2")
        
        assert len(chat_history) == 4
        messages = chat_history.get_messages()
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"
        assert messages[3]["role"] == "assistant"
