"""AI service implementation using LangChain."""

import logging
from typing import List, Dict, Any, cast, Union
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from .interfaces import AIServiceInterface
from .config import AIConfig
from .mocks import MockClient

# Get logger
logger = logging.getLogger(__name__)


class LangChainAIService(AIServiceInterface):
    """AI service implementation using LangChain and OpenAI API."""

    def __init__(self, config: AIConfig, test_mode: bool = False):
        """Initialize AI service with configuration.

        Args:
            config: AI configuration
            test_mode: If True, use mock client for testing
        """
        self.config = config
        self.test_mode = test_mode
        self.client: Union[MockClient, ChatOpenAI]

        logger.debug("Initializing AI service with config: %s", config)
        logger.debug("Test mode: %s", test_mode)

        if test_mode:
            # Use mock client for testing
            logger.info("Using mock client for testing")
            self.client = MockClient()
        else:
            # Use real ChatOpenAI client
            if not config.is_valid:
                raise ValueError("Invalid AI configuration: API key and base URL are required")

            logger.info("Using real ChatOpenAI client")
            self.client = ChatOpenAI(
                api_key=config.api_key,  # type: ignore[arg-type]
                base_url=config.base_url,
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,  # type: ignore[call-arg]
            )

    def generate_command(self, prompt: str) -> str:
        """Generate a shell command from a natural language prompt."""
        logger.debug("Generating command for prompt: %s", prompt)

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

        logger.debug("Calling AI service with system message and human message")
        response = self.client.invoke([system_message, human_message])

        logger.debug("Generated command: %s", response.content)
        return cast(str, response.content)

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """Generate a response from a chat history."""
        logger.debug("Chat messages: %s", messages)

        # Convert messages to LangChain format
        langchain_messages: list = []

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

        logger.debug("Calling AI service with LangChain messages")
        response = self.client.invoke(langchain_messages)

        logger.debug("AI response: %s", response.content)
        return cast(str, response.content)

    def translate(self, text: str, target_language: str) -> str:
        """Translate text to a target language."""
        logger.debug("Translating text: %s to language: %s", text, target_language)

        system_message = SystemMessage(
            content=(
                "You are a translation assistant. "
                "Your task is to translate text accurately and naturally. "
                "Return ONLY the translated text without any explanation or formatting."
            )
        )
        human_message = HumanMessage(content=f"Translate the following text to {target_language}:\n{text}")

        logger.debug("Calling AI service for translation")
        response = self.client.invoke([system_message, human_message])

        logger.debug("Translated text: %s", response.content)
        return cast(str, response.content)
