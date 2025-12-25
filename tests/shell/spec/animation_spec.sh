#!/usr/bin/env zsh

# ShellSpec helper to load and compile files
Include ./spec/spec_helper.sh

# Set up animation mocks using BeforeAll hook
# This allows kcov to instrument the original functions first
BeforeAll 'setup_animation_mocks'

# Test suite for loading animation functionality
Describe 'zsh_ai_assistant_background_animation()'
  # Test 1: Animation function should run without errors
  It 'should run animation function without errors'
    When call zsh_ai_assistant_background_animation
    The output should include "⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏"
    The status should be successful
  End
End

# Test suite for show/hide loading functions
Describe 'zsh_ai_assistant_show_loading()'
  It 'should show loading animation'
    # Save original animation pid
    original_pid="${zsh_ai_assistant_animation_pid:-}"
    
    # Show loading
    zsh_ai_assistant_show_loading
    
    # Check that animation pid is set
    The variable zsh_ai_assistant_animation_pid should eq "12345"
    
    # Hide loading
    zsh_ai_assistant_hide_loading
    
    # Check that animation pid is cleared
    The variable zsh_ai_assistant_animation_pid should eq ""
    
    # Restore original
    zsh_ai_assistant_animation_pid="$original_pid"
  End
End

Describe 'zsh_ai_assistant_hide_loading()'
  It 'should hide loading animation and clean up'
    # Set a fake pid
    zsh_ai_assistant_animation_pid="12345"
    
    # Hide loading
    When call zsh_ai_assistant_hide_loading
    
    # Check that animation pid is cleared
    The variable zsh_ai_assistant_animation_pid should eq ""
    
    # Check that trap is cleared
    The status should be successful
  End

  It 'should handle missing animation pid gracefully'
    # Clear animation pid
    zsh_ai_assistant_animation_pid=""
    
    # Hide loading should not fail
    When call zsh_ai_assistant_hide_loading
    
    The status should be successful
  End
End
