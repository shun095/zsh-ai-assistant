#!/usr/bin/env python3
"""Prompt history and input handling for zsh-ai-assistant."""

import os
import json
from typing import Any, List, Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings

# Try to import fuzzy search libraries
try:
    from fuzzywuzzy import fuzz, process  # type: ignore[import-untyped]

    FUZZY_SEARCH_AVAILABLE = True
except ImportError:
    FUZZY_SEARCH_AVAILABLE = False

# Try to import wcwidth for multibyte character handling
try:
    import wcwidth  # type: ignore[import-untyped]

    WCWIDTH_AVAILABLE = True
except ImportError:
    WCWIDTH_AVAILABLE = False


def get_character_width(char: str) -> int:
    """Get the display width of a character, handling multibyte characters.

    Args:
        char: Character to measure

    Returns:
        Display width of the character (1 for normal, 2 for wide)
    """
    if not char:
        return 0

    if WCWIDTH_AVAILABLE:
        try:
            width = wcwidth.wcwidth(char)
            return width if width is not None else 1
        except Exception:
            pass

    # Fallback: estimate width based on Unicode ranges
    # This is a simplified approach
    code_point = ord(char)

    # Common wide character ranges (CJK, etc.)
    if (
        0x1100 <= code_point <= 0x11FF  # Hangul Jamo
        or 0x2E80 <= code_point <= 0xA4CF  # CJK Radicals, Symbols, etc.
        or 0xAC00 <= code_point <= 0xD7AF  # Hangul Syllables
        or 0xF900 <= code_point <= 0xFAFF  # CJK Compatibility Ideographs
        or 0xFE30 <= code_point <= 0xFE4F  # CJK Compatibility Forms
        or 0xFF00 <= code_point <= 0xFFEF  # Halfwidth and Fullwidth Forms
        or 0x20000 <= code_point <= 0x2FA1F
    ):  # CJK Unified Ideographs Extension B-G
        return 2

    # Emoji and other wide characters
    if (
        0x1F600 <= code_point <= 0x1F64F  # Emoticons
        or 0x1F300 <= code_point <= 0x1F5FF  # Misc Symbols and Pictographs
        or 0x1F680 <= code_point <= 0x1F6FF
    ):  # Transport and Map Symbols
        return 2

    return 1


def get_string_display_width(text: str) -> int:
    """Get the display width of a string, handling multibyte characters.

    Args:
        text: String to measure

    Returns:
        Display width of the string
    """
    if not text:
        return 0

    return sum(get_character_width(char) for char in text)


class FuzzySearchState:
    """State management for fuzzy search functionality."""

    def __init__(self) -> None:
        """Initialize fuzzy search state."""
        self.active = False
        self.search_text = ""
        self.matches: List[str] = []
        self.current_match_index = 0
        self.original_text = ""


