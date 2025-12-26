# shellcheck shell=sh

# Defining variables and functions here will affect all specfiles.
# Change shell options inside a function may cause different behavior,
# so it is better to set them here.
# set -eu

# Source the plugin to make functions available
# This is done at the top level so that kcov can instrument the functions
source ../../zsh-ai-assistant.plugin.zsh

# Mock uv run command to avoid actual Python execution
# This is a function-based mock that will be available in all specfiles
uv() {
  if [[ "$1" == "run" ]]; then
    if [[ "$4" == "command" ]]; then
      local comment="${@:5}"
      if [[ -z "$comment" ]] || [[ "$comment" =~ ^[[:space:]]*$ ]]; then
        echo "Error: Empty or whitespace-only comment" >&2
        return 1
      fi
      echo "ls -la"
      return 0
    elif [[ "$4" == "interactive" ]]; then
      return 0
    elif [[ "$4" == "translate" ]]; then
      local target_language="${5:-japanese}"
      local text="${6:-}"
      
      # Mock translation responses
      case "$text" in
        *"Hello"*)
          echo "こんにちは"
          return 0
          ;;
        *"How are you"*)
          echo "元気です"
          return 0
          ;;
        *)
          echo "$text"
          return 0
          ;;
      esac
    else
      return 1
    fi
  else
    return 1
  fi
}

# This callback function will be invoked only once before loading specfiles.
spec_helper_precheck() {
  # Available functions: info, warn, error, abort, setenv, unsetenv
  # Available variables: VERSION, SHELL_TYPE, SHELLSPEC_VERSION
  : minimum_version "0.28.1"
}

# This callback function will be invoked after a specfile has been loaded.
spec_helper_loaded() {
  :
}

# Helper function to set up animation mocks
# This should be called in before_all hooks in test files that need animation mocks
setup_animation_mocks() {
  function zsh_ai_assistant_background_animation() {
    echo "⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏"
  }

  function zsh_ai_assistant_show_loading() {
    zsh_ai_assistant_animation_pid="12345"
  }

  function zsh_ai_assistant_hide_loading() {
    zsh_ai_assistant_animation_pid=""
  }
}

# This callback function will be invoked after core modules has been loaded.
spec_helper_configure() {
  # Available functions: import, before_each, after_each, before_all, after_all
  : import 'support/custom_matcher'
}
