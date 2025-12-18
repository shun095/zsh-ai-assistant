#!/usr/bin/env python3
import pexpect
import sys
import os
from pathlib import Path
import re


class PexpectPrefixLogger:
    _split_re = re.compile(r"(\r\n|\n|\r)")

    def __init__(self, prefix: str, stream):
        self.prefix = prefix
        self.stream = stream
        self._at_line_start = True  # 最初は行頭

    def write(self, data: str):
        if not data:
            return

        tokens = self._split_re.split(data)

        for token in tokens:
            if token in ("\n", "\r", "\r\n"):
                self.stream.write(token)
                self._at_line_start = True
                continue

            if token:
                if self._at_line_start:
                    self.stream.write(self.prefix)
                    self._at_line_start = False

                self.stream.write(token)

    def flush(self):
        if hasattr(self.stream, "flush"):
            self.stream.flush()


class TestInteractive:
    """Test cases for interface definitions."""

    child = None

    def setup_method(self):
        """Setup method to run before each test method."""
        self.child = pexpect.spawn("zsh -f", timeout=10, encoding="utf-8")
        # self.child.logfile_send = PexpectPrefixLogger("send: ", sys.stdout)
        self.child.logfile_read = PexpectPrefixLogger("read: ", sys.stdout)

        self.child.sendline('echo "=== SETUP START ==="')
        self.child.expect("%")
        self.child.sendline("PS1='%m%# '")
        self.child.expect("%")

        self.child.sendline("pwd")
        self.child.expect("%")

        # Source oh-my-zsh if it exists, otherwise just set up the plugin
        zsh_path = "/tmp/ohmyzsh/"
        ohmyzsh_sh = "oh-my-zsh.sh"

        self.child.sendline(f"export ZSH={zsh_path}")
        self.child.expect("%")
        if os.path.isfile(os.path.join(zsh_path, ohmyzsh_sh)):
            self.child.sendline(f"source {zsh_path}{ohmyzsh_sh}")
            self.child.expect("%")
        else:
            u = (
                "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/"
                "install.sh"
            )
            install_cmd = f'sh -c "$(curl -fsSL {u})"'
            self.child.sendline(f"yes | {install_cmd}")
            self.child.expect("Run zsh to try it out.")
            self.child.expect("%")
            self.child.sendline(f"source {zsh_path}{ohmyzsh_sh}")
            self.child.expect("%")

        # Set test mode for the plugin
        self.child.sendline("export ZSH_AI_ASSISTANT_TEST_MODE=1")
        self.child.expect("%")
        self.child.sendline("where zle")
        self.child.expect("%")

        script_path = (
            Path(__file__).parent.parent.parent / "zsh-ai-assistant.plugin.zsh"
        )
        script_path = script_path.resolve()
        self.child.sendline(f"source {script_path}")
        self.child.expect("%")
        self.child.sendline('echo "=== SETUP END ==="')
        self.child.expect("%")

    def teardown_method(self):
        """Teardown method to run after each test method."""
        if self.child and self.child.isalive():
            self.child.sendline("exit")
            try:
                self.child.expect(pexpect.EOF, timeout=2)
            except pexpect.TIMEOUT:
                self.child.terminate()
            self.child.close()
        self.child = None

    def test_command_generation(self):
        # コマンド変換がされること。
        self.child.send("# Simple command to list current directory files\r")
        # Wait for the command to be transformed to 'ls'
        self.child.expect("ls")
        # Send Enter to execute the command
        self.child.send("\r")
        # Wait for the command output (ls listing)
        self.child.expect("pyproject.toml", timeout=5)
        # Wait for the prompt to return
        self.child.expect("%", timeout=5)
        self.child.sendline("exit")
        self.child.expect(pexpect.EOF)

    def test_normal_command(self):
        # コマンド変換がスキップされ通常のコマンド実行ができること。
        self.child.send("echo 'hello'\r")
        self.child.expect("hello")
        self.child.sendline("exit")
        self.child.expect(pexpect.EOF)

    def test_chat(self):
        # チャットが正常に起動すること
        self.child.send("aiask\r")
        self.child.expect("Me:")
        # Send hello directly
        self.child.sendline("hello")
        self.child.expect("AI:")
        self.child.expect("Hello")
        self.child.expect("Me:")
        self.child.sendline("quit")
        self.child.expect("%")
        self.child.sendline("exit")
        self.child.expect(pexpect.EOF)

    def test_chat_multiturn(self):
        # チャットが正常に起動すること
        self.child.send("aiask\r")
        self.child.expect("Me:")
        # Send hello directly
        self.child.sendline("hello")
        self.child.expect("AI:")
        self.child.expect("Hello")
        self.child.expect("Me:")
        self.child.sendline("world")
        self.child.expect("AI:")
        self.child.expect("I received")
        self.child.expect("Me:")
        self.child.sendline("quit")
        self.child.expect("%")
        self.child.sendline("exit")
        self.child.expect(pexpect.EOF)
