#!/usr/bin/env zsh

# ShellSpec helper to load and compile files
Include ./spec/spec_helper.sh

# Test suite for translation functionality
Describe 'aitrans()'
  Describe "Translation functionality"
    It "should translate text from stdin"
      # Test with argument
      When call aitrans "Hello world"
      The output should include "こんにちは"
    End

    It "should handle multiline input from stdin"
      # Test with argument containing newlines
      When call aitrans $'Hello\nHow are you?'
      The output should include "こんにちは"
    End

    It "should handle empty input"
      # Test with empty argument - should now succeed and pass to Python CLI
      When call aitrans ""
      The status should be success
      The output should eq ""
    End

    It "should translate text from stdin using Data helper"
      # Test with stdin using Data helper
      Data
        #|Hello world
      End
      When run aitrans
      The output should include "こんにちは"
    End

    It "should handle multiline input from stdin using Data helper"
      # Test with multiline stdin using Data helper
      Data
        #|Hello
        #|How are you?
      End
      When run aitrans
      The output should include "こんにちは"
    End

    It "should handle directory change error"
      # Save original ZSH_AI_ASSISTANT_DIR
      original_dir="$ZSH_AI_ASSISTANT_DIR"
      
      # Set ZSH_AI_ASSISTANT_DIR to non-existent directory
      export ZSH_AI_ASSISTANT_DIR="/nonexistent/directory"
      
      When run aitrans "Hello" 2>&1
      The stderr should include "Error: Could not change to plugin directory"
      The status should be failure
      
      # Restore original ZSH_AI_ASSISTANT_DIR
      export ZSH_AI_ASSISTANT_DIR="$original_dir"
    End

  End
End
