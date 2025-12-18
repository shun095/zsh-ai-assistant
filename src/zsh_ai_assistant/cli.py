#!/usr/bin/env python3
"""CLI utilities for zsh-ai-assistant."""

import sys
import json
from zsh_ai_assistant.config import AIConfig
from zsh_ai_assistant.ai_service import LangChainAIService


def generate_command(prompt: str, test_mode: bool = False) -> str:
    """Generate a shell command from a natural language prompt."""
    # Load configuration
    config = AIConfig()

    # Check if we're in test mode (no API key required)
    if test_mode:
        # Simple test mode: map common prompts to commands
        test_prompts = {
            "check git current status": "git status",
            "list current directory files": "ls",
        }
        for key, cmd in test_prompts.items():
            if key in prompt.lower():
                return cmd

        # Default fallback for test mode
        return 'echo "hello world"'

    # Normal mode: require valid configuration
    if not config.is_valid:
        print(
            "Error: Invalid AI configuration. Please set " "OPENAI_API_KEY and OPENAI_BASE_URL",
            file=sys.stderr,
        )
        sys.exit(1)

    # Create AI service
    service = LangChainAIService(config)

    try:
        # Generate command
        command = service.generate_command(prompt)
        return command.strip()
    except Exception as e:
        print(f"Error generating command: {e}", file=sys.stderr)
        sys.exit(1)


def chat(messages_json: str, test_mode: bool = False) -> str:
    """Generate a response from chat history."""
    if not messages_json:
        print("Error: No chat history provided", file=sys.stderr)
        sys.exit(1)

    try:
        messages = json.loads(messages_json)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}", file=sys.stderr)
        sys.exit(1)

    # Check if we're in test mode (no API key required)
    if test_mode:
        # Simple test mode: return a generic response
        last_message = messages[-1] if messages else {"content": "hello"}
        content = last_message.get("content", "your message")
        # If the content is 'hello', return a friendly greeting
        if content.lower() == "hello":
            return "Hello! How can I assist you today? 😊"
        return f"I received: {content}"

    # Load configuration
    config = AIConfig()
    if not config.is_valid:
        print(
            "Error: Invalid AI configuration. Please set " "OPENAI_API_KEY and OPENAI_BASE_URL",
            file=sys.stderr,
        )
        sys.exit(1)

    # Create AI service
    service = LangChainAIService(config)

    try:
        # Generate response
        response = service.chat(messages)
        return response.strip()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def history_to_json(history_lines: str) -> str:
    """Convert chat history format to JSON format."""
    # Read chat history from stdin
    lines = history_lines.strip().split("\n")

    # Convert chat history to messages format
    messages = []
    for line in lines:
        line = line.strip()
        if line and ":" in line:
            role, content = line.split(":", 1)
            messages.append({"role": role, "content": content})

    # Output JSON
    return json.dumps(messages)


def main() -> None:
    """Main entry point for CLI utilities."""
    # Check if --test flag is present BEFORE removing it
    test_mode = "--test" in sys.argv

    # Remove --test flag if present to simplify argument parsing
    if test_mode:
        sys.argv.remove("--test")

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

    else:
        print("Usage:", file=sys.stderr)
        print("  command <prompt> - Generate command from prompt", file=sys.stderr)
        print("  chat - Chat with AI (reads JSON from stdin)", file=sys.stderr)
        print(
            "  history-to-json - Convert history to JSON " "(reads from stdin)",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
