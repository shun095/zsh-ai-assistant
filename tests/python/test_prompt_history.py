#!/usr/bin/env python3
"""Test cases for prompt history functionality."""

import os
import tempfile

from zsh_ai_assistant.prompt_history import (
    PromptHistoryManager,
    get_prompt_session,
    get_character_width,
    get_string_display_width,
)


class TestPromptHistoryManager:
    """Test cases for PromptHistoryManager class."""

    def test_init_with_default_history_file(self) -> None:
        """Test initialization with default history file."""
        manager = PromptHistoryManager()

        # Should use default history file location
        expected_path = os.path.expanduser("~/.zsh_ai_assistant_history")
        assert manager.history_file == expected_path

    def test_init_with_custom_history_file(self) -> None:
        """Test initialization with custom history file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)
            assert manager.history_file == temp_path
        finally:
            os.unlink(temp_path)


class TestCharacterWidthFunctions:
    """Test cases for character width utility functions."""

    def test_get_character_width_ascii(self) -> None:
        """Test character width for ASCII characters."""
        assert get_character_width("a") == 1
        assert get_character_width("A") == 1
        assert get_character_width("1") == 1
        assert get_character_width(" ") == 1

    def test_get_character_width_japanese(self) -> None:
        """Test character width for Japanese characters."""
        # Japanese Hiragana (should be 2)
        assert get_character_width("あ") == 2
        # Japanese Katakana (should be 2)
        assert get_character_width("ア") == 2
        # Japanese Kanji (should be 2)
        assert get_character_width("日") == 2

    def test_get_character_width_emoji(self) -> None:
        """Test character width for emoji characters."""
        # Emoji (should be 2)
        assert get_character_width("😀") == 2
        assert get_character_width("🎉") == 2

    def test_get_character_width_mixed(self) -> None:
        """Test character width for mixed character types."""
        # Half-width Katakana (should be 1)
        assert get_character_width("ｱ") == 1
        # Full-width characters (should be 2)
        assert get_character_width("Ａ") == 2

    def test_get_character_width_empty(self) -> None:
        """Test character width for empty string."""
        assert get_character_width("") == 0

    def test_get_string_display_width(self) -> None:
        """Test string display width calculation."""
        # ASCII string
        assert get_string_display_width("hello") == 5

        # Mixed string
        assert get_string_display_width("hello世界") == 5 + 2 + 2  # hello (5) + 世 (2) + 界 (2)

        # Emoji string
        assert get_string_display_width("hello😀") == 5 + 2  # hello (5) + 😀 (2)

        # Empty string
        assert get_string_display_width("") == 0

    def test_add_to_history(self) -> None:
        """Test adding text to history."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)
            manager.add_to_history("test prompt")

            # Verify history was added
            history_items = manager.get_history_items()
            assert len(history_items) == 1
            assert history_items[0] == "test prompt"
        finally:
            os.unlink(temp_path)

    def test_get_history_items(self) -> None:
        """Test getting history items."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("first prompt\nsecond prompt\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)
            history_items = manager.get_history_items()

            assert len(history_items) == 2
            assert history_items[0] == "first prompt"
            assert history_items[1] == "second prompt"
        finally:
            os.unlink(temp_path)

    def test_clear_history(self) -> None:
        """Test clearing history."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("test prompt\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Verify history exists
            history_items = manager.get_history_items()
            assert len(history_items) == 1

            # Clear history
            manager.clear_history()

            # Verify history is cleared
            history_items = manager.get_history_items()
            assert len(history_items) == 0

            # File should be removed by clear_history, so don't try to unlink it
            # Check if file exists
            assert not os.path.exists(temp_path)
        except Exception:
            # Clean up file if it still exists
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise


