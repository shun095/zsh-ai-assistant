"""Test cases for CLI utilities."""

import os
import sys
import json
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
import pytest
from zsh_ai_assistant.cli import generate_command, chat, history_to_json, main, convert_to_openai_format, translate
from typing import List, Dict, Any


class TestCLIGenerateCommand:
    """Test cases for generate_command function."""

    def test_generate_command_with_valid_config(  # type: ignore[no-untyped-def]
        self, reset_env, mock_langchain_client
    ) -> None:
        """Test generate_command with valid config."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.LangChainAIService") as mock_service_class:
            mock_service = Mock()
            mock_service.generate_command.return_value = "echo 'Hello World'"
            mock_service_class.return_value = mock_service

            result = generate_command("list files in current directory")

            assert result == "echo 'Hello World'"
            mock_service.generate_command.assert_called_once_with("list files in current directory")

    def test_generate_command_with_invalid_config(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test generate_command with invalid config."""
        # No API key set
        with pytest.raises(SystemExit) as exc_info:
            generate_command("test prompt")

        assert exc_info.value.code == 1

    def test_generate_command_handles_exception(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test generate_command handles exceptions gracefully."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.LangChainAIService") as mock_service_class:
            mock_service = Mock()
            mock_service.generate_command.side_effect = Exception("Test error")
            mock_service_class.return_value = mock_service

            with pytest.raises(SystemExit) as exc_info:
                generate_command("test prompt")

            assert exc_info.value.code == 1


