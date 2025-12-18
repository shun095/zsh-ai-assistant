"""Test cases for interfaces."""

from abc import ABC
from zsh_ai_assistant.interfaces import AIServiceInterface, ChatHistoryInterface
from zsh_ai_assistant.chat_history import InMemoryChatHistory
from zsh_ai_assistant.ai_service import LangChainAIService
from zsh_ai_assistant.config import AIConfig


class TestInterfaces:
    """Test cases for interface definitions."""

    def test_aiserviceinterface_has_required_methods(self):
        """Test AIServiceInterface has required abstract methods."""
        # Check that AIServiceInterface is an abstract class
        assert issubclass(AIServiceInterface, ABC)

        # Check that it has the required abstract methods
        assert hasattr(AIServiceInterface, "generate_command")
        assert hasattr(AIServiceInterface, "chat")

        # Verify they are abstract methods by checking if they have __isabstractmethod__
        assert getattr(
            AIServiceInterface.generate_command, "__isabstractmethod__", False
        )
        assert getattr(AIServiceInterface.chat, "__isabstractmethod__", False)

    def test_chathistoryinterface_has_required_methods(self):
        """Test ChatHistoryInterface has required abstract methods."""
        # Check that ChatHistoryInterface is an abstract class
        assert issubclass(ChatHistoryInterface, ABC)

        # Check that it has the required abstract methods
        assert hasattr(ChatHistoryInterface, "add_user_message")
        assert hasattr(ChatHistoryInterface, "add_ai_message")
        assert hasattr(ChatHistoryInterface, "get_messages")
        assert hasattr(ChatHistoryInterface, "clear")

        # Verify they are abstract methods by checking if they have __isabstractmethod__
        assert getattr(
            ChatHistoryInterface.add_user_message, "__isabstractmethod__", False
        )
        assert getattr(
            ChatHistoryInterface.add_ai_message, "__isabstractmethod__", False
        )
        assert getattr(ChatHistoryInterface.get_messages, "__isabstractmethod__", False)
        assert getattr(ChatHistoryInterface.clear, "__isabstractmethod__", False)

    def test_inmemorychathistory_implements_chathistoryinterface(self):
        """Test InMemoryChatHistory implements ChatHistoryInterface."""
        # Check that InMemoryChatHistory is a subclass of ChatHistoryInterface
        assert issubclass(InMemoryChatHistory, ChatHistoryInterface)

        # Create an instance and verify all methods work
        chat_history = InMemoryChatHistory()

        # Test add_user_message
        chat_history.add_user_message("test")
        assert len(chat_history) == 1

        # Test add_ai_message
        chat_history.add_ai_message("response")
        assert len(chat_history) == 2

        # Test get_messages
        messages = chat_history.get_messages()
        assert isinstance(messages, list)
        assert len(messages) == 2

        # Test clear
        chat_history.clear()
        assert len(chat_history) == 0

    def test_langchainaiservice_implements_aiserviceinterface(self):
        """Test LangChainAIService implements AIServiceInterface."""
        # Check that LangChainAIService is a subclass of AIServiceInterface
        assert issubclass(LangChainAIService, AIServiceInterface)

        # Create an instance with valid config and verify all methods work
        import os
        from unittest.mock import Mock, patch

        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()

        with patch("zsh_ai_assistant.ai_service.ChatOpenAI") as mock_class:
            mock_instance = Mock()
            mock_instance.invoke.return_value = Mock(content="test response")
            mock_class.return_value = mock_instance

            service = LangChainAIService(config)

            # Test generate_command
            result = service.generate_command("test prompt")
            assert result == "test response"

            # Test chat
            messages = [{"role": "user", "content": "Hello"}]
            result = service.chat(messages)
            assert result == "test response"

    def test_interface_method_signatures(self):
        """Test interface methods have correct signatures."""
        # Check AIServiceInterface method signatures
        import inspect

        # generate_command should take self and a string, return a string
        sig = inspect.signature(AIServiceInterface.generate_command)
        params = list(sig.parameters.values())
        # Abstract methods include 'self' parameter
        assert len(params) == 2  # self + prompt
        assert params[1].annotation == str  # prompt parameter
        assert sig.return_annotation == str

        # chat should take self and a list of dicts, return a string
        sig = inspect.signature(AIServiceInterface.chat)
        params = list(sig.parameters.values())
        assert len(params) == 2  # self + messages
        # The annotation should be List[dict] (or List[Dict[str, Any]])
        # Check that it's a List type with dict as generic parameter
        assert hasattr(params[1].annotation, "__origin__")
        assert params[1].annotation.__origin__ == list
        assert sig.return_annotation == str

        # Check ChatHistoryInterface method signatures
        # add_user_message should take self and a string, return None
        sig = inspect.signature(ChatHistoryInterface.add_user_message)
        params = list(sig.parameters.values())
        assert len(params) == 2  # self + message
        assert params[1].annotation == str  # message parameter
        assert sig.return_annotation is None

        # add_ai_message should take self and a string, return None
        sig = inspect.signature(ChatHistoryInterface.add_ai_message)
        params = list(sig.parameters.values())
        assert len(params) == 2  # self + message
        assert params[1].annotation == str  # message parameter
        assert sig.return_annotation is None

        # get_messages should take self and return a list
        sig = inspect.signature(ChatHistoryInterface.get_messages)
        params = list(sig.parameters.values())
        assert len(params) == 1  # only self
        # The annotation should be List[dict] (or List[Dict[str, Any]])
        # Check that it's a List type with dict as generic parameter
        assert hasattr(sig.return_annotation, "__origin__")
        assert sig.return_annotation.__origin__ == list

        # clear should take self and return None
        sig = inspect.signature(ChatHistoryInterface.clear)
        params = list(sig.parameters.values())
        assert len(params) == 1  # only self
        assert sig.return_annotation is None

    def test_concrete_classes_implement_all_interface_methods(self):
        """Test concrete classes implement all interface methods."""
        # Test LangChainAIService implements AIServiceInterface
        import os
        from unittest.mock import Mock, patch

        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()

        with patch("zsh_ai_assistant.ai_service.ChatOpenAI") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance

            service = LangChainAIService(config)
            assert isinstance(service, AIServiceInterface)
            assert hasattr(LangChainAIService, "generate_command")
            assert hasattr(LangChainAIService, "chat")

        # Test InMemoryChatHistory implements ChatHistoryInterface
        assert isinstance(InMemoryChatHistory(), ChatHistoryInterface)
        assert hasattr(InMemoryChatHistory, "add_user_message")
        assert hasattr(InMemoryChatHistory, "add_ai_message")
        assert hasattr(InMemoryChatHistory, "get_messages")
        assert hasattr(InMemoryChatHistory, "clear")
