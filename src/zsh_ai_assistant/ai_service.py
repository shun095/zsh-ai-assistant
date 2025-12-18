"""AI service implementation using LangChain."""

from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from .interfaces import AIServiceInterface
from .config import AIConfig


class LangChainAIService(AIServiceInterface):
    """AI service implementation using LangChain and OpenAI API."""

    def __init__(self, config: AIConfig):
        """Initialize AI service with configuration."""
        if not config.is_valid:
            raise ValueError(
                "Invalid AI configuration: API key and base URL are required"
            )

        self.config = config
        self.client = ChatOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

    def generate_command(self, prompt: str) -> str:
        """Generate a shell command from a natural language prompt."""
        system_message = SystemMessage(
            content=(
                "You are a shell command generator. "
                "Your task is to convert natural language requests into "
                "appropriate shell commands. Return ONLY the command without "
                "any explanation or markdown formatting. If the request is "
                "ambiguous, return the most likely command."
            )
        )
        human_message = HumanMessage(content=prompt)

        response = self.client.invoke([system_message, human_message])
        return str(response.content)

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """Generate a response from a chat history."""
        # Convert messages to LangChain format
        langchain_messages = []

        # Add default system message if no system message is provided
        has_system_message = any(msg.get("role") == "system" for msg in messages)
        if not has_system_message:
            system_message = SystemMessage(
                content=(
                    "You are a helpful AI assistant. "
                    "Provide concise, accurate responses to user questions. "
                    "Be friendly and professional."
                )
            )
            langchain_messages.append(system_message)

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))

        response = self.client.invoke(langchain_messages)
        return str(response.content)
