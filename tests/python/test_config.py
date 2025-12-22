"""Test cases for AIConfig."""

import os
from zsh_ai_assistant.config import AIConfig


class TestAIConfig:
    """Test cases for AIConfig class."""

    def test_valid_configuration_with_all_required_fields(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test valid configuration with all required fields."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()

        assert config.is_valid is True
        assert config.api_key == "test-api-key"
        assert config.base_url == "https://api.example.com"
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000

    def test_valid_configuration_with_custom_settings(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test valid configuration with custom settings."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"
        os.environ["AI_MODEL"] = "gpt-4"
        os.environ["AI_TEMPERATURE"] = "0.9"
        os.environ["AI_MAX_TOKENS"] = "2000"

        config = AIConfig()

        assert config.is_valid is True
        assert config.model == "gpt-4"
        assert config.temperature == 0.9
        assert config.max_tokens == 2000

    def test_invalid_configuration_without_api_key(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test invalid configuration without API key."""
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()

        assert config.is_valid is False

    def test_invalid_configuration_without_base_url(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test invalid configuration without base URL."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        # Note: base_url has a default value, so this is actually valid
        # This test is kept for documentation purposes

        config = AIConfig()

        # Since base_url has a default, this is actually valid
        assert config.is_valid is True
        assert config.base_url == "https://api.openai.com/v1"

    def test_invalid_configuration_without_both_api_key_and_base_url(  # type: ignore[no-untyped-def]
        self, reset_env
    ) -> None:
        """Test invalid config without both API key and base URL."""
        config = AIConfig()

        assert config.is_valid is False

    def test_string_representation_of_configuration(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test string representation of configuration."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()

        assert "AIConfig" in str(config)
        assert "base_url='https://api.example.com'" in str(config)
        assert "model='gpt-3.5-turbo'" in str(config)

    def test_default_base_url(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test default base URL when not specified."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"

        config = AIConfig()

        assert config.base_url == "https://api.openai.com/v1"

    def test_default_model(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test default model when not specified."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()

        assert config.model == "gpt-3.5-turbo"

    def test_default_temperature(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test default temperature when not specified."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()

        assert config.temperature == 0.7

    def test_default_max_tokens(self, reset_env) -> None:  # type: ignore[no-untyped-def]
        """Test default max_tokens when not specified."""
        os.environ["OPENAI_API_KEY"] = "test-api-key"
        os.environ["OPENAI_BASE_URL"] = "https://api.example.com"

        config = AIConfig()

        assert config.max_tokens == 1000


