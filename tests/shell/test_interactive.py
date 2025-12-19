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
            self.child = pexpect.spawn("zsh -f", timeout=10, encoding="utf-8")
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
        child_spawn.sendline(f"source {script_path}")
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
        child_spawn.expect("🤖 Generating command...")
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
