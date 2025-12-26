#!/usr/bin/env python3
"""CLI utilities for zsh-ai-assistant."""

import json
import os
import sys
import logging
from typing import List, Dict, Any, Callable, TypeVar

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

# Type variable for generic service methods
T = TypeVar("T")


def _get_ai_service(test_mode: bool = False) -> LangChainAIService:
    """Create and return an AI service instance with common setup.

    Args:
        test_mode: If True, use mock client for testing

    Returns:
        Configured AI service instance

    Raises:
        SystemExit: If configuration is invalid and not in test mode
    """
    # Load configuration
    config = AIConfig()

    # Setup logging based on config
    setup_logging(config.debug)
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

    return service


def _execute_service_method(service_method: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Execute a service method with error handling.

    Args:
        service_method: The service method to execute
        *args: Positional arguments for the method
        **kwargs: Keyword arguments for the method

    Returns:
        The result of the service method

    Raises:
        SystemExit: If an error occurs during execution
    """
    try:
        result = service_method(*args, **kwargs)
        logger.debug("Service method result: %s", result)
        return result
    except Exception as e:
        logger.error("Error executing service method: %s", e)
        # Return error message as a commented line so zsh plugin knows not to execute it
        error_message = f"# Error: {e}"
        print(error_message)
        sys.exit(1)


def generate_command(prompt: str, test_mode: bool = False) -> str:
    """Generate a shell command from a natural language prompt."""
    logger.debug("Generate command called with prompt: %s", prompt)

    # Create AI service
    service = _get_ai_service(test_mode)

    # Generate command
    logger.info("Generating command from prompt")
    command = _execute_service_method(service.generate_command, prompt)

    return command.strip()


def chat(messages_json: str, test_mode: bool = False) -> str:
    """Generate a response from chat history.

    Expected input format (OpenAI API compatible):
    [
        {"role": "user", "content": "message"},
        {"role": "assistant", "content": "response"}
    ]

    Returns response content only (not wrapped in JSON).
    """
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

    # Create AI service
    service = _get_ai_service(test_mode)

    # Generate response using OpenAI format
    logger.info("Generating chat response")
    response = _execute_service_method(service.chat, messages)

    return response.strip()


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


def translate(text: str, target_language: str, test_mode: bool = False) -> str:
    """Translate text to a target language."""
    logger.debug("Translate called with text: %s, target_language: %s", text, target_language)

    # Create AI service
    service = _get_ai_service(test_mode)

    # Translate text
    logger.info("Translating text")
    translation = _execute_service_method(service.translate, text, target_language)

    return translation.strip()


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
    # Check for test mode using environment variable
    test_mode = os.environ.get("ZSH_AI_ASSISTANT_TEST_MODE") is not None

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

        elif len(sys.argv) > 1 and sys.argv[1] == "translate":
            # Translation mode
            if len(sys.argv) < 3:
                print("Usage: translate <target_language> [text]", file=sys.stderr)
                sys.exit(1)
            target_language = sys.argv[2]
            if len(sys.argv) > 3:
                text = sys.argv[3]
            else:
                text = sys.stdin.read().strip()
            result = translate(text, target_language, test_mode)
            print(result)

        else:
            print("Usage:", file=sys.stderr)
            print("  command <prompt> - Generate command from prompt", file=sys.stderr)
            print("  chat - Chat with AI (reads JSON from stdin)", file=sys.stderr)
            print(
                "  history-to-json - Convert history to JSON " "(reads from stdin)",
                file=sys.stderr,
            )
            print("  interactive - Run interactive chat session", file=sys.stderr)
            print("  translate <target_language> <text> - Translate text to target language", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