class TestGetPromptSession:
    """Test cases for get_prompt_session function."""

    def test_get_prompt_session_returns_prompt_session(self) -> None:
        """Test that get_prompt_session returns a PromptSession instance."""
        session = get_prompt_session()
        assert hasattr(session, "prompt")

    def test_get_prompt_session_with_custom_history_file(self) -> None:
        """Test get_prompt_session with custom history file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            session = get_prompt_session(history_file=temp_path)
            assert hasattr(session, "prompt")
        finally:
            os.unlink(temp_path)


class TestMultibyteCharacterHandling:
    """Test cases for multibyte character handling in prompt input."""

    def test_backspace_with_multibyte_characters(self) -> None:
        """Test that backspace properly handles multibyte characters."""
        # Test the character width calculation for multibyte characters
        from zsh_ai_assistant.prompt_history import get_character_width, get_string_display_width

        # Test with Japanese characters (multibyte UTF-8)
        test_text = "こんにちは"  # "Hello" in Japanese

        # Verify each character has correct width
        for char in test_text:
            width = get_character_width(char)
            assert width == 2, f"Expected width 2 for character {char}, got {width}"

        # Verify total display width (5 characters × 2 width each = 10)
        total_width = get_string_display_width(test_text)
        assert total_width == 10, f"Expected total width 10 for '{test_text}', got {total_width}"

    def test_backspace_with_mixed_characters(self) -> None:
        """Test backspace with mixed ASCII and multibyte characters."""
        from zsh_ai_assistant.prompt_history import get_character_width, get_string_display_width

        # Test with mixed text
        test_text = "hello こんにちは world"  # Mixed ASCII and Japanese

        # Verify character widths
        expected_widths = [
            ("h", 1),
            ("e", 1),
            ("l", 1),
            ("l", 1),
            ("o", 1),
            (" ", 1),
            (" ", 1),
            ("こ", 2),
            ("ん", 2),
            ("に", 2),
            ("ち", 2),
            ("は", 2),
            (" ", 1),
            ("w", 1),
            ("o", 1),
            ("r", 1),
            ("l", 1),
            ("d", 1),
        ]

        for char, expected_width in expected_widths:
            width = get_character_width(char)
            assert width == expected_width, f"Expected width {expected_width} for character {char}, got {width}"

        # Verify total display width (11 ASCII chars × 1 + 5 Japanese chars × 2 = 22)
        total_width = get_string_display_width(test_text)
        assert total_width == 22, f"Expected total width 22 for '{test_text}', got {total_width}"


class TestCtrlRSearch:
    """Test cases for Ctrl+R fuzzy search functionality."""

    def test_ctrl_r_search_with_exact_match(self) -> None:
        """Test Ctrl+R search with exact match."""
        # Create a temporary history file with test data
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("hello world\n")
            temp_file.write("test prompt\n")
            temp_file.write("another entry\n")
            temp_path = temp_file.name

        try:
            # Create a history manager with the test history
            from zsh_ai_assistant.prompt_history import PromptHistoryManager

            history_manager = PromptHistoryManager(history_file=temp_path)

            # Test fuzzy search functionality
            search_text = "test"
            matches = history_manager.perform_fuzzy_search(search_text)

            # Verify that matches were found
            assert len(matches) > 0, f"Expected matches for '{search_text}', got none"

            # Verify that "test prompt" is in the matches
            assert "test prompt" in matches, f"Expected 'test prompt' in matches, got {matches}"

        finally:
            os.unlink(temp_path)

    def test_ctrl_r_search_with_partial_match(self) -> None:
        """Test Ctrl+R search with partial match."""
        # Create a temporary history file with test data
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("hello world\n")
            temp_file.write("testing prompt\n")
            temp_file.write("another test entry\n")
            temp_path = temp_file.name

        try:
            # Create a history manager with the test history
            from zsh_ai_assistant.prompt_history import PromptHistoryManager

            history_manager = PromptHistoryManager(history_file=temp_path)

            # Test fuzzy search functionality
            search_text = "test"
            matches = history_manager.perform_fuzzy_search(search_text)

            # Verify that matches were found
            assert len(matches) > 0, f"Expected matches for '{search_text}', got none"

            # Verify that all matches contain "test" (case-insensitive)
            for match in matches:
                assert "test" in match.lower(), f"Expected 'test' in match '{match}'"

        finally:
            os.unlink(temp_path)

    def test_ctrl_r_search_no_matches(self) -> None:
        """Test Ctrl+R search when no matches are found."""
        # Create a temporary history file with test data
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("hello world\n")
            temp_file.write("test prompt\n")
            temp_path = temp_file.name

        try:
            # Create a history manager with the test history
            from zsh_ai_assistant.prompt_history import PromptHistoryManager

            history_manager = PromptHistoryManager(history_file=temp_path)

            # Test fuzzy search functionality with non-matching text
            search_text = "nonexistent"
            matches = history_manager.perform_fuzzy_search(search_text)

            # Verify that no matches were found
            assert len(matches) == 0, f"Expected no matches for '{search_text}', got {matches}"

        finally:
            os.unlink(temp_path)
