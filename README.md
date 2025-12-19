# zsh-ai-assistant

A zsh plugin that integrates AI assistance directly into your shell, allowing you to:

1. **Convert comments to commands**: Type a comment starting with `#` and press Enter to have it converted to the appropriate shell command
2. **Interactive AI chat**: Use the `aiask` command to have interactive conversations with AI

## Features

### 1. Command Transformation

Type a comment describing what you want to do, and the AI will suggest the appropriate command:

```zsh
# List files in current directory
```

Press Enter, and it transforms to:

```zsh
ls -la
```

### 2. Interactive AI Chat

Use the `aiask` command to start an interactive chat session:

```zsh
$ aiask
Me: Where is the capital of France?
AI: The capital of France is Paris. It's located in the northern part of the country and is known for its historical landmarks such as the Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral.
Me: 
```

## Installation

### Prerequisites

- zsh 5.9 or later
- Python 3.10 or later
- [uv](https://github.com/astral/uv) (Python package manager)

### Installing the Plugin

#### Option 1: Manual Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/zsh-ai-assistant.git ~/.oh-my-zsh/custom/plugins/zsh-ai-assistant
   ```

2. Add the plugin to your `.zshrc`:
   ```bash
   plugins=(zsh-ai-assistant)
   ```

3. Set up the Python environment:
   ```bash
   cd ~/.oh-my-zsh/custom/plugins/zsh-ai-assistant
   uv venv
   eval "$(uv venv shell)"
   uv sync --all-extras
   ```

#### Option 2: Using oh-my-zsh Plugin Manager

If available in the oh-my-zsh plugin repository:

```bash
# Add to your .zshrc
plugins=(zsh-ai-assistant)
```

Then manually set up the Python environment as shown above.

## Configuration

### Environment Variables

The plugin uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_BASE_URL` | Base URL for OpenAI-compatible API | `https://api.openai.com/v1` |
| `ZSH_AI_ASSISTANT_MODEL` | AI model to use | `gpt-3.5-turbo` |
| `ZSH_AI_ASSISTANT_TEMPERATURE` | Sampling temperature (0-1) | `0.7` |
| `ZSH_AI_ASSISTANT_MAX_TOKENS` | Maximum tokens in response | `1000` |

### Example Configuration

Add these to your `~/.zshrc`:

```bash
export OPENAI_API_KEY="your-api-key-here"
export ZSH_AI_ASSISTANT_MODEL="gpt-4"
export ZSH_AI_ASSISTANT_TEMPERATURE="0.8"
```

## Usage

### Command Transformation

Simply type a comment starting with `#` and press Enter:

```zsh
# Show disk usage
# Find large files in home directory
# Check network connections
```

The plugin will transform these into appropriate shell commands.

### Interactive Chat

Start an interactive chat session:

```zsh
$ aiask
Me: What is the capital of Japan?
AI: The capital of Japan is Tokyo.
Me: How many people live there?
AI: As of recent estimates, Tokyo has a population of approximately 14 million people in the city proper, and around 37 million in the greater Tokyo metropolitan area.
Me: quit
```

## Development

### Project Structure

```
zsh-ai-assistant/
├── .venv/                  # Python virtual environment
├── src/
│   └── zsh_ai_assistant/   # Python backend
│       ├── __init__.py
│       ├── ai_service.py   # AI service implementation
│       ├── chat_history.py # Chat history management
│       ├── cli.py          # CLI interface
│       ├── config.py       # Configuration
│       └── interfaces.py   # Interfaces and abstractions
├── tests/
│   ├── python/            # Python unit tests
│   └── shell/             # Shell integration tests
├── zsh-ai-assistant.plugin.zsh # Main zsh plugin
├── pyproject.toml         # Python project configuration
└── README.md              # This file
```

### Setting Up Development Environment

```bash
# Clone the repository
cd /path/to/zsh-ai-assistant

# Create virtual environment
uv venv

# Activate it
eval "$(uv venv shell)"

# Install dependencies
uv sync --all-extras
```

### Running Tests

```bash
# Run all Python tests with coverage
eval "$(uv venv shell)"
uv run pytest -v --cov=src --cov-report=html

# View coverage report
xdg-open htmlcov/index.html
```

### Code Quality

The project follows:
- **SOLID principles** for maintainable, testable code
- **TDD methodology** (Test-Driven Development)
- **Python type hints** for better code clarity
- **Black** for code formatting
- **Flake8** for linting
- **mypy** for static type checking

Run quality checks:
```bash
uv run black --check src tests
uv run flake8 src tests
uv run mypy src tests
```

## Architecture

### Design Principles

The plugin follows the SOLID principles:

1. **Single Responsibility Principle**: Each module has one clear responsibility
2. **Open/Closed Principle**: Modules are open for extension but closed for modification
3. **Liskov Substitution Principle**: Interfaces can be substituted by their implementations
4. **Interface Segregation Principle**: Clients don't depend on interfaces they don't use
5. **Dependency Inversion Principle**: High-level modules depend on abstractions

### Key Components

#### 1. Interfaces (`interfaces.py`)

Defines abstract base classes for:
- `AIServiceInterface`: Interface for AI services
- `ChatHistoryInterface`: Interface for chat history management

#### 2. Configuration (`config.py`)

Handles environment variable loading and validation.

#### 3. AI Service (`ai_service.py`)

Implements the LangChain-based AI service that:
- Connects to OpenAI-compatible APIs
- Generates commands from natural language
- Provides chat responses

#### 4. Chat History (`chat_history.py`)

Manages conversation history for context-aware responses.

#### 5. CLI (`cli.py`)

Command-line interface that bridges zsh and Python:
- Parses commands from zsh
- Returns AI responses
- Manages chat sessions

#### 6. Plugin (`zsh-ai-assistant.plugin.zsh`)

The zsh frontend that:
- Detects comments starting with `#`
- Calls the Python backend
- Transforms prompts
- Provides the `aiask` command

## Testing

### Test Coverage

The project maintains **90%+ test coverage** for both Python and shell components.

### Test Structure

```
tests/
├── python/
│   ├── test_ai_service.py
│   ├── test_chat_history.py
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_interfaces.py
└── shell/
    └── test_interactive.py
```

### Writing Tests

Follow the TDD workflow:

1. **Step 1**: Add test to the test list
2. **Step 2**: Write one failing test
3. **Step 3**: Make the test pass
4. **Step 4**: Refactor if needed
5. **Step 5**: Repeat until all tests pass

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create your branch
2. **Write tests** for new features
3. **Ensure all tests pass**
4. **Follow the coding style** (Black, Flake8, mypy)
5. **Update documentation** if needed
6. **Submit a pull request**

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/yourusername/zsh-ai-assistant).

## Acknowledgements

- [oh-my-zsh](https://ohmyz.sh/) - The popular zsh framework
- [LangChain](https://www.langchain.com/) - AI application development framework
- [OpenAI](https://openai.com/) - AI models and API
- [uv](https://github.com/astral/uv) - Fast Python package manager

