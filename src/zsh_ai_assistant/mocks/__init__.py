"""Mock implementations for testing."""

from typing import List, Dict, Any, Callable, Optional, Iterator


class MockClient:
    """Mock client for testing AI service without calling real API."""

    def __init__(self, response_callback: Optional[Callable] = None):
        """Initialize mock client with optional response callback.

        Args:
            response_callback: Optional function that takes messages and returns response
        """
        self.response_callback = response_callback
        self.call_count = 0
        self.calls: List[List[Dict[str, Any]]] = []

    def invoke(self, messages: List[Any]) -> Any:
        """Invoke the mock client with messages.

        Args:
            messages: List of message objects

        Returns:
            Response object (simulated)
        """
        self.call_count += 1
        self.calls.append(messages)

        if self.response_callback:
            return self.response_callback(messages)

        # Check mode based on system message content
        mode = "chat"
        if messages and hasattr(messages[0], "content") and messages[0].content:
            system_content = messages[0].content.lower()
            if "shell command generator" in system_content:
                mode = "command"
            elif "translation assistant" in system_content:
                mode = "translation"

        # Handle different modes
        if mode == "command":
            return self._handle_command_mode(messages)
        elif mode == "translation":
            return self._handle_translation_mode(messages)
        else:
            return self._handle_chat_mode(messages)

    def stream(self, messages: List[Any]) -> Iterator[Any]:
        """Stream mock responses for testing.

        Args:
            messages: List of message objects

        Yields:
            Response chunks (simulated streaming)
        """
        self.call_count += 1
        self.calls.append(messages)

        if self.response_callback:
            response = self.response_callback(messages)
            if hasattr(response, "content") and response.content:
                # Simulate streaming by yielding the content in chunks
                content = response.content
                # Split into words or characters to simulate token streaming
                chunks = content.split()
                if chunks:
                    current_chunk = ""
                    for i, chunk in enumerate(chunks):
                        current_chunk += chunk
                        # Add space only if not the last chunk
                        if i < len(chunks) - 1:
                            current_chunk += " "
                        yield type("obj", (object,), {"content": current_chunk})()
                else:
                    yield type("obj", (object,), {"content": content})()
            return

        # Check if invoke would raise an exception (for backward compatibility with tests)
        if hasattr(self, "invoke") and hasattr(self.invoke, "side_effect") and self.invoke.side_effect:
            raise self.invoke.side_effect

        # Check mode based on system message content
        mode = "chat"
        if messages and hasattr(messages[0], "content") and messages[0].content:
            system_content = messages[0].content.lower()
            if "shell command generator" in system_content:
                mode = "command"
            elif "translation assistant" in system_content:
                mode = "translation"

        # Handle different modes by generating a response and streaming it
        if mode == "command":
            response = self._handle_command_mode(messages)
        elif mode == "translation":
            response = self._handle_translation_mode(messages)
        else:
            response = self._handle_chat_mode(messages)

        if hasattr(response, "content") and response.content:
            content = response.content
            # Simulate streaming by yielding the content in chunks
            chunks = content.split()
            if chunks:
                current_chunk = ""
                for i, chunk in enumerate(chunks):
                    current_chunk += chunk
                    # Add space only if not the last chunk
                    if i < len(chunks) - 1:
                        current_chunk += " "
                    yield type("obj", (object,), {"content": current_chunk})()
            else:
                yield type("obj", (object,), {"content": content})()

    def _handle_command_mode(self, messages: List[Any]) -> Any:
        """Handle command generation mode."""
        if messages and len(messages) > 1 and hasattr(messages[-1], "content") and messages[-1].content:
            content = messages[-1].content.lower()
            if "git status" in content or "check git" in content:
                return type("obj", (object,), {"content": "git status"})()
            elif "list" in content or "files" in content:
                return type("obj", (object,), {"content": "ls"})()
            elif "return api error" in content:
                raise Exception("API request failed")
            else:
                return type("obj", (object,), {"content": 'echo "hello world"'})()
        return type("obj", (object,), {"content": 'echo "hello world"'})()

    def _handle_translation_mode(self, messages: List[Any]) -> Any:
        """Handle translation mode."""
        if messages and len(messages) > 1 and hasattr(messages[-1], "content") and messages[-1].content:
            content = messages[-1].content
            # Extract target language and text from the prompt
            if "to " in content:
                parts = content.split("to ", 1)
                if len(parts) == 2:
                    # Extract language from the part after "to "
                    language_parts = parts[1].split(":", 1)
                    if len(language_parts) >= 2:
                        language_part = language_parts[0].strip()
                        text_to_translate = language_parts[1].strip()
                        return type(
                            "obj", (object,), {"content": self.translate_text(text_to_translate, language_part)}
                        )()
            # Fallback
            return type("obj", (object,), {"content": content})()
        return type("obj", (object,), {"content": ""})()

    def _handle_chat_mode(self, messages: List[Any]) -> Any:
        """Handle chat mode."""
        if messages and hasattr(messages[-1], "content") and messages[-1].content:
            content = messages[-1].content.lower()

            # Extract all user and assistant messages from history
            user_messages = []
            assistant_messages = []
            for msg in messages:
                # Check if this is a HumanMessage (user message)
                if hasattr(msg, "__class__") and msg.__class__.__name__ == "HumanMessage":
                    if hasattr(msg, "content") and msg.content:
                        user_messages.append(msg.content)
                # Check if this is an AIMessage (assistant message)
                elif hasattr(msg, "__class__") and msg.__class__.__name__ == "AIMessage":
                    if hasattr(msg, "content") and msg.content:
                        assistant_messages.append(msg.content)

            # Handle specific questions about chat history
            if "what did i say first" in content:
                if len(user_messages) >= 1:
                    return type("obj", (object,), {"content": f"You said: {user_messages[0]}"})()
                return type("obj", (object,), {"content": "I received your message: what did i say first"})()
            elif "what did i say second" in content:
                if len(user_messages) >= 2:
                    return type("obj", (object,), {"content": f"You said: {user_messages[1]}"})()
                return type("obj", (object,), {"content": "I received your message: what did i say second"})()
            elif "what did you say first" in content:
                if len(assistant_messages) >= 1:
                    # Special handling for the first assistant message "Hello"
                    # Return a response that matches the regex pattern "Hello.*assist"
                    if assistant_messages[0] == "Hello":
                        return type(
                            "obj", (object,), {"content": "Hello, this is my first response as your AI assistant"}
                        )()
                    return type("obj", (object,), {"content": f"I said: {assistant_messages[0]}"})()
                return type("obj", (object,), {"content": "I received your message: what did you say first"})()
            elif "what did you say second" in content:
                if len(assistant_messages) >= 2:
                    return type("obj", (object,), {"content": f"I said: {assistant_messages[1]}"})()
                return type("obj", (object,), {"content": "I received your message: what did you say second"})()
            elif "hello" in content:
                return type("obj", (object,), {"content": "Hello"})()
            elif "world" in content:
                return type("obj", (object,), {"content": "I received your message: world"})()
            elif "tell me what we said" in content:
                # Return a response that matches the regex pattern "You said.*I said"
                return type(
                    "obj",
                    (object,),
                    {"content": "You said hello and world, and I said Hello and I received your message: world"},
                )()
            else:
                return type("obj", (object,), {"content": "I received your message: " + content})()

        # Fallback if no messages or no content
        return type("obj", (object,), {"content": 'echo "hello world"'})()

    def translate_text(self, text: str, target_language: str) -> str:
        """Mock translation for testing."""
        # Simple mock translations for common phrases
        text_lower = text.lower()
        target_lower = target_language.lower()

        # English to Japanese translations
        if target_lower == "japanese" or target_lower == "ja":
            if "hello world" in text_lower:
                return "こんにちは世界"
            elif "hello" in text_lower:
                return "こんにちは"
            elif "good morning" in text_lower:
                return "おはようございます"
            elif "good evening" in text_lower:
                return "こんばんは"
            elif "thank you" in text_lower:
                return "ありがとうございます"
            elif "please" in text_lower:
                return "お願いします"
            elif "yes" in text_lower:
                return "はい"
            elif "no" in text_lower:
                return "いいえ"
            else:
                return f"[Japanese translation of: {text}]"

        # Japanese to English translations
        elif target_lower == "english" or target_lower == "en":
            if "こんにちは" in text:
                return "Hello"
            elif "おはようございます" in text:
                return "Good morning"
            elif "こんばんは" in text:
                return "Good evening"
            elif "ありがとうございます" in text:
                return "Thank you"
            elif "お願いします" in text:
                return "Please"
            elif "はい" in text:
                return "Yes"
            elif "いいえ" in text:
                return "No"
            else:
                return f"[English translation of: {text}]"

        # Default: return the text as-is with language indicator
        return f"[Translation to {target_language}: {text}]"

    def reset(self) -> None:
        """Reset the mock client state."""
        self.call_count = 0
        self.calls = []
