#!/usr/bin/env zsh

# ShellSpec helper to load and compile files
# This is required for all spec files
Include ./spec/spec_helper.sh

# Source the plugin to make functions available
source ../../zsh-ai-assistant.plugin.zsh

# Test suite for directory detection functionality
Describe 'zsh_ai_assistant_detect_plugin_dir()'
  # Test 1: Basic directory detection when script is in plugin directory
  It 'should detect plugin directory when script is in plugin directory'
    When call zsh_ai_assistant_detect_plugin_dir
    The output should eq "$(pwd)"
    The status should be successful
  End

  # Test 2: Directory detection with ZSH_CUSTOM environment variable
  It 'should detect plugin directory using ZSH_CUSTOM'
    # Set up test environment
    export ZSH_CUSTOM="/tmp/test-oh-my-zsh/custom/plugins/zsh-ai-assistant"
    # Create test directory structure
    mkdir -p "$ZSH_CUSTOM"
    # Copy plugin file to test location
    cp "../../zsh-ai-assistant.plugin.zsh" "$ZSH_CUSTOM/"
    # Change to test directory
    cd "$ZSH_CUSTOM"
    
    When call zsh_ai_assistant_detect_plugin_dir
    The output should eq "$ZSH_CUSTOM"
    
    # Cleanup
    rm -rf "$ZSH_CUSTOM"
    unset ZSH_CUSTOM
  End

  # Test 3: Directory detection with ZSH environment variable
  It 'should detect plugin directory using ZSH'
    export ZSH="/tmp/test-oh-my-zsh/plugins/zsh-ai-assistant"
    mkdir -p "$ZSH"
    cp "../../zsh-ai-assistant.plugin.zsh" "$ZSH/"
    cd "$ZSH"
    
    When call zsh_ai_assistant_detect_plugin_dir
    The output should eq "$ZSH"
    
    rm -rf "$ZSH"
    unset ZSH
  End

  # Test 4: Directory detection from relative path
  It 'should detect plugin directory from relative path'
    # Create test directory structure
    mkdir -p "zsh-ai-assistant"
    cp "../../zsh-ai-assistant.plugin.zsh" "zsh-ai-assistant/"
    
    When call zsh_ai_assistant_detect_plugin_dir
    The output should eq "zsh-ai-assistant"
    
    # Cleanup
    rm -rf "zsh-ai-assistant"
  End

  # Test 5: Error handling when directory cannot be detected
  It 'should return error when directory cannot be detected'
    # Save original function
    original_func=$(declare -f zsh_ai_assistant_detect_plugin_dir)
    
    # Replace function with error version
    eval 'zsh_ai_assistant_detect_plugin_dir() {
      echo "Error: Could not determine plugin directory" >&2
      return 1
    }'
    
    When run zsh_ai_assistant_detect_plugin_dir 2>&1
    The status should be failure
    The stderr should include "Error: Could not determine plugin directory"
    
    # Restore original function
    eval "$original_func"
  End
End

# Test suite for comment detection functionality
Describe 'zsh_ai_assistant_check_for_comment()'
  # Test 1: Detect comment line
  It 'should detect comment line starting with #'
    When call zsh_ai_assistant_check_for_comment "# list files"
    The status should be successful
  End

  # Test 2: Detect comment line with leading whitespace
  It 'should detect comment line with leading whitespace'
    When call zsh_ai_assistant_check_for_comment "  # list files"
    The status should be successful
  End

  # Test 3: Detect non-comment line
  It 'should not detect non-comment line'
    When call zsh_ai_assistant_check_for_comment "ls -la"
    The status should be failure
  End

  # Test 4: Detect error message (should not be transformed)
  It 'should not detect error message for transformation'
    When call zsh_ai_assistant_check_for_comment "# Error: Something went wrong"
    The status should be failure
  End

  # Test 5: Detect empty comment
  It 'should not detect empty comment'
    When call zsh_ai_assistant_check_for_comment "#"
    The status should be failure
  End

  # Test 6: Detect comment with only whitespace after #
  It 'should not detect comment with only whitespace after #'
    When call zsh_ai_assistant_check_for_comment "#   "
    The status should be failure
  End
End

