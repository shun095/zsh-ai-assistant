#!/usr/bin/env python3
"""CLI utilities for zsh-ai-assistant."""

import json
import os
import sys
import logging
from typing import List, Dict, Any

# Add the src directory to Python path to ensure module can be imported
# This allows the script to be run from any directory
_src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Import after path manipulation
from zsh_ai_assistant.config import AIConfig, setup_logging  # noqa: E402
from zsh_ai_assistant.ai_service import LangChainAIService  # noqa: E402
from zsh_ai_assistant.interactive_chat import InteractiveChat  # noqa: E402

# Get logger
logger = logging.getLogger(__name__)


def generate_command(prompt: str, test_mode: bool = False) -> str:
    """Generate a shell command from a natural language prompt."""
    # Load configuration
    config = AIConfig()

    # Setup logging based on config
    setup_logging(config.debug)
    logger.debug("Generate command called with prompt: %s", prompt)
    logger.debug("Configuration: %s", config)

    # Normal mode: require valid configuration
    if not test_mode and not config.is_valid:
        logger.error("Invalid AI configuration")
        print(
            "Error: Invalid AI configuration. Please set " "OPENAI_API_KEY and OPENAI_BASE_URL",
            file=sys.stderr,
        )
        sys.exit(1)

    # Create AI service with test mode
    logger.info("Creating AI service")
    service = LangChainAIService(config, test_mode=test_mode)

    try:
        # Generate command
        logger.info("Generating command from prompt")
        command = service.generate_command(prompt)
        logger.debug("Generated command: %s", command)
        return command.strip()
    except Exception as e:
        # Return error message as a commented line so zsh plugin knows not to execute it
        logger.error("Error generating command: %s", e)
        error_message = f"# Error: {e}"
        print(error_message)
        sys.exit(1)


def chat(messages_json: str, test_mode: bool = False) -> str:
    """Generate a response from chat history.

    Expected input format (OpenAI API compatible):
    [
        {"role": "user", "content": "message"},
        {"role": "assistant", "content": "response"}
    ]

    Returns response content only (not wrapped in JSON).
    """
    # Load configuration first to setup logging
    config = AIConfig()
    setup_logging(config.debug)
    logger.debug("Chat called with messages_json length: %d", len(messages_json))

    if not messages_json:
        logger.error("No chat history provided")
        print("Error: No chat history provided", file=sys.stderr)
        sys.exit(1)

    try:
        messages = json.loads(messages_json)
        logger.debug("Parsed messages: %s", messages)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON format: %s", e)
        print(f"Error: Invalid JSON format: {e}", file=sys.stderr)
        sys.exit(1)

    # Normal mode: require valid configuration
    if not test_mode and not config.is_valid:
        logger.error("Invalid AI configuration")
        print(
            "Error: Invalid AI configuration. Please set " "OPENAI_API_KEY and OPENAI_BASE_URL",
            file=sys.stderr,
        )
        sys.exit(1)

    # Create AI service with test mode
    logger.info("Creating AI service")
    service = LangChainAIService(config, test_mode=test_mode)

    try:
        # Generate response using OpenAI format
        logger.info("Generating chat response")
        response = service.chat(messages)
        logger.debug("Generated response: %s", response)
        return response.strip()
    except Exception as e:
        logger.error("Error generating chat response: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def history_to_json(history_lines: str) -> str:
    """Convert chat history format to OpenAI API compatible JSON format.

    Input format: "user:message" or "assistant:message"
    Output format: [{"role": "user", "content": "message"}]
    """
    # Read chat history from stdin
    # Handle both actual newlines and the literal string "$'\n'" that zsh might pass
    lines = history_lines.replace("$'\\n'", "").strip().split("\n")

    # Convert chat history to OpenAI API format
    messages = []
    for line in lines:
        line = line.strip()
        if line and ":" in line:
            role, content = line.split(":", 1)
            # Use OpenAI API format: {"role": "user/assistant", "content": "message"}
            messages.append({"role": role, "content": content})

    # Output JSON
    return json.dumps(messages)


def convert_to_openai_format(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert messages from {"user": "content"} format to OpenAI API format {"role": "user", "content": "content"}."""
    openai_messages = []
    for msg in messages:
        # Check if message is already in OpenAI format
        if "role" in msg and "content" in msg:
            openai_messages.append(msg)
        # Convert from {"user": "content"} format
        elif "user" in msg:
            openai_messages.append({"role": "user", "content": msg["user"]})
        elif "assistant" in msg:
            openai_messages.append({"role": "assistant", "content": msg["assistant"]})
        elif "system" in msg:
            openai_messages.append({"role": "system", "content": msg["system"]})
        else:
            # If format is unknown, keep as-is
            openai_messages.append(msg)

    return openai_messages


def run_interactive_chat(test_mode: bool = False) -> None:
    """Run interactive chat session."""
    # Load configuration first to setup logging
    config = AIConfig()
    setup_logging(config.debug)
    logger.debug("Running interactive chat with test_mode: %s", test_mode)

    try:
        logger.info("Starting interactive chat session")
        chat = InteractiveChat(test_mode=test_mode)
        chat.run_interactive_chat()
    except Exception as e:
        logger.error("Error in interactive chat: %s", e)
        print(f"Error: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for CLI utilities."""
    # Check if --test flag is present BEFORE removing it
    test_mode = "--test" in sys.argv

    # Remove --test flag if present to simplify argument parsing
    if test_mode:
        sys.argv.remove("--test")

    try:
        if len(sys.argv) > 1 and sys.argv[1] == "command":
            # Command generation mode
            if len(sys.argv) > 2:
                prompt = sys.argv[2]
            else:
                prompt = sys.stdin.read().strip()

            result = generate_command(prompt, test_mode)
            print(result)

        elif len(sys.argv) > 1 and sys.argv[1] == "chat":
            # Chat mode
            chat_history_json = sys.stdin.read().strip()
            result = chat(chat_history_json, test_mode)
            print(result)

        elif len(sys.argv) > 1 and sys.argv[1] == "history-to-json":
            # History to JSON mode
            history_lines = sys.stdin.read().strip()
            result = history_to_json(history_lines)
            print(result)

        elif len(sys.argv) > 1 and sys.argv[1] == "interactive":
            # Interactive chat mode
            run_interactive_chat(test_mode)

        else:
            print("Usage:", file=sys.stderr)
            print("  command <prompt> - Generate command from prompt", file=sys.stderr)
            print("  chat - Chat with AI (reads JSON from stdin)", file=sys.stderr)
            print(
                "  history-to-json - Convert history to JSON " "(reads from stdin)",
                file=sys.stderr,
            )
            print("  interactive - Run interactive chat session", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