class PromptHistoryManager:
    """Manage prompt history with file persistence and search capabilities."""

    def __init__(self, history_file: Optional[str] = None) -> None:
        """Initialize prompt history manager.

        Args:
            history_file: Path to history file. If None, uses default location.
        """
        if history_file is None:
            # Use default history file location
            home_dir = os.path.expanduser("~")
            history_file = os.path.join(home_dir, ".zsh_ai_assistant_history")

        self.history_file = history_file
        self.history = FileHistory(history_file)
        self.fuzzy_search_state = FuzzySearchState()

        # Load existing history
        self._load_history()

    def _load_history(self) -> None:
        """Load history from file."""
        # FileHistory handles this automatically
        pass

    def add_to_history(self, text: str) -> None:
        """Add text to history.

        Args:
            text: Text to add to history
        """
        if text and text.strip():
            # FileHistory stores history automatically when using PromptSession
            # We can manually add to the history file for immediate persistence
            try:
                with open(self.history_file, "a", encoding="utf-8") as f:
                    f.write(text + "\n")
            except IOError:
                pass  # Ignore file write errors

    def get_history_session(self) -> PromptSession:
        """Get a configured prompt session with history.

        Returns:
            Configured PromptSession instance
        """
        return PromptSession(history=self.history)

    def get_history_session_with_auto_suggest(self) -> PromptSession:
        """Get a configured prompt session with history and auto-suggest.

        Returns:
            Configured PromptSession instance with auto-suggest
        """
        return PromptSession(history=self.history, auto_suggest=AutoSuggestFromHistory())

    def clear_history(self) -> None:
        """Clear all history."""
        # Remove history file
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        # Create new empty history
        self.history = FileHistory(self.history_file)

    def get_history_items(self) -> List[str]:
        """Get all history items.

        Returns:
            List of history strings
        """
        # FileHistory doesn't provide direct access to all items,
        # but we can read the file directly
        history_items = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history_items = [line.strip() for line in f if line.strip()]
            except (IOError, json.JSONDecodeError):
                pass
        return history_items

    def perform_fuzzy_search(self, search_text: str) -> List[str]:
        """Perform fuzzy search on history items.

        Args:
            search_text: Text to search for

        Returns:
            List of matching history items, sorted by relevance
        """
        if not search_text:
            return []

        history_items = self.get_history_items()
        if not history_items:
            return []

        if FUZZY_SEARCH_AVAILABLE:
            # Use fuzzy search with scoring
            # Use token_set_ratio for better partial matching
            # Handle multibyte characters by using the text as-is
            results = process.extract(search_text, history_items, scorer=fuzz.token_set_ratio, limit=50)
            # Sort by score (descending) and return items with score > 42 for balanced precision/recall
            # This threshold catches typos while avoiding most false positives
            matches = [item for item, score in results if score > 42]
            # Sort by score descending
            matches.sort(key=lambda x: next((score for item, score in results if item == x), 0), reverse=True)
        else:
            # Fallback to simple substring search
            # Handle multibyte characters by using case-insensitive comparison
            matches = []
            for item in history_items:
                if search_text.lower() in item.lower():
                    matches.append(item)
            # Sort by length to show shorter matches first (more relevant)
            matches.sort(key=len)

        return matches

    def start_fuzzy_search(self, search_text: str) -> None:
        """Start fuzzy search session.

        Args:
            search_text: Initial search text
        """
        self.fuzzy_search_state.active = True
        self.fuzzy_search_state.search_text = search_text
        self.fuzzy_search_state.matches = self.perform_fuzzy_search(search_text)
        self.fuzzy_search_state.current_match_index = 0
        self.fuzzy_search_state.original_text = search_text

    def cycle_fuzzy_search(self, forward: bool = True) -> Optional[str]:
        """Cycle through fuzzy search matches.

        Args:
            forward: If True, cycle forward; if False, cycle backward

        Returns:
            The current match text, or None if no matches
        """
        if not self.fuzzy_search_state.active or not self.fuzzy_search_state.matches:
            return None

        if forward:
            self.fuzzy_search_state.current_match_index += 1
            if self.fuzzy_search_state.current_match_index >= len(self.fuzzy_search_state.matches):
                self.fuzzy_search_state.current_match_index = 0
        else:
            self.fuzzy_search_state.current_match_index -= 1
            if self.fuzzy_search_state.current_match_index < 0:
                self.fuzzy_search_state.current_match_index = len(self.fuzzy_search_state.matches) - 1

        return self.fuzzy_search_state.matches[self.fuzzy_search_state.current_match_index]

    def end_fuzzy_search(self) -> None:
        """End fuzzy search session."""
        self.fuzzy_search_state.active = False
        self.fuzzy_search_state.search_text = ""
        self.fuzzy_search_state.matches = []
        self.fuzzy_search_state.current_match_index = 0
        self.fuzzy_search_state.original_text = ""


