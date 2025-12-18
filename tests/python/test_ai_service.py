"""Test cases for LangChainAIService."""

import os
import pytest
from unittest.mock import Mock, patch
from zsh_ai_assistant.config import AIConfig
from zsh_ai_assistant.ai_service import LangChainAIService


class TestLangChainAIService:
    """Test cases for LangChainAIService class."""

    def test_generate_command_from_prompt(  # type: ignore[no-untyped-def]
        self, reset_env, mock_langchain_client
    ) -> None:
        """Test generating command from natural language prompt."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config)

        result = service.generate_command("List files in current directory")

        assert result == "mock_response"

    def test_chat_with_ai(self, reset_env, mock_langchain_client) -> None:  # type: ignore[no-untyped-def]
        """Test chatting with AI using message history."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config)

        messages = [
            {"role": "user", "content": "Hello, AI!"},
            {"role": "assistant", "content": "Hello, user!"},
        ]

        result = service.chat(messages)

        assert result == "mock_response"

    def test_invalid_configuration_raises_error(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test that invalid configuration raises an error."""
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"
        # Missing API key

        config = AIConfig()

        with pytest.raises(ValueError, match="Invalid AI configuration"):
            LangChainAIService(config)

    def test_generate_command_with_empty_prompt(  # type: ignore[no-untyped-def]
        self, reset_env, mock_langchain_client
    ) -> None:
        """Test generating command with empty prompt."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config)

        result = service.generate_command("")

        assert result == "mock_response"

    def test_chat_with_empty_messages(self, reset_env, mock_langchain_client) -> None:  # type: ignore[no-untyped-def]
        """Test chatting with AI when no messages are provided."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config)

        result = service.chat([])

        assert result == "mock_response"

    def test_chat_with_system_message(self, reset_env, mock_langchain_client) -> None:  # type: ignore[no-untyped-def]
        """Test chatting with AI when a system message is included."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config)

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]

        result = service.chat(messages)

        assert result == "mock_response"

    def test_service_initialization_with_valid_config(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test that service initializes correctly with valid config."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()

        with patch("zsh_ai_assistant.ai_service.ChatOpenAI") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance

            service = LangChainAIService(config)

            assert service.config == config
            assert service.client == mock_instance

            # Verify ChatOpenAI was called with correct parameters
            mock_class.assert_called_once_with(
                api_key="test-api-key",
                base_url="https://api.example.com",
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=1000,
            )

    def test_service_initialization_with_custom_config(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test that service initializes correctly with custom config."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"
        os.environ["AI_MODEL"] = "gpt-4"
        os.environ["AI_TEMPERATURE"] = "0.9"
        os.environ["AI_MAX_TOKENS"] = "2000"

        config = AIConfig()

        with patch("zsh_ai_assistant.ai_service.ChatOpenAI") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance

            LangChainAIService(config)

            # Verify ChatOpenAI was called with custom parameters
            mock_class.assert_called_once_with(
                api_key="test-api-key",
                base_url="https://api.example.com",
                model="gpt-4",
                temperature=0.9,
                max_tokens=2000,
            )

    def test_generate_command_uses_correct_system_prompt(  # type: ignore[no-untyped-def]
        self, reset_env, mock_langchain_client
    ) -> None:
        """Test that generate_command uses the correct system prompt."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config)

        # Mock the invoke method to capture the messages
        captured_messages = []

        def capture_invoke(messages: list) -> Mock:
            captured_messages.extend(messages)
            mock_response = Mock()
            mock_response.content = "mock_command"
            return mock_response

        mock_langchain_client.invoke = capture_invoke

        service.generate_command("test prompt")

        # Verify the system message is correct
        assert len(captured_messages) == 2
        assert captured_messages[0].content.startswith("You are a shell command generator.")
        assert captured_messages[1].content == "test prompt"
