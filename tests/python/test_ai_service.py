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

    def test_translate_text_to_japanese(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test translating text to Japanese."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        result = service.translate("Hello", "japanese")

        assert result == "こんにちは"

    def test_translate_text_to_english(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test translating text to English."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        result = service.translate("こんにちは", "english")

        assert result == "Hello"

    def test_translate_text_to_other_language(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test translating text to other languages."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        result = service.translate("Hello world", "french")

        assert result == "[Translation to french: Hello world]"

    def test_translate_multiline_text(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test translating multiline text."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        multiline_text = "The quick brown fox\nJumps over the lazy dog"
        result = service.translate(multiline_text, "japanese")

        expected = "[Japanese translation of: The quick brown fox\nJumps over the lazy dog]"
        assert result == expected

    def test_translate_empty_text(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test translating empty text."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        result = service.translate("", "japanese")

        assert result == "[Japanese translation of: ]"

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

    def test_service_with_test_mode_uses_mock_client(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test that service uses MockClient when test_mode is True."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Verify that client is a MockClient
        from zsh_ai_assistant.ai_service import MockClient

        assert isinstance(service.client, MockClient)

    def test_generate_command_with_test_mode(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test command generation using MockClient in test mode."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Test various command generation scenarios
        result = service.generate_command("List files in current directory")
        assert result == "ls"

        result = service.generate_command("Check git status")
        assert result == "git status"

        result = service.generate_command("Some other command")
        assert result == 'echo "hello world"'

    def test_chat_with_test_mode(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test chat functionality using MockClient in test mode."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Test basic chat
        messages = [{"role": "user", "content": "Hello"}]
        result = service.chat(messages)
        assert result == "Hello"

        # Test chat with history context
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "world"},
        ]
        result = service.chat(messages)
        assert result == "I received your message: world"

    def test_chat_with_history_context_in_test_mode(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test chat with history context using MockClient."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Test "what did I say first" functionality
        messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "Response to first"},
            {"role": "user", "content": "what did i say first"},
        ]
        result = service.chat(messages)
        assert "First message" in result

        # Test "what did you say first" functionality
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "what did you say first"},
        ]
        result = service.chat(messages)
        assert "Hello, this is my first response as your AI assistant" in result

    def test_mock_client_reset_functionality(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test MockClient reset functionality."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Generate a command to increment call count
        service.generate_command("test")

        # Verify call count is incremented
        assert service.client.call_count == 1  # type: ignore[union-attr]
        assert len(service.client.calls) == 1  # type: ignore[union-attr]

        # Reset the client
        service.client.reset()  # type: ignore[union-attr]

        # Verify reset worked
        assert service.client.call_count == 0  # type: ignore[union-attr]
        assert len(service.client.calls) == 0  # type: ignore[union-attr]

    def test_mock_client_with_custom_response_callback(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test MockClient with custom response callback."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        def custom_callback(messages: list) -> Mock:
            mock_response = Mock()
            mock_response.content = "custom response"
            return mock_response

        from zsh_ai_assistant.ai_service import MockClient

        mock_client = MockClient(response_callback=custom_callback)

        result = mock_client.invoke([{"content": "test"}])
        assert result.content == "custom response"

    def test_mock_client_command_generation_patterns(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test MockClient command generation patterns."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Test various command patterns
        result = service.generate_command("git status")
        assert result == "git status"

        result = service.generate_command("check git")
        assert result == "git status"

        result = service.generate_command("list files")
        assert result == "ls"

        result = service.generate_command("find large files")
        assert result == "ls"  # "find large files" contains "list" so it returns "ls"

    def test_mock_client_error_handling(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test MockClient error handling."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Test API error simulation - this should raise an exception
        import pytest

        with pytest.raises(Exception, match="API request failed"):
            service.generate_command("return api error")

    def test_chat_with_system_message_in_test_mode(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test chat with system message using MockClient."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Test with system message provided
        messages = [
            {"role": "system", "content": "You are a test assistant."},
            {"role": "user", "content": "Hello"},
        ]
        result = service.chat(messages)
        assert result == "Hello"

        # Test with no system message (should add default)
        messages = [
            {"role": "user", "content": "Hello"},
        ]
        result = service.chat(messages)
        assert result == "Hello"

    def test_mock_client_captures_calls(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test that MockClient captures all calls."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Generate multiple commands
        service.generate_command("first command")
        service.generate_command("second command")

        # Verify calls were captured
        assert service.client.call_count == 2  # type: ignore[union-attr]
        assert len(service.client.calls) == 2  # type: ignore[union-attr]
        assert len(service.client.calls[0]) == 2  # type: ignore[union-attr]  # system + human message
        assert len(service.client.calls[1]) == 2  # type: ignore[union-attr]  # system + human message

    def test_chat_with_tell_me_what_we_said(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test MockClient response to 'tell me what we said'."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Test the specific pattern that should match the regex
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "world"},
            {"role": "assistant", "content": "I received your message: world"},
            {"role": "user", "content": "tell me what we said"},
        ]
        result = service.chat(messages)
        assert "You said" in result and "I said" in result

    def test_empty_prompt_with_test_mode(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test empty prompt handling in test mode."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        result = service.generate_command("")
        assert result == 'echo "hello world"'

    def test_chat_with_second_message_queries(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test MockClient responses to second message queries."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Test "what did I say second"
        messages = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Second"},
            {"role": "assistant", "content": "Response 2"},
            {"role": "user", "content": "what did i say second"},
        ]
        result = service.chat(messages)
        assert "Second" in result

        # Test "what did you say second"
        messages = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Second"},
            {"role": "assistant", "content": "Response 2"},
            {"role": "user", "content": "what did you say second"},
        ]
        result = service.chat(messages)
        assert "Response 2" in result

    def test_mock_client_fallback_responses(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test MockClient fallback responses for various queries."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()
        service = LangChainAIService(config, test_mode=True)

        # Test response for "what did i say first" with one message
        result = service.chat([{"role": "user", "content": "what did i say first"}])
        assert "You said: what did i say first" in result

        # Test response for "what did i say second" when only one message exists
        service.chat([{"role": "user", "content": "hello"}])
        result = service.chat([{"role": "user", "content": "what did i say second"}])
        assert "I received your message: what did i say second" in result

        # Test fallback for "what did you say first" when no assistant messages
        result = service.chat([{"role": "user", "content": "what did you say first"}])
        assert "I received your message: what did you say first" in result

        # Test fallback for "what did you say second" when only one assistant message
        service.chat([{"role": "user", "content": "test"}])
        result = service.chat([{"role": "user", "content": "what did you say second"}])
        assert "I received your message: what did you say second" in result

        # Test response for "what did you say first" when no assistant messages
        result = service.chat([{"role": "user", "content": "what did you say first"}])
        assert "I received your message: what did you say first" in result

        # Test response for "what did you say second" when only one assistant message exists
        # First create an assistant message by chatting
        result = service.chat([{"role": "user", "content": "hello"}])
        # Now ask for second assistant message
        result = service.chat([{"role": "user", "content": "what did you say second"}])
        assert "I received your message: what did you say second" in result

        # Test fallback for "what did you say second" when only one assistant message
        service.chat([{"role": "user", "content": "hello"}])
        result = service.chat([{"role": "user", "content": "what did you say second"}])
        assert "I received your message: what did you say second" in result

        # Test fallback for unknown content
        result = service.chat([{"role": "user", "content": "unknown query"}])
        assert "I received your message: unknown query" in result
