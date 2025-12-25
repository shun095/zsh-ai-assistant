#!/usr/bin/env zsh

# ShellSpec helper to load and compile files
Include ./spec/spec_helper.sh





# Test suite for command generation functionality
Describe 'zsh_ai_assistant_generate_command()'
  # Test 1: Generate command with valid comment
  It 'should generate command from valid comment'
    When call zsh_ai_assistant_generate_command "list files in current directory"
    The output should eq "ls -la"
    The status should be successful
  End

  # Test 2: Handle empty comment
  It 'should handle empty comment gracefully'
    When run zsh_ai_assistant_generate_command ""
    The status should be failure
    The output should include "Error: Empty or whitespace-only comment"
  End

  # Test 3: Handle comment with only whitespace
  It 'should handle whitespace-only comment gracefully'
    When run zsh_ai_assistant_generate_command "   "
    The status should be failure
    The output should include "Error: Empty or whitespace-only comment"
  End

  # Test 4: Error handling when plugin directory cannot be accessed
  It 'should handle plugin directory access error'
    # Save original ZSH_AI_ASSISTANT_DIR
    original_dir="$ZSH_AI_ASSISTANT_DIR"
    
    # Set ZSH_AI_ASSISTANT_DIR to non-existent directory
    export ZSH_AI_ASSISTANT_DIR="/nonexistent/directory"
    
    When run zsh_ai_assistant_generate_command "test" 2>&1
    The stderr should include "Error: Could not change to plugin directory"
    The status should be failure
    
    # Restore original ZSH_AI_ASSISTANT_DIR
    export ZSH_AI_ASSISTANT_DIR="$original_dir"
  End
End

# Test suite for command transformation functionality
Describe 'zsh_ai_assistant_transform_command()'
  # Test 1: Transform command with valid input
  It 'should transform command and update BUFFER'
    # Set a test BUFFER
    BUFFER="# list files"
    
    # Call transform command
    When run zsh_ai_assistant_transform_command "# list files"
    
    # Should succeed
    The status should be successful
  End

  # Test 2: Transform command with empty input
  It 'should handle empty input gracefully'
    BUFFER=""
    
    When run zsh_ai_assistant_transform_command ""
    
    The status should be successful
  End

  # Test 3: Transform command with non-comment input
  It 'should handle non-comment input gracefully'
    BUFFER="ls -la"
    
    When run zsh_ai_assistant_transform_command "ls -la"
    
    The status should be successful
  End
End
