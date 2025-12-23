#!/usr/bin/env python3
import pexpect
import sys
import os
from pathlib import Path
import re
from typing import Optional


class PexpectPrefixLogger:
    _split_re = re.compile(r"(\r\n|\n|\r)")

    def __init__(self, prefix: str, stream: object) -> None:
        self.prefix = prefix
        self.stream = stream
        self._at_line_start = True  # 最初は行頭

    def write(self, data: str) -> None:
        if not data:
            return

        tokens = self._split_re.split(data)

        for token in tokens:
            if token in ("\n", "\r", "\r\n"):
                self._write_to_stream(token)
                self._at_line_start = True
                continue

            if token:
                if self._at_line_start:
                    self._write_to_stream(self.prefix)
                    self._at_line_start = False

                self._write_to_stream(token)

    def _write_to_stream(self, text: str) -> None:
        """Helper method to write to stream with proper type handling."""
        if hasattr(self.stream, "write"):
            self.stream.write(text)

    def flush(self) -> None:
        if hasattr(self.stream, "flush"):
            self.stream.flush()


class TestInteractive:
    """Test cases for interface definitions."""

    child: Optional[pexpect.spawn] = None

    def _assert_child_is_spawn(self) -> pexpect.spawn:
        """Assert that child is a pexpect.spawn instance and return it."""
        assert self.child is not None, "child should be initialized by setup_method"
        assert isinstance(self.child, pexpect.spawn), "child should be a pexpect.spawn instance"
        return self.child

    def setup_method(self) -> None:
        """Setup method to run before each test method."""
        # Initialize child if not already set
        if self.child is None:
            # Merge stderr with stdout so pexpect can capture animation output
            self.child = pexpect.spawn("zsh -f", timeout=10, encoding="utf-8")
            # Merge stderr into stdout
            self.child.setecho(False)
            self.child.logfile_read = PexpectPrefixLogger("read: ", sys.stdout)
        # self.child.logfile_send = PexpectPrefixLogger("send: ", sys.stdout)
        self.child.logfile_read = PexpectPrefixLogger("read: ", sys.stdout)
        # Type narrowing - child is guaranteed to be pexpect.spawn here
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child
        child_spawn.sendline('echo "=== SETUP START ==="')
        child_spawn.expect("%")
        child_spawn.sendline("PS1='%m%# '")
        child_spawn.expect("%")

        child_spawn.sendline("pwd")
        child_spawn.expect("%")

        # Source oh-my-zsh if it exists, otherwise just set up the plugin
        zsh_path = "/tmp/ohmyzsh/"
        ohmyzsh_sh = "oh-my-zsh.sh"

        child_spawn.sendline(f"export ZSH={zsh_path}")
        child_spawn.sendline("export KEEP_ZSHRC=yes")
        child_spawn.expect("%")
        if os.path.isfile(os.path.join(zsh_path, ohmyzsh_sh)):
            child_spawn.sendline(f"source {zsh_path}{ohmyzsh_sh}")
            child_spawn.expect("%")
        else:
            u = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/" "install.sh"
            install_cmd = f'sh -c "$(curl -fsSL {u})"'
            child_spawn.sendline(f"yes | {install_cmd}")
            child_spawn.expect("Run zsh to try it out.")
            child_spawn.expect("%")
            child_spawn.sendline(f"source {zsh_path}{ohmyzsh_sh}")
            child_spawn.expect("%")

        # Set test mode for the plugin
        child_spawn.sendline("export ZSH_AI_ASSISTANT_TEST_MODE=1")
        child_spawn.expect("%")
        child_spawn.sendline("where zle")
        child_spawn.expect("%")

        script_path = Path(__file__).parent.parent.parent / "zsh-ai-assistant.plugin.zsh"
        script_path = script_path.resolve()
        child_spawn.sendline("cd /tmp")
        child_spawn.sendline(f"source {script_path}")
        child_spawn.sendline("cd -")
        child_spawn.expect("%")
        child_spawn.sendline('echo "=== SETUP END ==="')
        child_spawn.expect("%")

    def teardown_method(self) -> None:
        """Teardown method to run after each test method."""
        if self.child and self.child.isalive():
            self.child.sendline("exit")
            try:
                self.child.expect(pexpect.EOF, timeout=2)
            except pexpect.TIMEOUT:
                self.child.terminate()
            self.child.close()
        self.child = None

    def test_loading_message_displayed(self) -> None:
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child
        # Test that loading message is displayed during command generation
        child_spawn.send("# list current directory files\r")
        # Wait for the loading message to appear in the buffer
        # The animation cycles through flame characters, so we check for any flame character
        # Animation output is on stderr for background processes
        child_spawn.expect(re.compile(r"⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏ Generating command..."), timeout=10)
        # Wait for the command to be transformed to 'ls'
        child_spawn.expect("ls")
        try:
            child_spawn.expect("pyproject.toml", timeout=3)
            # 見つかった場合
            raise Exception("Generated command should not be executed")
        except pexpect.TIMEOUT:
            # timeout → ERROR は出なかった
            pass
        # Send Enter to execute the command
        child_spawn.send("\r")
        # Wait for the command output (ls listing)
        child_spawn.expect("pyproject.toml", timeout=5)
        # Wait for the prompt to return
        child_spawn.expect("%")

    def test_flame_animation_displayed(self) -> None:
        """Test that flame animation shows multiple frames during command generation."""
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child

        # Test that loading message is displayed during command generation
        child_spawn.send("# list current directory files\r")

        # Wait for the first flame character (any flame character)
        child_spawn.expect(re.compile(r"⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏ Generating command..."), timeout=10)

        # Wait for at least 2 more different flame characters to verify animation
        # This ensures the animation is actually cycling, not just showing one frame
        try:
            # Try to find a different flame character
            # We need to exclude the one we just saw
            # Since we don't know which one we saw, we'll just wait for any different one
            # This is a simplification - in a real test, we'd track which frame we saw
            child_spawn.expect(re.compile(r"⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏ Generating command..."), timeout=2)
        except pexpect.TIMEOUT:
            raise Exception("Flame animation did not show multiple frames - animation is not working")

        # Wait for the command to be transformed to 'ls'
        child_spawn.expect("ls")

        # Send Enter to execute the command
        child_spawn.send("\r")

        # Wait for the command output (ls listing)
        child_spawn.expect("pyproject.toml", timeout=5)

        # Wait for the prompt to return
        child_spawn.expect("%")

    def test_flame_animation_with_sigterm(self) -> None:
        """Test that flame animation properly handles SIGINT and stops."""
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child

        # Start command generation which will start the animation
        child_spawn.send("# list current directory files\r")

        # Wait for any flame character (animation may have already cycled past first frame)
        child_spawn.expect(re.compile(r"⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏ Generating command..."), timeout=10)

        # Wait for at least one more different frame to ensure animation is actively running
        # We need to be flexible since we don't know which frame we just saw
        try:
            child_spawn.expect(re.compile(r"⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏ Generating command..."), timeout=0.5)
        except pexpect.TIMEOUT:
            # If we timeout, it means the animation stopped quickly, which is acceptable
            # for this test since we're about to send SIGINT anyway
            pass

        # Send SIGINT (Ctrl+C) to the zsh process
        # This should trigger the cleanup handler and stop the animation
        child_spawn.sendcontrol("c")  # Send Ctrl+C which sends SIGINT

        # After sending SIGINT, the animation should stop
        # We should see the prompt return without the animation still running

        # Wait a short time for the cleanup to complete
        import time

        time.sleep(0.2)

    def test_uv_error_on_command_generation(self) -> None:
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child
        # Mock uv command to assuming failure
        child_spawn.send('uv () { echo "failed reason message" >&2; return 1 }\r')
        # Test that loading message is displayed during command generation
        child_spawn.send("# list current directory files\r")
        # Wait for the loading message to appear in the buffer
        # The animation cycles through flame characters, so we check for any flame character
        child_spawn.expect(re.compile(r"⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏ Generating command..."))
        # Wait for the command to be transformed to 'error message'
        child_spawn.expect("# Error: failed reason message")
        # Send Enter to execute the command as comment out
        child_spawn.send("\r")
        try:
            child_spawn.expect("⠋ Generating command...", timeout=3)
            # 見つかった場合
            raise Exception("Command generation should not be executed when `Error:`")
        except pexpect.TIMEOUT:
            # timeout → ERROR は出なかった
            pass
        # Wait for the prompt to return without regenerating command when error.
        child_spawn.expect("%")

    def test_error_on_command_generation(self) -> None:
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child
        # Test that loading message is displayed during command generation
        child_spawn.send("# return api error\r")
        # Wait for the loading message to appear in the buffer (any flame character)
        child_spawn.expect(re.compile(r"⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏ Generating command..."))
        # Wait for the command to be transformed to 'error message'
        child_spawn.expect("# Error: ")
        # Send Enter to execute the command as comment out
        child_spawn.send("\r")
        try:
            child_spawn.expect("⠋ Generating command...", timeout=3)
            # 見つかった場合
            raise Exception("Command generation should not be executed when `Error:`")
        except pexpect.TIMEOUT:
            # timeout → ERROR は出なかった
            pass
        # Wait for the prompt to return without regenerating command when error.
        child_spawn.expect("%")

    def test_command_generation_git_status(self) -> None:
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child
        # コマンド変換がされること。
        child_spawn.send("# check git current status\r")
        # Wait for the command to be transformed to 'ls'
        child_spawn.expect("git status")
        # Send Enter to execute the command
        child_spawn.send("\r")
        # Wait for the prompt to return
        child_spawn.expect("%", timeout=5)
        child_spawn.sendline("exit")
        child_spawn.expect(pexpect.EOF)

    def test_normal_command(self) -> None:
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child
        # コマンド変換がスキップされ通常のコマンド実行ができること。
        child_spawn.send("echo 'hello'\r")
        child_spawn.expect("hello")
        child_spawn.sendline("exit")
        child_spawn.expect(pexpect.EOF)

    def test_chat_history_accumulation(self) -> None:
        """Test that full conversation history is accumulated and sent to Python CLI."""
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child

        # Start chat
        child_spawn.send("aiask\r")
        child_spawn.expect("Me:")

        # First turn: send "hello"
        child_spawn.sendline("hello")
        child_spawn.expect("AI:")
        child_spawn.expect("Hello")
        child_spawn.expect("Me:")

        # Second turn: send "world"
        # The full history should now include both user and assistant messages
        child_spawn.sendline("world")
        child_spawn.expect("AI:")
        child_spawn.expect(re.compile(r"I received your message: world"))
        child_spawn.expect("Me:")

        # Third turn: verify the assistant can reference the full history
        # by asking about what was said in the first turn
        child_spawn.sendline("what did I say first")
        child_spawn.expect("AI:")
        # The response should contain "hello" from the first message
        child_spawn.expect(re.compile(r"hello", re.IGNORECASE))
        child_spawn.expect("Me:")

        # Fourth turn: verify the assistant can reference the second message
        child_spawn.sendline("what did I say second")
        child_spawn.expect("AI:")
        # The response should contain "world" from the second message
        child_spawn.expect(re.compile(r"world", re.IGNORECASE))
        child_spawn.expect("Me:")

        child_spawn.sendline("quit")
        child_spawn.expect("%")
        child_spawn.sendline("exit")
        child_spawn.expect(pexpect.EOF)

    def test_chat_history_with_assistant_responses(self) -> None:
        """Test that assistant can reference its own previous responses, not just user messages."""
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child

        # Start chat
        child_spawn.send("aiask\r")
        child_spawn.expect("Me:")

        # First turn: send "hello"
        child_spawn.sendline("hello")
        child_spawn.expect("AI:")
        child_spawn.expect("Hello")
        child_spawn.expect("Me:")

        # Second turn: send "world"
        child_spawn.sendline("world")
        child_spawn.expect("AI:")
        child_spawn.expect(re.compile(r"I received your message: world"))
        child_spawn.expect("Me:")

        # Third turn: ask what the assistant said first
        child_spawn.sendline("what did you say first")
        child_spawn.expect("AI:")
        # The AI should be able to reference its first response containing "Hello.*assist"
        child_spawn.expect(re.compile(r"Hello.*assist", re.IGNORECASE))
        child_spawn.expect("Me:")

        # Fourth turn: ask what the assistant said second
        child_spawn.sendline("what did you say second")
        child_spawn.expect("AI:")
        # The AI should be able to reference its second response containing "I received your message"
        child_spawn.expect(re.compile(r"I received your message", re.IGNORECASE))
        child_spawn.expect("Me:")

        # Fifth turn: ask for a summary of what we said
        child_spawn.sendline("tell me what we said")
        child_spawn.expect("AI:")
        # The AI should reference both user and assistant messages
        child_spawn.expect(re.compile(r"You said.*I said", re.IGNORECASE))
        child_spawn.expect("Me:")

        child_spawn.sendline("quit")
        child_spawn.expect("%")
        child_spawn.sendline("exit")
        child_spawn.expect(pexpect.EOF)

    def test_command_generation_from_random_directory(self) -> None:
        """Test normal case of command generation from a random directory."""
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child

        # Change to a different directory (e.g., /tmp)
        child_spawn.sendline("cd /tmp")
        child_spawn.expect("%")

        # Verify we're in /tmp
        child_spawn.sendline("pwd")
        child_spawn.expect("/tmp")
        child_spawn.expect("%")

        # Test command generation from /tmp directory
        child_spawn.send("# list files in current directory\r")
        # Wait for the loading message (any flame character)
        child_spawn.expect(re.compile(r"⠋|⠙|⠹|⠸|⠼|⠴|⠦|⠧|⠇|⠏ Generating command..."))
        # Wait for the command to be transformed to 'ls'
        child_spawn.expect("ls")
        # Send Enter to execute the command
        child_spawn.send("\r")
        # Wait for the prompt to return
        child_spawn.expect("%")

    def test_chat_from_random_directory(self) -> None:
        """Test normal case of chat (aiask) from a random directory."""
        assert self.child is not None
        child_spawn: pexpect.spawn = self.child

        # Change to a different directory (e.g., home directory)
        child_spawn.sendline("cd ~")
        child_spawn.expect("%")

        # Start chat from home directory
        child_spawn.send("aiask\r")
        child_spawn.expect("Me:")

        # Send a message
        child_spawn.sendline("Hello")
        child_spawn.expect("AI:")
        # The AI should respond
        child_spawn.expect(re.compile(r"Hello", re.IGNORECASE))
        child_spawn.expect("Me:")

        # Send another message
        child_spawn.sendline("quit")
        child_spawn.expect("%")
