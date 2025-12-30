#!/usr/bin/env python3
"""Test cases for new interactive features: multibyte backspace, arrow key navigation, and Ctrl+R fuzzy search."""

import os
import tempfile

from zsh_ai_assistant.prompt_history import (
    PromptHistoryManager,
    get_character_width,
    get_string_display_width,
)


class TestMultibyteCharacterWidth:
    """Test cases for multibyte character width calculation."""

    def test_character_width_ascii(self) -> None:
        """Test character width for ASCII characters."""
        assert get_character_width("a") == 1
        assert get_character_width("A") == 1
        assert get_character_width("1") == 1
        assert get_character_width(" ") == 1

    def test_character_width_japanese(self) -> None:
        """Test character width for Japanese characters."""
        # Hiragana, Katakana, and Kanji should have width 2
        assert get_character_width("あ") == 2  # Hiragana
        assert get_character_width("ア") == 2  # Katakana
        assert get_character_width("日") == 2  # Kanji

    def test_character_width_emoji(self) -> None:
        """Test character width for emoji characters."""
        # Emoji should have width 2
        assert get_character_width("😀") == 2
        assert get_character_width("🎉") == 2
        assert get_character_width("🚀") == 2

    def test_character_width_mixed(self) -> None:
        """Test character width for mixed text."""
        # Test string with mixed ASCII, Japanese, and emoji
        text = "hello こんにちは 😀"
        expected_width = 5 + 1 + 5 * 2 + 1 + 2  # "hello" (5) + space (1) + "こんにちは" (5*2) + space (1) + "😀" (2)
        assert get_string_display_width(text) == expected_width

    def test_character_width_empty(self) -> None:
        """Test character width for empty string."""
        assert get_character_width("") == 0
        assert get_string_display_width("") == 0


class TestBackspaceMultibyteCharacters:
    """Test cases for backspace handling with multibyte characters."""

    def test_character_width_calculation_for_backspace(self) -> None:
        """Test character width calculation used in backspace handler."""
        # Test ASCII character
        assert get_character_width("a") == 1

        # Test Japanese character
        assert get_character_width("こ") == 2

        # Test emoji character
        assert get_character_width("😀") == 2

        # Test mixed text width calculation
        text = "hello こんにちは"
        expected_width = 5 + 1 + 5 * 2  # "hello" (5) + space (1) + "こんにちは" (5*2)
        assert get_string_display_width(text) == expected_width

    def test_backspace_logic_simulation(self) -> None:
        """Test backspace logic simulation without full prompt_toolkit context."""
        # Simulate the backspace logic from the handler
        text = "こんにちは"  # Japanese text
        cursor_position = len(text)

        # Simulate backspace - delete one character
        text_before_cursor = text[:cursor_position]
        if text_before_cursor:
            char_before_cursor = text_before_cursor[-1]
            char_width = get_character_width(char_before_cursor)

            # Delete one character
            new_text = text[: cursor_position - 1] + text[cursor_position:]
            new_cursor_position = cursor_position - 1

            # Verify results
            assert len(new_text) == len(text) - 1
            assert new_cursor_position == cursor_position - 1
            assert char_width == 2  # Japanese character width


