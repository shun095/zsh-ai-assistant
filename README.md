# zsh-ai-assistant

A zsh plugin that integrates AI assistance directly into your shell, allowing you to:

1. **Convert comments to commands**: Type a comment starting with `#` and press Enter to have it converted to the appropriate shell command
2. **Interactive AI chat**: Use the `aiask` command to have interactive conversations with AI

## Features

### 1. Command Transformation

Type a comment describing what you want to do, and the AI will suggest the appropriate command:

```zsh
$ # List files in current directory
```

Press Enter, and it transforms to:

```zsh
$ ls -la
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
- Python 3.12 or later
- [uv](https://github.com/astral/uv) (Python package manager)

### Installing the Plugin

#### Option 1: Manual Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/shun095/zsh-ai-assistant.git ~/.zsh/zsh-ai-assistant
   ```

2. Add the plugin to your `.zshrc`:
   ```bash
   source ~/.zsh/zsh-ai-assistant/zsh-ai-assistant.plugin.zsh
   ```

#### Option 2: Using oh-my-zsh Plugin Manager

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/zsh-ai-assistant.git ~/.oh-my-zsh/custom/plugins/zsh-ai-assistant
   ```

2. Add the plugin to your `.zshrc`:

   ```bash
   # Add to your .zshrc
   plugins=(zsh-ai-assistant)
   ```

## Configuration

### Environment Variables

The plugin uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_BASE_URL` | Base URL for OpenAI-compatible API | `https://api.openai.com/v1` |
| `AI_MODEL` | AI model to use | `gpt-3.5-turbo` |
| `AI_TEMPERATURE` | Sampling temperature (0-1) | `0.7` |
| `AI_MAX_TOKENS` | Maximum tokens in response | `1000` |

### Example Configuration

Add these to your `~/.zshrc`:

```bash
export OPENAI_API_KEY="your-api-key-here"
export AI_MODEL="gpt-4"
export AI_TEMPERATURE="0.8"
```
