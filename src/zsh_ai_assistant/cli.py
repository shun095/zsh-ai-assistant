#!/usr/bin/env python3
"""CLI utilities for zsh-ai-assistant."""

import sys
import json
from typing import List, Dict, Any
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

        # Special case: simulate API error
        if "return api error" in prompt.lower():
            return "# Error: API request failed"

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
        # Return error message as a commented line so zsh plugin knows not to execute it
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
        # Test mode: simulate AI responses based on content
        # Get the last user message (expecting OpenAI format)
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]

        if not user_messages:
            return "No user messages found"

        last_user_message = user_messages[-1].get("content", "")

        # Simulate AI responses
        if last_user_message.lower() == "hello":
            # Return just the greeting text (no JSON wrapper)
            # This simulates a real AI response
            return "Hello! How can I assist you today?"
        elif "what did i say first" in last_user_message.lower():
            # Check if there are previous user messages in the conversation history
            if len(user_messages) >= 2:
                # Return the first message content
                first_message = user_messages[0].get("content", "")
                return f"You said '{first_message}' first"
            else:
                return "This is your first message."
        elif "what did i say second" in last_user_message.lower():
            # Check if there are at least 3 user messages in the conversation history
            if len(user_messages) >= 3:
                # Return the second message content
                second_message = user_messages[1].get("content", "")
                return f"You said '{second_message}' second"
            elif len(user_messages) >= 2:
                return "This is your second message."
            else:
                return "This is your first message."
        elif "what did you say first" in last_user_message.lower():
            # Check if there are previous assistant messages in the conversation history
            if len(assistant_messages) >= 1:
                # Return the first assistant message content
                first_assistant_message = assistant_messages[0].get("content", "")
                return f"I said '{first_assistant_message}' first"
            else:
                return "This is my first response."
        elif "what did you say second" in last_user_message.lower():
            # Check if there are at least 2 assistant messages in the conversation history
            if len(assistant_messages) >= 2:
                # Return the second assistant message content
                second_assistant_message = assistant_messages[1].get("content", "")
                return f"I said '{second_assistant_message}' second"
            elif len(assistant_messages) >= 1:
                return "This is my second response."
            else:
                return "This is my first response."
        elif last_user_message.lower() == "world":
            # For 'world' message, return a simple acknowledgment
            return f"I received your message: {last_user_message}"
        elif "tell me what we said" in last_user_message.lower():
            # Provide a summary of the conversation
            if user_messages and assistant_messages:
                return f"You said: {user_messages[0].get('content', '')}. I said: {assistant_messages[0].get('content', '')}"
            else:
                return "We haven't said much yet."
        else:
            # For other messages, return a simple acknowledgment
            # The conversation history is managed by zsh using jq
            return f"I received your message: {last_user_message}"

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
        # Generate response using OpenAI format
        response = service.chat(messages)
        return response.strip()
    except Exception as e:
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
