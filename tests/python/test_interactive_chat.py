#!/usr/bin/env python3
"""Test cases for interactive chat functionality."""

import os
import json
from io import StringIO
from unittest.mock import Mock, patch
import pytest
from zsh_ai_assistant.interactive_chat import InteractiveChat, main


class TestInteractiveChat:
    """Test cases for InteractiveChat class."""

    def test_init(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test InteractiveChat initialization."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        assert chat.test_mode is True
        assert len(chat.chat_history) == 0

    def test_init_with_env_var(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test InteractiveChat initialization with environment variable."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"
        os.environ["ZSH_AI_ASSISTANT_TEST_MODE"] = "true"

        chat = InteractiveChat()  # test_mode not explicitly set

        assert chat.test_mode is True
        assert len(chat.chat_history) == 0

    def test_init_without_env_var(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test InteractiveChat initialization without environment variable."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"
        # ZSH_AI_ASSISTANT_TEST_MODE not set

        chat = InteractiveChat()  # test_mode not explicitly set

        assert chat.test_mode is False
        assert len(chat.chat_history) == 0

    def test_add_user_message(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test adding user message to chat history."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)
        chat.add_user_message("Hello")

        assert len(chat.chat_history) == 1
        assert chat.chat_history[0] == {"role": "user", "content": "Hello"}

    def test_add_assistant_message(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test adding assistant message to chat history."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)
        chat.add_assistant_message("Hello there!")

        assert len(chat.chat_history) == 1
        assert chat.chat_history[0] == {"role": "assistant", "content": "Hello there!"}

    def test_get_chat_history_json(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test getting chat history as JSON."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)
        chat.add_user_message("Hello")
        chat.add_assistant_message("Hi there!")

        history_json = chat.get_chat_history_json()
        history = json.loads(history_json)

        assert len(history) == 2
        assert history[0] == {"role": "user", "content": "Hello"}
        assert history[1] == {"role": "assistant", "content": "Hi there!"}

    def test_generate_response(self, reset_env, mock_langchain_client) -> None:  # type: ignore[no-untyped-def]
        """Test generating AI response to user input."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Mock the client to return a specific response
        mock_langchain_client.invoke.return_value = Mock(content="Hello")

        result = chat.generate_response("Hello")

        assert result == "Hello"
        assert len(chat.chat_history) == 2
        assert chat.chat_history[0] == {"role": "user", "content": "Hello"}
        assert chat.chat_history[1] == {"role": "assistant", "content": "Hello"}

    def test_generate_response_handles_exception(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test that generate_response handles exceptions gracefully."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Patch the service's client attribute to simulate an error
        with patch.object(chat.service, "client") as mock_client:
            mock_client.invoke.side_effect = Exception("Test error")

            with pytest.raises(Exception) as exc_info:
                chat.generate_response("Hello")

            assert "Error: Test error" in str(exc_info.value)
            # Error should be added to chat history
            assert len(chat.chat_history) == 2
            assert chat.chat_history[0] == {"role": "user", "content": "Hello"}
            assert "Error: Test error" in chat.chat_history[1]["content"]


class TestInteractiveChatMain:
    """Test cases for main function."""

    def test_main_with_test_mode(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main function with test mode."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        # Mock the InteractiveChat class to avoid actual interactive session
        with patch("zsh_ai_assistant.interactive_chat.InteractiveChat") as mock_chat_class:
            mock_chat = Mock()
            mock_chat.run_interactive_chat = Mock()
            mock_chat_class.return_value = mock_chat

            main(test_mode=True)

        # Should exit gracefully
        assert True

    def test_main_without_test_mode(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main function without test mode."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        # Mock the InteractiveChat class to avoid actual interactive session
        with patch("zsh_ai_assistant.interactive_chat.InteractiveChat") as mock_chat_class:
            mock_chat = Mock()
            mock_chat.run_interactive_chat = Mock()
            mock_chat_class.return_value = mock_chat

            main(test_mode=False)

        # Should exit gracefully
        assert True

    def test_main_handles_exception(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main function handles exceptions."""
        # Mock sys.stdin to simulate user input
        with patch("sys.stdin", StringIO("quit\n")):
            # Mock InteractiveChat to raise an exception
            with patch("zsh_ai_assistant.interactive_chat.InteractiveChat") as mock_chat_class:
                mock_chat = Mock()
                mock_chat.run_interactive_chat.side_effect = Exception("Test error")
                mock_chat_class.return_value = mock_chat

                with pytest.raises(SystemExit) as exc_info:
                    main(test_mode=True)

                assert exc_info.value.code == 1


class TestInteractiveChatRun:
    """Test cases for run_interactive_chat method."""

    def test_run_interactive_chat_normal_flow(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test normal flow of interactive chat."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Mock the prompt_session.prompt method to simulate user input
        # First call returns "Hello", second call returns "quit"
        with patch.object(chat.prompt_session, "prompt", side_effect=["Hello", "quit"]):
            # Mock the generate_response method
            with patch.object(chat, "generate_response", return_value="Hi there!"):
                chat.run_interactive_chat()

        # Check output
        captured = capsys.readouterr()
        assert "Starting AI chat" in captured.out
        assert "Goodbye!" in captured.out

    def test_run_interactive_chat_exit_commands(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test that exit commands work properly."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Test various exit commands
        for exit_cmd in ["quit", "exit", "q"]:
            # Mock the prompt_session.prompt method to return exit command
            with patch.object(chat.prompt_session, "prompt", return_value=exit_cmd):
                chat.run_interactive_chat()

            captured = capsys.readouterr()
            assert "Goodbye!" in captured.out

    def test_run_interactive_chat_keyboard_interrupt(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test that keyboard interrupt is handled gracefully."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Mock the prompt_session.prompt method to raise KeyboardInterrupt
        with patch.object(chat.prompt_session, "prompt", side_effect=KeyboardInterrupt):
            chat.run_interactive_chat()

        # Should handle the interrupt gracefully
        captured = capsys.readouterr()
        assert "Goodbye!" in captured.out

    def test_run_interactive_chat_empty_input(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test that empty input exits the chat."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Mock the prompt_session.prompt method to return empty string
        with patch.object(chat.prompt_session, "prompt", return_value=""):
            chat.run_interactive_chat()

        captured = capsys.readouterr()
        assert "Goodbye!" in captured.out


class TestInteractiveChatTranslation:
    """Test cases for interactive translation functionality."""

    def test_run_interactive_translation_test_mode(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test translation in test mode with stdin input."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Mock stdin to provide text for translation
        import sys
        from io import StringIO

        original_stdin = sys.stdin
        sys.stdin = StringIO("Hello world")

        try:
            # Mock the translate_text method
            with patch.object(chat, "translate_text", return_value="Bonjour le monde") as mock_translate:
                chat.run_interactive_translation("french")

                # Should call translate_text with the input text
                mock_translate.assert_called_once_with("Hello world", "french")
        finally:
            sys.stdin = original_stdin


class TestInteractiveChatEdgeCases:
    """Test edge cases and additional coverage for interactive chat."""

    def test_translate_text_method(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test the translate_text method directly."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Mock the service's translate_stream method
        mock_chunks = ["Hello ", "world"]
        with patch.object(chat.service, "translate_stream", return_value=iter(mock_chunks)) as mock_translate_stream:
            result = chat.translate_text("Bonjour", "english")

            # Should call translate_stream with correct arguments
            mock_translate_stream.assert_called_once_with("Bonjour", "english")

            # Should return the concatenated result
            assert result == "Hello world"

            # Should add to history
            assert "Bonjour" in chat.history_manager.get_history_items()

    def test_translate_text_error_handling(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test error handling in translate_text method."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Mock the service's translate_stream method to raise an exception
        with patch.object(chat.service, "translate_stream", side_effect=Exception("Translation error")):
            with pytest.raises(Exception, match="Translation error"):
                chat.translate_text("Bonjour", "english")

    def test_main_function_error_handling(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test error handling in main function."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        # Mock InteractiveChat to raise an exception
        with patch("zsh_ai_assistant.interactive_chat.InteractiveChat", side_effect=Exception("Init error")):
            with pytest.raises(SystemExit):
                main(test_mode=True)

    def test_generate_response_error_handling(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test error handling in generate_response method."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Mock the service's chat_stream method to raise an exception
        with patch.object(chat.service, "chat_stream", side_effect=Exception("Chat error")):
            with pytest.raises(Exception, match="Chat error"):
                chat.generate_response("Hello")

            # Should still add error message to chat history
            assert len(chat.chat_history) == 2  # user message + error message
            assert "Error: Chat error" in chat.chat_history[1]["content"]

    def test_run_interactive_translation_test_mode_empty_input(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test translation in test mode with empty stdin input."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        chat = InteractiveChat(test_mode=True)

        # Mock stdin to provide empty input
        import sys
        from io import StringIO

        original_stdin = sys.stdin
        sys.stdin = StringIO("")

        try:
            # Mock the translate_text method
            with patch.object(chat, "translate_text", return_value="Bonjour le monde") as mock_translate:
                chat.run_interactive_translation("french")

                # Should not call translate_text with empty input
                mock_translate.assert_not_called()
        finally:
            sys.stdin = original_stdin
