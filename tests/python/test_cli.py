"""Test cases for CLI utilities."""

import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock
import pytest
from zsh_ai_assistant.cli import generate_command, chat, history_to_json, main


class TestCLIGenerateCommand:
    """Test cases for generate_command function."""

    def test_generate_command_with_valid_config(self, reset_env, mock_langchain_client):
        """Test generate_command with valid config."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.LangChainAIService") as mock_service_class:
            mock_service = Mock()
            mock_service.generate_command.return_value = "echo 'Hello World'"
            mock_service_class.return_value = mock_service

            result = generate_command("list files in current directory")

            assert result == "echo 'Hello World'"
            mock_service.generate_command.assert_called_once_with(
                "list files in current directory"
            )

    def test_generate_command_with_invalid_config(self, reset_env):
        """Test generate_command with invalid config."""
        # No API key set
        with pytest.raises(SystemExit) as exc_info:
            generate_command("test prompt")

        assert exc_info.value.code == 1

    def test_generate_command_handles_exception(self, reset_env):
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

    def test_chat_with_valid_messages(self, reset_env, mock_langchain_client):
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

    def test_chat_with_empty_messages(self, reset_env):
        """Test chat with empty messages."""
        with pytest.raises(SystemExit) as exc_info:
            chat("")

        assert exc_info.value.code == 1

    def test_chat_with_invalid_json(self, reset_env):
        """Test chat with invalid JSON."""
        with pytest.raises(SystemExit) as exc_info:
            chat("invalid json")

        assert exc_info.value.code == 1

    def test_chat_with_invalid_config(self, reset_env):
        """Test chat with invalid config."""
        messages = [{"role": "user", "content": "Hello"}]
        messages_json = json.dumps(messages)

        with pytest.raises(SystemExit) as exc_info:
            chat(messages_json)

        assert exc_info.value.code == 1

    def test_chat_handles_exception(self, reset_env):
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

    def test_history_to_json_with_valid_input(self):
        """Test history_to_json with valid input."""
        history_lines = (
            "user:Hello\nassistant:Hi there!\nuser:How are you?\nassistant:I'm good!"
        )

        result = history_to_json(history_lines)

        expected = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm good!"},
        ]

        assert json.loads(result) == expected

    def test_history_to_json_with_empty_input(self):
        """Test history_to_json with empty input."""
        result = history_to_json("")

        assert json.loads(result) == []

    def test_history_to_json_with_whitespace(self):
        """Test history_to_json handles whitespace."""
        history_lines = "user:Hello\nassistant:Hi"

        result = history_to_json(history_lines)

        expected = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        assert json.loads(result) == expected

    def test_history_to_json_with_lines_without_colon(self):
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

    def test_main_with_command_arg(self, reset_env, capsys):
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

    def test_main_with_command_from_stdin(self, reset_env, capsys):
        """Test main with command from stdin."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        with patch("zsh_ai_assistant.cli.generate_command") as mock_generate:
            mock_generate.return_value = "echo 'test'"

            # Simulate reading from stdin
            with patch.object(sys, "argv", ["cli", "command"]):
                with patch(
                    "sys.stdin", MagicMock(read=MagicMock(return_value="test prompt\n"))
                ):
                    main()

            mock_generate.assert_called_once_with("test prompt", False)

            # Check output
            captured = capsys.readouterr()
            assert captured.out.strip() == "echo 'test'"

    def test_main_with_chat_arg(self, reset_env, capsys):
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

    def test_main_with_history_to_json_arg(self, capsys):
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
                with patch(
                    "sys.stdin", MagicMock(read=MagicMock(return_value=history_lines))
                ):
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

    def test_main_without_arguments(self, capsys):
        """Test main without arguments shows usage."""
        with patch.object(sys, "argv", ["cli"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 1

        # Check error output
        captured = capsys.readouterr()
        assert "Usage:" in captured.err