class TestArrowKeyNavigation:
    """Test cases for arrow key navigation through history."""

    def test_history_manager_initialization(self) -> None:
        """Test history manager initialization."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("first command\n")
            temp_file.write("second command\n")
            temp_file.write("third command\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Verify history items are loaded
            history_items = manager.get_history_items()
            assert len(history_items) == 3
            assert history_items[0] == "first command"
            assert history_items[1] == "second command"
            assert history_items[2] == "third command"

        finally:
            os.unlink(temp_path)

    def test_history_navigation_logic(self) -> None:
        """Test history navigation logic."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("first command\n")
            temp_file.write("second command\n")
            temp_file.write("third command\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Simulate Up arrow navigation - should get most recent item
            history_items = manager.get_history_items()
            most_recent = history_items[-1] if history_items else ""

            assert most_recent == "third command"

        finally:
            os.unlink(temp_path)


class TestCtrlRFuzzySearch:
    """Test cases for Ctrl+R fuzzy search functionality."""

    def test_fuzzy_search_with_exact_match(self) -> None:
        """Test fuzzy search with exact match."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("hello world\n")
            temp_file.write("test prompt\n")
            temp_file.write("another entry\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Perform fuzzy search
            matches = manager.perform_fuzzy_search("test")

            # Should find at least one match
            assert len(matches) >= 1
            assert any("test" in match.lower() for match in matches)

        finally:
            os.unlink(temp_path)

    def test_fuzzy_search_with_partial_match(self) -> None:
        """Test fuzzy search with partial match."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("hello world\n")
            temp_file.write("testing prompt\n")
            temp_file.write("another test entry\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Perform fuzzy search
            matches = manager.perform_fuzzy_search("test")

            # Should find matches containing "test"
            assert len(matches) >= 1
            for match in matches:
                assert "test" in match.lower()

        finally:
            os.unlink(temp_path)

    def test_fuzzy_search_no_matches(self) -> None:
        """Test fuzzy search when no matches are found."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("hello world\n")
            temp_file.write("test prompt\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Perform fuzzy search with no matches
            matches = manager.perform_fuzzy_search("nonexistent")

            # Should return empty list
            assert len(matches) == 0

        finally:
            os.unlink(temp_path)

    def test_fuzzy_search_empty_query(self) -> None:
        """Test fuzzy search with empty query."""
        manager = PromptHistoryManager()

        # Perform fuzzy search with empty query
        matches = manager.perform_fuzzy_search("")

        # Should return empty list
        assert len(matches) == 0

    def test_fuzzy_search_state_management(self) -> None:
        """Test fuzzy search state management."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("test command 1\n")
            temp_file.write("test command 2\n")
            temp_file.write("other command\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Start fuzzy search
            manager.start_fuzzy_search("test")

            # Verify state
            assert manager.fuzzy_search_state.active
            assert manager.fuzzy_search_state.search_text == "test"
            assert len(manager.fuzzy_search_state.matches) >= 1
            assert manager.fuzzy_search_state.current_match_index == 0

            # Cycle through matches
            first_match = manager.cycle_fuzzy_search(forward=False)
            assert first_match is not None
            assert "test" in first_match.lower()

            # Cycle forward
            second_match = manager.cycle_fuzzy_search(forward=True)
            if second_match:
                assert second_match != first_match
                assert "test" in second_match.lower()

            # End fuzzy search
            manager.end_fuzzy_search()
            assert not manager.fuzzy_search_state.active

        finally:
            os.unlink(temp_path)

    def test_fuzzy_search_cycle_wrap_around(self) -> None:
        """Test fuzzy search cycle wrap around."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("test 1\n")
            temp_file.write("test 2\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Start fuzzy search
            manager.start_fuzzy_search("test")

            # Get first match
            first_match = manager.cycle_fuzzy_search(forward=False)

            # Cycle through all matches multiple times
            current_match = first_match
            for i in range(5):  # Cycle multiple times
                next_match = manager.cycle_fuzzy_search(forward=True)
                if next_match:
                    current_match = next_match

            # Should eventually wrap around
            assert current_match in ["test 1", "test 2"]

        finally:
            os.unlink(temp_path)


class TestCtrlCCancel:
    """Test cases for Ctrl+C cancel functionality."""

    def test_fuzzy_search_cancel(self) -> None:
        """Test canceling fuzzy search."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("test command\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Start fuzzy search
            search_text = "test"
            manager.start_fuzzy_search(search_text)

            # Verify search is active
            assert manager.fuzzy_search_state.active

            # Cancel fuzzy search
            manager.end_fuzzy_search()

            # Verify search is ended
            assert not manager.fuzzy_search_state.active
            assert manager.fuzzy_search_state.search_text == ""
            assert manager.fuzzy_search_state.matches == []

        finally:
            os.unlink(temp_path)


class TestFuzzySearchStateManagement:
    """Test cases for fuzzy search state management."""

    def test_fuzzy_search_state_initialization(self) -> None:
        """Test fuzzy search state initialization."""
        manager = PromptHistoryManager()

        # Initial state should be inactive
        assert not manager.fuzzy_search_state.active
        assert manager.fuzzy_search_state.search_text == ""
        assert manager.fuzzy_search_state.matches == []
        assert manager.fuzzy_search_state.current_match_index == 0
        assert manager.fuzzy_search_state.original_text == ""

    def test_start_fuzzy_search(self) -> None:
        """Test starting fuzzy search."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("test command 1\n")
            temp_file.write("test command 2\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Start fuzzy search
            search_text = "test"
            manager.start_fuzzy_search(search_text)

            # Verify state
            assert manager.fuzzy_search_state.active
            assert manager.fuzzy_search_state.search_text == search_text
            assert len(manager.fuzzy_search_state.matches) >= 1
            assert manager.fuzzy_search_state.current_match_index == 0
            assert manager.fuzzy_search_state.original_text == search_text

        finally:
            os.unlink(temp_path)

    def test_cycle_fuzzy_search_forward(self) -> None:
        """Test cycling through fuzzy search matches forward."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("test 1\n")
            temp_file.write("test 2\n")
            temp_file.write("test 3\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Start fuzzy search
            manager.start_fuzzy_search("test")

            # Get first match
            first_match = manager.cycle_fuzzy_search(forward=False)

            # Cycle forward
            second_match = manager.cycle_fuzzy_search(forward=True)
            third_match = manager.cycle_fuzzy_search(forward=True)

            # Should cycle through matches
            assert first_match != second_match
            assert second_match != third_match

        finally:
            os.unlink(temp_path)

    def test_cycle_fuzzy_search_backward(self) -> None:
        """Test cycling through fuzzy search matches backward."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("test 1\n")
            temp_file.write("test 2\n")
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Start fuzzy search
            manager.start_fuzzy_search("test")

            # Get first match
            first_match = manager.cycle_fuzzy_search(forward=False)

            # Cycle forward to second match
            manager.cycle_fuzzy_search(forward=True)

            # Cycle backward to first match
            back_to_first = manager.cycle_fuzzy_search(forward=False)

            # Should return to first match
            assert back_to_first == first_match

        finally:
            os.unlink(temp_path)

    def test_end_fuzzy_search(self) -> None:
        """Test ending fuzzy search."""
        manager = PromptHistoryManager()

        # Start fuzzy search
        manager.start_fuzzy_search("test")

        # End fuzzy search
        manager.end_fuzzy_search()

        # Verify state is reset
        assert not manager.fuzzy_search_state.active
        assert manager.fuzzy_search_state.search_text == ""
        assert manager.fuzzy_search_state.matches == []
        assert manager.fuzzy_search_state.current_match_index == 0
        assert manager.fuzzy_search_state.original_text == ""


class TestIntegrationFeatures:
    """Integration tests for all new features working together."""

    def test_full_interactive_workflow(self) -> None:
        """Test complete interactive workflow with all features."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("hello world\n")
            temp_file.write("test command\n")
            temp_file.write("こんにちは\n")  # Japanese greeting
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Test 1: Character width calculation for multibyte characters
            assert get_character_width("こ") == 2
            assert get_character_width("a") == 1
            assert get_character_width("😀") == 2

            # Test 2: History navigation
            history_items = manager.get_history_items()
            assert len(history_items) == 3
            assert history_items[-1] == "こんにちは"  # Most recent

            # Test 3: Fuzzy search
            matches = manager.perform_fuzzy_search("test")
            assert len(matches) >= 1
            assert any("test" in match.lower() for match in matches)

            # Test 4: Fuzzy search state management
            manager.start_fuzzy_search("test")
            assert manager.fuzzy_search_state.active

            first_match = manager.cycle_fuzzy_search(forward=False)
            assert first_match is not None

            manager.end_fuzzy_search()
            assert not manager.fuzzy_search_state.active

        finally:
            os.unlink(temp_path)

    def test_multibyte_character_in_history(self) -> None:
        """Test multibyte characters in history and search."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.write("hello world\n")
            temp_file.write("こんにちは\n")  # Japanese
            temp_file.write("😀 emoji test\n")  # Emoji
            temp_path = temp_file.name

        try:
            manager = PromptHistoryManager(history_file=temp_path)

            # Test history contains multibyte characters
            history_items = manager.get_history_items()
            assert "こんにちは" in history_items
            assert "😀 emoji test" in history_items

            # Test fuzzy search with multibyte characters
            matches = manager.perform_fuzzy_search("こんにちは")
            assert len(matches) >= 1
            assert "こんにちは" in matches[0]

            # Test character width calculations
            width_hello = get_string_display_width("hello")
            width_japanese = get_string_display_width("こんにちは")
            width_emoji = get_string_display_width("😀")

            assert width_hello == 5
            assert width_japanese == 10  # 5 characters * 2 width each
            assert width_emoji == 2

        finally:
            os.unlink(temp_path)
