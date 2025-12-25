#!/usr/bin/env zsh

# ShellSpec helper to load and compile files
Include ./spec/spec_helper.sh

# Test suite for chat functionality
Describe 'zsh_ai_assistant_chat()'
  # Test 1: Chat function should execute without errors
  It 'should execute chat function without errors'
    # Chat function should not fail
    When run zsh_ai_assistant_chat
    
    The status should be successful
  End

  # Test 2: Chat function should handle plugin directory error
  It 'should handle plugin directory error gracefully'
    # Save original ZSH_AI_ASSISTANT_DIR
    original_dir="$ZSH_AI_ASSISTANT_DIR"
    
    # Set ZSH_AI_ASSISTANT_DIR to non-existent directory
    export ZSH_AI_ASSISTANT_DIR="/nonexistent/directory"
    
    When run zsh_ai_assistant_chat 2>&1
    The stderr should include "Error: Could not change to plugin directory"
    The status should be failure
    
    # Restore original ZSH_AI_ASSISTANT_DIR
    export ZSH_AI_ASSISTANT_DIR="$original_dir"
  End
End

# Test suite for aiask command
Describe 'aiask()'
  # Test 1: aiask command should execute chat
  It 'should execute chat when called'
    # aiask should call zsh_ai_assistant_chat
    When run aiask
    
    The status should be successful
  End
End