class TestCLIChat:
    """Test cases for chat function."""

    def test_chat_with_valid_messages(self, reset_env, mock_langchain_client) -> None:  # type: ignore[no-untyped-def]
        """Test chat with valid messages."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        messages_json = json.dumps(messages)

        with patch("zsh_ai_assistant.cli.LangChainAIService") as mock_service_class:
            mock_service = Mock()
            mock_service.chat.return_value = "Hello there!"
            mock_service_class.return_value = mock_service

            result = chat(messages_json)

            assert result == "Hello there!"
            mock_service.chat.assert_called_once_with(messages)

    def test_chat_with_empty_messages(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test chat with empty messages."""
        with pytest.raises(SystemExit) as exc_info:
            chat("")

        assert exc_info.value.code == 1

    def test_chat_with_invalid_json(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test chat with invalid JSON."""
        with pytest.raises(SystemExit) as exc_info:
            chat("invalid json")

        assert exc_info.value.code == 1

    def test_chat_with_invalid_config(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test chat with invalid config."""
        messages = [{"role": "user", "content": "Hello"}]
        messages_json = json.dumps(messages)

        with pytest.raises(SystemExit) as exc_info:
            chat(messages_json)

        assert exc_info.value.code == 1

    def test_chat_handles_exception(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test chat handles exceptions gracefully."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        messages = [{"role": "user", "content": "Hello"}]
        messages_json = json.dumps(messages)

        with patch("zsh_ai_assistant.cli.LangChainAIService") as mock_service_class:
            mock_service = Mock()
            mock_service.chat.side_effect = Exception("Test error")
            mock_service_class.return_value = mock_service

            with pytest.raises(SystemExit) as exc_info:
                chat(messages_json)

            assert exc_info.value.code == 1


class TestCLIHistoryToJson:
    """Test cases for history_to_json function."""

    def test_history_to_json_with_valid_input(self) -> None:
        """Test history_to_json with valid input."""
        history_lines = "user:Hello\nassistant:Hi there!\nuser:How are you?\nassistant:I'm good!"

        result = history_to_json(history_lines)

        expected = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm good!"},
        ]

        assert json.loads(result) == expected

    def test_history_to_json_with_empty_input(self) -> None:
        """Test history_to_json with empty input."""
        result = history_to_json("")

        assert json.loads(result) == []

    def test_history_to_json_with_whitespace(self) -> None:
        """Test history_to_json handles whitespace."""
        history_lines = "user:Hello\nassistant:Hi"

        result = history_to_json(history_lines)

        expected = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        assert json.loads(result) == expected

    def test_history_to_json_with_lines_without_colon(self) -> None:
        """Test history_to_json handles lines without colon."""
        history_lines = "user:Hello\ninvalid_line\nassistant:Hi"

        result = history_to_json(history_lines)

        expected = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        assert json.loads(result) == expected


class TestCLIMain:
    """Test cases for main function."""

    def test_main_with_command_arg(self, reset_env, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main with command arg."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.generate_command") as mock_generate:
            mock_generate.return_value = "echo 'test'"

            # Simulate command line arguments
            with patch.object(sys, "argv", ["cli", "command", "test prompt"]):
                main()

            mock_generate.assert_called_once_with("test prompt", False)

            # Check output
            captured = capsys.readouterr()
            assert captured.out.strip() == "echo 'test'"

    def test_main_with_command_from_stdin(self, reset_env, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main with command from stdin."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.generate_command") as mock_generate:
            mock_generate.return_value = "echo 'test'"

            # Simulate reading from stdin
            with patch.object(sys, "argv", ["cli", "command"]):
                with patch("sys.stdin", MagicMock(read=MagicMock(return_value="test prompt\n"))):
                    main()

            mock_generate.assert_called_once_with("test prompt", False)

            # Check output
            captured = capsys.readouterr()
            assert captured.out.strip() == "echo 'test'"

    def test_main_with_chat_arg(self, reset_env, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main with chat arg."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        messages = [{"role": "user", "content": "Hello"}]

        with patch("zsh_ai_assistant.cli.chat") as mock_chat:
            mock_chat.return_value = "Hi there!"

            # Simulate reading from stdin
            with patch.object(sys, "argv", ["cli", "chat"]):
                with patch(
                    "sys.stdin",
                    MagicMock(read=MagicMock(return_value=json.dumps(messages))),
                ):
                    main()

            mock_chat.assert_called_once_with(json.dumps(messages), False)

            # Check output
            captured = capsys.readouterr()
            assert captured.out.strip() == "Hi there!"

    def test_main_with_history_to_json_arg(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main with history-to-json arg."""
        history_lines = "user:Hello assistant:Hi"

        with patch("zsh_ai_assistant.cli.history_to_json") as mock_history:
            mock_history.return_value = json.dumps(
                [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi"},
                ]
            )

            # Simulate reading from stdin
            with patch.object(sys, "argv", ["cli", "history-to-json"]):
                with patch("sys.stdin", MagicMock(read=MagicMock(return_value=history_lines))):
                    main()

            mock_history.assert_called_once_with(history_lines)

            # Check output
            captured = capsys.readouterr()
            expected = json.dumps(
                [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi"},
                ]
            )
            assert captured.out.strip() == expected

    def test_main_without_arguments(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main without arguments shows usage."""
        with patch.object(sys, "argv", ["cli"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1

        # Check error output
        captured = capsys.readouterr()
        assert "Usage:" in captured.err

    def test_main_with_exception_handling(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main function exception handling."""
        with patch.object(sys, "argv", ["cli", "command"]):
            with patch("sys.stdin", StringIO("")):
                with patch("zsh_ai_assistant.cli.generate_command") as mock_generate:
                    mock_generate.side_effect = Exception("Test error")
                    with pytest.raises(SystemExit) as exc_info:
                        main()

        # Check error output
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "Test error" in captured.out
        assert exc_info.value.code == 1

    def test_main_with_test_mode_flag(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main function with ZSH_AI_ASSISTANT_TEST_MODE environment variable."""
        with patch.object(sys, "argv", ["cli", "command"]):
            with patch.dict(os.environ, {"ZSH_AI_ASSISTANT_TEST_MODE": "1"}):
                with patch("sys.stdin", StringIO("")):
                    with patch("zsh_ai_assistant.cli.generate_command") as mock_generate:
                        mock_generate.return_value = "test command"
                        main()

        # Check output
        captured = capsys.readouterr()
        assert "test command" in captured.out

    def test_main_with_translate_arg(self, reset_env, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main with translate arg."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.translate") as mock_translate:
            mock_translate.return_value = "こんにちは"

            # Simulate command line arguments
            with patch.object(sys, "argv", ["cli", "translate", "japanese", "Hello"]):
                main()

            mock_translate.assert_called_once_with("Hello", "japanese", False, stream=False)

            # Check output
            captured = capsys.readouterr()
            assert captured.out.strip() == "こんにちは"

    def test_main_with_translate_arg_invalid_usage(self, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main with translate arg but missing arguments."""
        with patch.object(sys, "argv", ["cli", "translate"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1

        # Check error output
        captured = capsys.readouterr()
        assert "Usage:" in captured.err

    def test_main_with_translate_arg_multiline_stdin(self, reset_env, capsys) -> None:  # type: ignore[no-untyped-def]
        """Test main with translate arg and multiline stdin input."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.translate") as mock_translate:
            mock_translate.return_value = "こんにちは\n世界"

            # Simulate command line arguments with only target language
            # and multiline text from stdin
            with patch.object(sys, "argv", ["cli", "translate", "japanese"]):
                with patch(
                    "sys.stdin",
                    MagicMock(read=MagicMock(return_value="Hello\nWorld\n")),
                ):
                    main()

            mock_translate.assert_called_once_with("Hello\nWorld", "japanese", False, stream=True)

            # When streaming, the translate function prints directly, so we need to mock that
            # Since we're mocking translate, it doesn't actually print, so output should be empty
            # In streaming mode, output is printed by translate function, not captured here
            # So we just verify the function was called correctly


class TestMessageConversion:
    """Test cases for message format conversion."""

    def test_convert_to_openai_format_with_user_message(self) -> None:
        """Test conversion of {"user": "content"} to OpenAI format."""
        messages = [{"user": "Hello"}]
        result = convert_to_openai_format(messages)
        expected = [{"role": "user", "content": "Hello"}]
        assert result == expected

    def test_convert_to_openai_format_with_assistant_message(self) -> None:
        """Test conversion of {"assistant": "content"} to OpenAI format."""
        messages = [{"assistant": "Hi there!"}]
        result = convert_to_openai_format(messages)
        expected = [{"role": "assistant", "content": "Hi there!"}]
        assert result == expected

    def test_convert_to_openai_format_with_system_message(self) -> None:
        """Test conversion of {"system": "content"} to OpenAI format."""
        messages = [{"system": "You are a helpful assistant."}]
        result = convert_to_openai_format(messages)
        expected = [{"role": "system", "content": "You are a helpful assistant."}]
        assert result == expected

    def test_convert_to_openai_format_with_mixed_messages(self) -> None:
        """Test conversion of mixed message formats."""
        messages = [{"user": "Hello"}, {"assistant": "Hi there!"}, {"user": "How are you?"}]
        result = convert_to_openai_format(messages)
        expected = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]
        assert result == expected

    def test_convert_to_openai_format_with_openai_format(self) -> None:
        """Test that OpenAI format messages pass through unchanged."""
        messages = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]
        result = convert_to_openai_format(messages)
        expected = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]
        assert result == expected

    def test_convert_to_openai_format_with_mixed_formats(self) -> None:
        """Test conversion with a mix of old and new formats."""
        messages = [{"user": "Hello"}, {"role": "assistant", "content": "Hi there!"}, {"user": "How are you?"}]
        result = convert_to_openai_format(messages)
        expected = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]
        assert result == expected

    def test_convert_to_openai_format_with_unknown_format(self) -> None:
        """Test that unknown message formats are preserved."""
        messages = [{"unknown": "content"}]
        result = convert_to_openai_format(messages)
        expected = [{"unknown": "content"}]
        assert result == expected

    def test_convert_to_openai_format_with_multiple_unknown_formats(self) -> None:
        """Test that multiple unknown message formats are preserved."""
        messages = [{"unknown": "content1"}, {"weird": "content2"}, {"random": "content3"}]
        result = convert_to_openai_format(messages)
        expected = [{"unknown": "content1"}, {"weird": "content2"}, {"random": "content3"}]
        assert result == expected

    def test_convert_to_openai_format_with_empty_list(self) -> None:
        """Test conversion with empty message list."""
        messages: List[Dict[str, Any]] = []
        result = convert_to_openai_format(messages)
        expected: List[Dict[str, Any]] = []
        assert result == expected

    def test_convert_to_openai_format_preserves_additional_fields(self) -> None:
        """Test that additional fields in OpenAI format are preserved."""
        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": "Hello", "name": "user1"},
            {"role": "assistant", "content": "Hi there!", "tool_calls": []},
        ]
        result = convert_to_openai_format(messages)
        expected = [
            {"role": "user", "content": "Hello", "name": "user1"},
            {"role": "assistant", "content": "Hi there!", "tool_calls": []},
        ]
        assert result == expected


class TestCLITranslate:
    """Test cases for translate function."""

    def test_translate_with_valid_config(  # type: ignore[no-untyped-def]
        self, reset_env, mock_langchain_client
    ) -> None:
        """Test translate with valid config."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.LangChainAIService") as mock_service_class:
            mock_service = Mock()
            mock_service.translate.return_value = "こんにちは"
            mock_service_class.return_value = mock_service

            result = translate("Hello", "japanese")

            assert result == "こんにちは"
            mock_service.translate.assert_called_once_with("Hello", "japanese")

    def test_translate_with_invalid_config(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test translate with invalid config."""
        # No API key set
        with pytest.raises(SystemExit) as exc_info:
            translate("Hello", "japanese")

        assert exc_info.value.code == 1

    def test_translate_handles_exception(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test translate handles exceptions gracefully."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.LangChainAIService") as mock_service_class:
            mock_service = Mock()
            mock_service.translate.side_effect = Exception("Test error")
            mock_service_class.return_value = mock_service

            with pytest.raises(SystemExit) as exc_info:
                translate("Hello", "japanese")

            assert exc_info.value.code == 1

    def test_translate_with_multiline_text(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test translate with multiline text."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.LangChainAIService") as mock_service_class:
            mock_service = Mock()
            mock_service.translate.return_value = "こんにちは\n世界"
            mock_service_class.return_value = mock_service

            multiline_text = "Hello\nWorld"
            result = translate(multiline_text, "japanese")

            assert result == "こんにちは\n世界"
            mock_service.translate.assert_called_once_with(multiline_text, "japanese")

    def test_translate_with_empty_text(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test translate with empty text."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.LangChainAIService") as mock_service_class:
            mock_service = Mock()
            mock_service.translate.return_value = ""
            mock_service_class.return_value = mock_service

            result = translate("", "japanese")

            assert result == ""
            mock_service.translate.assert_called_once_with("", "japanese")
