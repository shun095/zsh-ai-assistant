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

    def __init__(self, test_mode: bool = False) -> None:
        """Initialize interactive chat session."""
        self.test_mode = test_mode
        self.config = AIConfig()

        # Setup logging based on config
        setup_logging(self.config.debug)
        logger.debug("Initializing interactive chat with config: %s", self.config)
        logger.debug("Test mode: %s", test_mode)

        self.service = LangChainAIService(self.config, test_mode=test_mode)
        self.chat_history: List[Dict[str, Any]] = []
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

        while True:
            try:
                # Display prompt
                print("Me: ", end="", flush=True)

                # Read user input
                user_input = sys.stdin.readline().strip()

                # Check for exit commands
                if not user_input or user_input.lower() in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break

                # Generate response
                self.generate_response(user_input)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                break


def main(test_mode: bool = False) -> None:
    """Main entry point for interactive chat."""
    # Check for test mode using environment variable
    if test_mode is False:  # Only check if not explicitly set
        test_mode = os.environ.get("ZSH_AI_ASSISTANT_TEST_MODE") is not None

    try:
        chat = InteractiveChat(test_mode=test_mode)
        chat.run_interactive_chat()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
