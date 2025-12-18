"""Pytest configuration and fixtures for BDD tests."""

import os
import pytest
from unittest.mock import Mock, patch
from zsh_ai_assistant.config import AIConfig
from zsh_ai_assistant.chat_history import InMemoryChatHistory


@pytest.fixture
def reset_env():
    """Reset environment variables before each test."""
    # Save current env vars
    saved = {k: v for k, v in os.environ.items() if k.startswith(("OPENAI_", "AI_"))}

    # Clear relevant env vars
    for key in list(os.environ.keys()):
        if key.startswith(("OPENAI_", "AI_")):
            del os.environ[key]

    yield

    # Restore saved env vars
    os.environ.update(saved)


@pytest.fixture
def valid_config():
    """Create a valid AI configuration for testing."""
    os.environ["OPENAI_API_KEY"] = "test-api-key"
    os.environ["OPENAI_BASE_URL"] = "https://api.example.com"
    return AIConfig()


@pytest.fixture
def invalid_config():
    """Create an invalid AI configuration for testing."""
    return AIConfig()


@pytest.fixture
def chat_history():
    """Create a new InMemoryChatHistory instance."""
    return InMemoryChatHistory()


@pytest.fixture
def mock_ai_service():
    """Create a mock AI service for testing."""
    from zsh_ai_assistant.interfaces import AIServiceInterface

    mock = Mock(spec=AIServiceInterface)
    mock.generate_command.return_value = "mock_command"
    mock.chat.return_value = "mock_response"
    return mock


@pytest.fixture
def mock_langchain_client():
    """Create a mock LangChain client for testing."""
    with patch("zsh_ai_assistant.ai_service.ChatOpenAI") as mock_class:
        mock_instance = Mock()
        mock_instance.invoke.return_value = Mock(content="mock_response")
        mock_class.return_value = mock_instance
        yield mock_instance