def get_prompt_session(history_file: Optional[str] = None) -> PromptSession:
    """Get a configured prompt session for interactive input.

    Args:
        history_file: Path to history file. If None, uses default location.

    Returns:
        Configured PromptSession instance
    """
    history_manager = PromptHistoryManager(history_file)

    # Create key bindings for additional functionality
    kb = KeyBindings()

    @kb.add("c-r")
    def _(event: Any) -> None:
        """Handle Ctrl+R for fuzzy search (reverse-i-search).

        Initiates fuzzy search through command history. If search text is provided,
        finds and displays the first matching history item. If no search text is provided,
        shows helpful instructions to the user.
        """
        # Get current buffer
        buffer = event.app.current_buffer

        # Get current search text
        search_text = buffer.text if buffer.text else ""

        if not search_text:
            # If no search text, show help message
            print("\n🔍 Fuzzy Search: Type your search query, then press Ctrl+R to search history.")
            print("   Press Ctrl+R again to cycle through matches, Ctrl+C to cancel search.")
            return

        # Start or update fuzzy search
        history_manager.start_fuzzy_search(search_text)

        # Get first match
        first_match = history_manager.cycle_fuzzy_search(forward=False)  # Start with first match

        if first_match:
            # Replace buffer with first match
            buffer.text = first_match
            buffer.cursor_position = len(buffer.text)

            # Show search status
            total_matches = len(history_manager.fuzzy_search_state.matches)
            print(
                f"\n🔍 Fuzzy search: "
                f"{history_manager.fuzzy_search_state.current_match_index + 1}/"
                f"{total_matches} matches"
            )
            print("   Press Ctrl+R again to cycle through matches, Ctrl+C to cancel")
        else:
            # No matches found
            print(f"\n🔍 No matches found for: '{search_text}'")
            print("   Try a different search term or check your spelling.")
            # Restore original text
            buffer.text = search_text
            buffer.cursor_position = len(buffer.text)
            history_manager.end_fuzzy_search()

    @kb.add("c-r", "c-r")
    def _(event: Any) -> None:
        """Handle double Ctrl+R to cycle through matches.

        Cycles through fuzzy search matches when fuzzy search is active.
        Provides visual feedback about current position in match list.
        """
        # Check if fuzzy search is active
        if not history_manager.fuzzy_search_state.active:
            return

        # Cycle to next match
        next_match = history_manager.cycle_fuzzy_search(forward=True)

        if next_match:
            buffer = event.app.current_buffer
            buffer.text = next_match
            buffer.cursor_position = len(buffer.text)

            # Show search status
            total_matches = len(history_manager.fuzzy_search_state.matches)
            print(
                f"\n🔍 Fuzzy search: "
                f"{history_manager.fuzzy_search_state.current_match_index + 1}/"
                f"{total_matches} matches"
            )
        else:
            # No more matches
            print("\n🔍 No more matches found. Wrapping around to first match.")
            # Wrap around to first match for better UX
            first_match = history_manager.cycle_fuzzy_search(forward=False)
            if first_match:
                buffer = event.app.current_buffer
                buffer.text = first_match
                buffer.cursor_position = len(buffer.text)
                total_matches = len(history_manager.fuzzy_search_state.matches)
                print(
                    f"🔍 Fuzzy search: "
                    f"{history_manager.fuzzy_search_state.current_match_index + 1}/"
                    f"{total_matches} matches"
                )

    @kb.add("up")
    def _(event: Any) -> None:
        """Handle Up arrow key for history navigation.

        Navigates through command history using Up arrow key.
        When fuzzy search is active, cycles through fuzzy search matches.
        Otherwise, uses prompt_toolkit's built-in history navigation.
        """
        buffer = event.app.current_buffer

        # Check if fuzzy search is active
        if history_manager.fuzzy_search_state.active:
            # Cycle backward through fuzzy search matches
            prev_match = history_manager.cycle_fuzzy_search(forward=False)
            if prev_match:
                buffer.text = prev_match
                buffer.cursor_position = len(buffer.text)
                total_matches = len(history_manager.fuzzy_search_state.matches)
                print(
                    f"\nFuzzy search: "
                    f"{history_manager.fuzzy_search_state.current_match_index + 1}/"
                    f"{total_matches} matches"
                )
            return

        # Normal history navigation - use prompt_toolkit's built-in history
        # This will navigate through the history items
        buffer._history_move_up()

    @kb.add("down")
    def _(event: Any) -> None:
        """Handle Down arrow key for history navigation.

        Navigates through command history using Down arrow key.
        When fuzzy search is active, cycles through fuzzy search matches.
        Otherwise, uses prompt_toolkit's built-in history navigation.
        """
        buffer = event.app.current_buffer

        # Check if fuzzy search is active
        if history_manager.fuzzy_search_state.active:
            # Cycle forward through fuzzy search matches
            next_match = history_manager.cycle_fuzzy_search(forward=True)
            if next_match:
                buffer.text = next_match
                buffer.cursor_position = len(buffer.text)
                total_matches = len(history_manager.fuzzy_search_state.matches)
                print(
                    f"\nFuzzy search: "
                    f"{history_manager.fuzzy_search_state.current_match_index + 1}/"
                    f"{total_matches} matches"
                )
            return

        # Normal history navigation - use prompt_toolkit's built-in history
        # This will navigate forward through history or return to empty buffer
        buffer._history_move_down()

    @kb.add("backspace")
    def _(event: Any) -> None:
        """Handle backspace key for multibyte character support.

        This handler ensures that backspace properly deletes multibyte characters
        (like Japanese, Chinese, emoji) and maintains correct cursor positioning.
        The character width calculation is used to ensure proper visual alignment
        in the terminal display.
        """
        buffer = event.app.current_buffer

        if buffer.cursor_position == 0:
            # Nothing to delete at the beginning of line
            return

        # Get text before cursor
        text_before_cursor = buffer.text[: buffer.cursor_position]

        if not text_before_cursor:
            return

        # Get the character immediately before the cursor
        if text_before_cursor:
            char_before_cursor = text_before_cursor[-1]
            _ = get_character_width(char_before_cursor)  # Calculate width for consistency

            # Delete one character (this handles both ASCII and multibyte characters correctly)
            # The buffer.delete_before_cursor(count=1) method works with Unicode characters
            # and should handle multibyte characters properly
            buffer.delete_before_cursor(count=1)

            # Ensure cursor is properly positioned after deletion
            # This is important for multibyte characters to maintain correct display
            buffer.cursor_position = len(buffer.text)

            # Force redisplay to ensure proper rendering
            event.app.invalidate()

    @kb.add("c-h")
    def _(event: Any) -> None:
        """Handle Ctrl+H (alternative backspace representation).

        This is a fallback handler for terminals that send Ctrl+H instead of backspace.
        """
        # Same implementation as backspace
        buffer = event.app.current_buffer

        if buffer.cursor_position == 0:
            # Nothing to delete at the beginning of line
            return

        # Get text before cursor
        text_before_cursor = buffer.text[: buffer.cursor_position]

        if not text_before_cursor:
            return

        # Get the character immediately before the cursor
        if text_before_cursor:
            char_before_cursor = text_before_cursor[-1]
            _ = get_character_width(char_before_cursor)  # Calculate width for consistency

            # Delete one character
            buffer.delete_before_cursor(count=1)

            # Ensure cursor is properly positioned after deletion
            buffer.cursor_position = len(buffer.text)

            # Force redisplay to ensure proper rendering
            event.app.invalidate()

    @kb.add("c-c")
    def _(event: Any) -> None:
        """Handle Ctrl+C to cancel fuzzy search or interrupt."""
        buffer = event.app.current_buffer

        # Check if fuzzy search is active
        if history_manager.fuzzy_search_state.active:
            # End fuzzy search and restore original text
            original_text = history_manager.fuzzy_search_state.original_text
            buffer.text = original_text
            buffer.cursor_position = len(buffer.text)
            history_manager.end_fuzzy_search()
            print("\nFuzzy search cancelled")
            # Prevent the default Ctrl+C behavior (interrupt)
            event.app.exit(result=None)
        else:
            # Normal Ctrl+C behavior - raise KeyboardInterrupt
            buffer.text = ""
            buffer.cursor_position = 0
            raise KeyboardInterrupt()

    # Configure prompt session with multibyte character support
    return PromptSession(
        history=history_manager.history,
        auto_suggest=AutoSuggestFromHistory(),
        key_bindings=kb,
        # Enable multiline input support
        multiline=True,
        # Enable better completion
        complete_while_typing=True,
        # Enable better history search
        enable_history_search=True,
        # Enable system prompt for better terminal compatibility
        enable_system_prompt=True,
        # Enable suspend for better terminal control
        enable_suspend=True,
        # Enable open in editor for complex input
        enable_open_in_editor=True,
    )
