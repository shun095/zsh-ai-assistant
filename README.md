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

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/yourusername/zsh-ai-assistant).

## Acknowledgements

- [oh-my-zsh](https://ohmyz.sh/) - The popular zsh framework
- [LangChain](https://www.langchain.com/) - AI application development framework
- [OpenAI](https://openai.com/) - AI models and API
- [uv](https://github.com/astral/uv) - Fast Python package manager

