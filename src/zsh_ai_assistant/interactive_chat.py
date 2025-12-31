#!/usr/bin/env python3
"""Interactive chat functionality for zsh-ai-assistant."""

import json
import sys
import logging
from typing import List, Dict, Any
import os

# Add the src directory to Python path to ensure module can be imported
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from zsh_ai_assistant.config import AIConfig, setup_logging  # noqa: E402
from zsh_ai_assistant.ai_service import LangChainAIService  # noqa: E402


# Get logger
logger = logging.getLogger(__name__)


class InteractiveChat:
    """Interactive chat session with AI."""

    def __init__(self, test_mode: bool | None = None) -> None:
        """Initialize interactive chat session."""
        # Check for test mode using environment variable if not explicitly set
        if test_mode is None:
            test_mode_value = os.environ.get("ZSH_AI_ASSISTANT_TEST_MODE", "").lower()
            test_mode = test_mode_value in ("true", "1", "yes", "on")

        self.test_mode = test_mode
        self.config = AIConfig()

        # Setup logging based on config
        setup_logging(self.config.debug)
        logger.debug("Initializing interactive chat with config: %s", self.config)
        logger.debug("Test mode: %s", test_mode)

        self.service = LangChainAIService(self.config, test_mode=test_mode)
        self.chat_history: List[Dict[str, Any]] = []

        # Import here to avoid circular imports
        from zsh_ai_assistant.prompt_history import PromptHistoryManager

        # Create a single history manager instance to be shared
        self.history_manager = PromptHistoryManager()
        self.prompt_session = self.history_manager.get_history_session_with_auto_suggest()
        logger.info("Interactive chat session initialized")

    def add_user_message(self, content: str) -> None:
        """Add user message to chat history."""
        self.chat_history.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        """Add assistant message to chat history."""
        self.chat_history.append({"role": "assistant", "content": content})

    def get_chat_history_json(self) -> str:
        """Get current chat history as JSON."""
        return json.dumps(self.chat_history)

    def generate_response(self, user_input: str) -> str:
        """Generate AI response to user input."""
        # Add user message to history
        logger.debug("User input: %s", user_input)
        self.add_user_message(user_input)

        # Add to prompt history for Up/Down navigation
        # Use the shared history manager instance
        self.history_manager.add_to_history(user_input)

        try:
            # Generate response using the AI service with streaming
            logger.info("Generating AI response with streaming")
            # Use streaming for better user experience
            # Print AI: prefix first
            print("AI: ", end="", flush=True)

            response_parts: list[str] = []
            for chunk in self.service.chat_stream(self.chat_history):
                response_parts.append(chunk)
                # Print chunk as it arrives for streaming effect
                print(chunk, end="", flush=True)

            response = "".join(response_parts).strip()

            # Add assistant response to history
            logger.debug("AI response: %s", response)
            self.add_assistant_message(response)

            # Print newline after AI response to separate from next prompt
            print(flush=True)

            return response
        except Exception as e:
            logger.error("Error generating response: %s", e)
            error_message = f"Error: {e}"
            # Add error as assistant message for context
            self.add_assistant_message(error_message)
            raise Exception(error_message)

    def run_interactive_chat(self) -> None:
        """Run interactive chat session."""
        print("Starting AI chat. Type 'quit', 'exit', or 'q' to end.")
        print("Use Up/Down arrows to navigate history, Ctrl+R for fuzzy search.")

        while True:
            try:
                # Display prompt using prompt_toolkit
                user_input = self.prompt_session.prompt("Me: ")

                # Check for exit commands
                if not user_input or user_input.lower() in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break

                # Generate response
                self.generate_response(user_input)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                break

    def run_interactive_translation(self, target_language: str) -> None:
        """Run interactive translation session.

        Args:
            target_language: Target language for translation
        """
        # Check if we're in test mode - if so, simulate interactive behavior
        if self.test_mode:
            # In test mode, simulate interactive session for compatibility with shell tests
            import sys

            # Print the initial prompt to simulate interactive mode
            print("Translate: ", end="", flush=True)

            # Read from stdin line by line to simulate multiple inputs
            while True:
                try:
                    # Read a line from stdin
                    line = sys.stdin.readline()
                    if not line:  # EOF
                        break

                    text = line.strip()

                    # Check for exit commands
                    if not text or text.lower() in ("quit", "exit", "q"):
                        print("Goodbye!")
                        break

                    # Translate the text
                    if text:
                        self.translate_text(text, target_language)
                        # Print the prompt again for next input
                        print("\nTranslate: ", end="", flush=True)

                except Exception as e:
                    print(f"\nError: {e}")
                    break

            return

        print(f"Starting translation to {target_language}. Type 'quit', 'exit', or 'q' to end.")
        print("Use Up/Down arrows to navigate history, Ctrl+R for fuzzy search.")
        print("Enter text to translate, then press Enter.")

        while True:
            try:
                # Display prompt using prompt_toolkit
                user_input = self.prompt_session.prompt("Translate: ")

                # Check for exit commands
                if not user_input or user_input.lower() in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break

                # Translate the text
                if user_input:
                    self.translate_text(user_input, target_language)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                break

    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language.

        Args:
            text: Text to translate
            target_language: Target language

        Returns:
            The translated text
        """
        logger.debug("Translating text: %s, target_language: %s", text, target_language)

        # Add to prompt history for Up/Down navigation
        # Use the shared history manager instance
        self.history_manager.add_to_history(text)

        try:
            # Translate text using the AI service with streaming
            logger.info("Translating text with streaming")

            # Print translation prefix
            print(f"→ {target_language}: ", end="", flush=True)

            translation_parts: list[str] = []
            for chunk in self.service.translate_stream(text, target_language):
                translation_parts.append(chunk)
                # Print chunk as it arrives for streaming effect
                print(chunk, end="", flush=True)

            translation = "".join(translation_parts).strip()

            # Print newline after translation to separate from next prompt
            print(flush=True)

            return translation
        except Exception as e:
            logger.error("Error translating text: %s", e)
            error_message = f"Error: {e}"
            raise Exception(error_message)


def main(test_mode: bool | None = None) -> None:
    """Main entry point for interactive chat."""
    # Check for test mode using environment variable
    if test_mode is None:  # Only check if not explicitly set
        test_mode_value = os.environ.get("ZSH_AI_ASSISTANT_TEST_MODE", "").lower()
        test_mode = test_mode_value in ("true", "1", "yes", "on")

    try:
        chat = InteractiveChat(test_mode=test_mode)

        # Check if this is an interactive translation request
        if len(sys.argv) > 1 and sys.argv[1] == "translate":
            if len(sys.argv) < 3:
                print("Usage: translate <target_language>", file=sys.stderr)
                sys.exit(1)
            target_language = sys.argv[2]
            chat.run_interactive_translation(target_language)
        else:
            # Default: run interactive chat
            chat.run_interactive_chat()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
