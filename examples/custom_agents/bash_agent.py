import subprocess
import shlex
import os
import logging
from typing import Dict, Any, Optional, List, Set, Tuple, Union
from pathlib import Path
from omnicoreagent import OmniAgent, ToolRegistry, MemoryRouter, EventRouter
import sys
import asyncio
import signal
import re


# Setup logging
logging.basicConfig(
    filename="copilot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
# Try to import rich for enhanced UX
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


logger = logging.getLogger(__name__)


class Bash:
    """
    Production-ready secure Bash agent for DevOps tasks, supporting a comprehensive set of safe commands
    for file operations, system monitoring, container management, Kubernetes, log analysis, and more.
    Features:
    - Quote-aware parsing (handles nested quotes, escapes)
    - Extensive allowed command set with validation
    - Robust error handling and logging
    - Command history tracking
    - Input validation and sanitization
    """

    ALLOWED_COMMANDS: Set[str] = {
        # File inspection and navigation
        "ls",
        "pwd",
        "cat",
        "head",
        "tail",
        "more",
        "less",
        "tree",
        "file",
        "stat",
        "readlink",
        "realpath",
        "basename",
        "dirname",
        # File search and pattern matching
        "find",
        "grep",
        "egrep",
        "fgrep",
        "locate",
        "which",
        "whereis",
        "type",
        "command",
        # Text processing
        "awk",
        "sed",
        "cut",
        "tr",
        "sort",
        "uniq",
        "wc",
        "fold",
        "fmt",
        "column",
        "expand",
        "unexpand",
        "join",
        "paste",
        "split",
        "csplit",
        "nl",
        "pr",
        "tac",
        "rev",
        # File comparison
        "diff",
        "cmp",
        "comm",
        "diff3",
        "sdiff",
        # Compression/Archive inspection (read-only)
        "tar",
        "zip",
        "unzip",
        "gzip",
        "gunzip",
        "bzip2",
        "bunzip2",
        "xz",
        "unxz",
        "zcat",
        "bzcat",
        "xzcat",
        # Checksums and hashing
        "md5sum",
        "sha1sum",
        "sha224sum",
        "sha256sum",
        "sha384sum",
        "sha512sum",
        "cksum",
        "sum",
        "b2sum",
        # Safe file operations
        "touch",
        "mkdir",
        "cp",
        "mv",
        "echo",
        "printf",
        "tee",
        # System information
        "date",
        "cal",
        "uptime",
        "whoami",
        "id",
        "groups",
        "users",
        "hostname",
        "hostid",
        "uname",
        "arch",
        "lscpu",
        "lsblk",
        "df",
        "du",
        "free",
        "vmstat",
        "iostat",
        "mpstat",
        "numastat",
        "lscpu",
        "lsmem",
        "lsblk",
        "blkid",
        # Process inspection
        "ps",
        "pgrep",
        "pidof",
        "pstree",
        "top",
        "htop",
        "jobs",
        # Network inspection
        "ping",
        "traceroute",
        "netstat",
        "ss",
        "ip",
        "ifconfig",
        "hostname",
        "host",
        "nslookup",
        "dig",
        "whois",
        "curl",
        "wget",
        "arp",
        "route",
        "nstat",
        # Environment
        "env",
        "printenv",
        "set",
        "export",
        "alias",
        "unalias",
        # Conditionals and testing
        "test",
        "[",
        "[[",
        "expr",
        "true",
        "false",
        # Utilities
        "seq",
        "yes",
        "sleep",
        "timeout",
        "wait",
        "watch",
        "bc",
        "dc",
        "factor",
        "jot",
        "shuf",
        "od",
        "hexdump",
        "xxd",
        "strings",
        "iconv",
        "base64",
        "base32",
        "uuencode",
        "uudecode",
        # JSON/Data processing
        "jq",
        "yq",
        "xmllint",
        "xsltproc",
        # Version control (read-only operations)
        "git",
        # Container management (read-only or safe operations)
        "docker",
        # Kubernetes (read-only or safe operations)
        "kubectl",
        # Log analysis and monitoring
        "journalctl",
        "dmesg",
        "loginctl",
        "last",
        "lastb",
        "lastlog",
        # System resource monitoring
        "sar",
        "iotop",
        "nmon",
        "glances",
        # File system checks
        "fsck",
        "badblocks",
        "duf",
        "ncdu",
        # Package inspection (read-only)
        "dpkg",
        "rpm",
        "yum",
        "dnf",
    }

    SHELL_RESERVED_WORDS: Set[str] = {
        # Control structures
        "if",
        "then",
        "else",
        "elif",
        "fi",
        "case",
        "esac",
        "in",
        "for",
        "while",
        "until",
        "do",
        "done",
        "select",
        # Functions
        "function",
        # Grouping
        "{",
        "}",
        "(",
        ")",
        # Logical
        "!",
        "[[",
        "]]",
        # Time
        "time",
        "coproc",
        # Built-in commands (safe ones)
        ".",
        "source",
        ":",
        "true",
        "false",
        "break",
        "continue",
        "return",
        "declare",
        "typeset",
        "local",
        "readonly",
        "shift",
        "getopts",
        "read",
        "mapfile",
        "readarray",
        "let",
        "eval",
        "exec",
        "command",
        "builtin",
        "enable",
        "help",
        "hash",
        "type",
        "cd",
        "pushd",
        "popd",
        "dirs",
        "pwd",
        "exit",
        "logout",
        "times",
        "ulimit",
        "umask",
        "shopt",
        "caller",
        "complete",
        "compgen",
        "compopt",
        "fc",
        "history",
        "bind",
    }

    BLOCKED_COMMANDS: Set[str] = {
        # Deletion
        "rm",
        "rmdir",
        "shred",
        "unlink",
        # System modification
        "sudo",
        "su",
        "chown",
        "chgrp",
        "chmod",
        "chattr",
        "reboot",
        "shutdown",
        "halt",
        "poweroff",
        "init",
        # Package management (write operations)
        "apt",
        "apt-get",
        "pacman",
        "pip",
        "npm",
        "gem",
        "cargo",
        "go",
        # System tools
        "dd",
        "fdisk",
        "parted",
        "mkfs",
        "mount",
        "umount",
        "swapon",
        "swapoff",
        # Network manipulation
        "iptables",
        "ip6tables",
        "firewall-cmd",
        "ufw",
        "nc",
        "netcat",
        "nmap",
        "tcpdump",
        # Process manipulation
        "kill",
        "killall",
        "pkill",
        "xkill",
        # Compiler/interpreters
        "python",
        "python3",
        "perl",
        "ruby",
        "php",
        "node",
        "bash",
        "sh",
        "zsh",
        "fish",
        "dash",
        "ksh",
        "gcc",
        "g++",
        "cc",
        "make",
        "cmake",
        # Editors
        "vi",
        "vim",
        "nano",
        "emacs",
        "ed",
        "pico",
        # Cron/scheduling
        "crontab",
        "at",
        "batch",
        "systemctl",
    }

    def __init__(
        self,
        cwd: str,
        timeout_seconds: int = 30,
        max_output_chars: int = 50_000,
        enable_history: bool = True,
        max_history_size: int = 100,
    ):
        """
        Initialize Bash agent with security constraints.
        Args:
            cwd: Working directory
            timeout_seconds: Max execution time per command
            max_output_chars: Max output size before truncation
            enable_history: Track command history
            max_history_size: Max commands to keep in history
        """
        resolved_cwd = Path(cwd).resolve()
        if not resolved_cwd.exists():
            resolved_cwd.mkdir(parents=True, exist_ok=True)
        if not resolved_cwd.is_dir():
            raise ValueError(f"Path exists but is not a directory: {resolved_cwd}")
        self.cwd = str(resolved_cwd)
        self._timeout = timeout_seconds
        self._max_output = max_output_chars
        self._enable_history = enable_history
        self._max_history_size = max_history_size
        self._command_history: List[Dict[str, Any]] = []
        logger.info(f"Bash agent initialized in {self.cwd}")

    def _split_on_operators(self, cmd: str) -> List[Tuple[str, str]]:
        """
        Split command on control operators OUTSIDE of quotes and handle all edge cases.
        Handles:
        - Single and double quotes
        - Escaped characters
        - Nested quotes (e.g., "He said 'hello'")
        - Backticks and $() command substitution
        - Here-docs and here-strings
        Returns:
            List of (segment, operator) tuples
        """
        result = []
        current = []
        i = 0
        in_single_quote = False
        in_double_quote = False
        in_backtick = False
        paren_depth = 0  # Track $() depth
        while i < len(cmd):
            char = cmd[i]
            # Handle escapes - next char is literal
            if char == "\\" and i + 1 < len(cmd) and not in_single_quote:
                current.append(char)
                current.append(cmd[i + 1])
                i += 2
                continue
            # Single quotes - everything is literal except closing quote
            if char == "'" and not in_double_quote and not in_backtick:
                in_single_quote = not in_single_quote
                current.append(char)
                i += 1
                continue
            # Double quotes - allow some expansions
            if char == '"' and not in_single_quote and not in_backtick:
                in_double_quote = not in_double_quote
                current.append(char)
                i += 1
                continue
            # Backticks - command substitution
            if char == "`" and not in_single_quote and not in_double_quote:
                in_backtick = not in_backtick
                current.append(char)
                i += 1
                continue
            # $() command substitution depth tracking
            if not in_single_quote and not in_backtick:
                if char == "$" and i + 1 < len(cmd) and cmd[i + 1] == "(":
                    paren_depth += 1
                    current.append(char)
                    current.append("(")
                    i += 2
                    continue
                if char == ")" and paren_depth > 0:
                    paren_depth -= 1
                    current.append(char)
                    i += 1
                    continue
            # Only look for operators outside quotes and substitutions
            if (
                not in_single_quote
                and not in_double_quote
                and not in_backtick
                and paren_depth == 0
            ):
                # Check for two-character operators
                if i + 1 < len(cmd):
                    two_char = cmd[i : i + 2]
                    if two_char in ("&&", "||", "<<", ">>", ">&", "2>", "&>", "<&"):
                        # For redirections, include them in the current segment
                        if two_char in ("<<", ">>", ">&", "2>", "&>", "<&"):
                            current.append(two_char)
                            i += 2
                            continue
                        # For logical operators, split
                        else:
                            result.append(("".join(current).strip(), two_char))
                            current = []
                            i += 2
                            continue
                # Check for single-character operators
                if char in (";", "|"):
                    # Pipe is an operator
                    if char == "|" and (i + 1 >= len(cmd) or cmd[i + 1] != "|"):
                        result.append(("".join(current).strip(), char))
                        current = []
                        i += 1
                        continue
                    # Semicolon is an operator
                    elif char == ";":
                        result.append(("".join(current).strip(), char))
                        current = []
                        i += 1
                        continue
                # Handle redirections (>, <)
                if char in (">", "<"):
                    current.append(char)
                    i += 1
                    continue
            current.append(char)
            i += 1
        # Add final segment
        if current:
            result.append(("".join(current).strip(), ""))
        return result

    def _validate_git_command(self, tokens: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate git commands - only allow read-only operations.
        Returns:
            (is_safe, error_message)
        """
        if len(tokens) < 2:
            return True, None  # Let git handle the error
        git_subcommand = tokens[1]
        safe_git_commands = {
            "log",
            "show",
            "diff",
            "status",
            "branch",
            "tag",
            "ls-files",
            "ls-tree",
            "ls-remote",
            "rev-parse",
            "describe",
            "blame",
            "annotate",
            "grep",
            "config",
            "help",
            "version",
            "remote",
            "fetch",
            "clone",
        }
        dangerous_git_commands = {
            "commit",
            "push",
            "pull",
            "merge",
            "rebase",
            "reset",
            "checkout",
            "add",
            "rm",
            "mv",
            "clean",
            "stash",
            "cherry-pick",
            "revert",
            "tag",
            "branch",
        }
        if git_subcommand in dangerous_git_commands:
            return (
                False,
                f"Git subcommand '{git_subcommand}' is not allowed (write operation)",
            )
        if git_subcommand not in safe_git_commands:
            return (
                False,
                f"Git subcommand '{git_subcommand}' is not in the allowed list",
            )
        return True, None

    def _validate_docker_command(self, tokens: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate docker commands - only allow read-only or safe operations.
        Returns:
            (is_safe, error_message)
        """
        if len(tokens) < 2:
            return True, None  # Let docker handle the error
        subcommand = tokens[1]
        safe_docker_commands = {
            "ps",
            "info",
            "version",
            "inspect",
            "logs",
            "events",
            "top",
            "stats",
            "history",
            "images",
            "search",
            "volume",
            "network",
            "node",
            "service",
            "stack",
            "swarm",
            "config",
            "secret",
            "buildx",
            "context",
            "trust",
        }
        dangerous_docker_commands = {
            "run",
            "exec",
            "start",
            "stop",
            "restart",
            "kill",
            "rm",
            "rmi",
            "push",
            "pull",
            "commit",
            "tag",
            "save",
            "load",
            "import",
            "export",
            "build",
        }
        if subcommand in dangerous_docker_commands:
            return (
                False,
                f"Docker subcommand '{subcommand}' is not allowed (write operation)",
            )
        if subcommand not in safe_docker_commands:
            return False, f"Docker subcommand '{subcommand}' is not in the allowed list"
        return True, None

    def _validate_kubectl_command(
        self, tokens: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate kubectl commands - only allow read-only or safe operations.
        Returns:
            (is_safe, error_message)
        """
        if len(tokens) < 2:
            return True, None  # Let kubectl handle the error
        subcommand = tokens[1]
        safe_kubectl_commands = {
            "get",
            "describe",
            "logs",
            "top",
            "explain",
            "api-resources",
            "api-versions",
            "cluster-info",
            "version",
            "config",
            "whoami",
        }
        dangerous_kubectl_commands = {
            "apply",
            "create",
            "delete",
            "edit",
            "patch",
            "replace",
            "rollout",
            "scale",
            "taint",
            "cordon",
            "uncordon",
            "drain",
            "exec",
            "run",
        }
        if subcommand in dangerous_kubectl_commands:
            return (
                False,
                f"Kubectl subcommand '{subcommand}' is not allowed (write operation)",
            )
        if subcommand not in safe_kubectl_commands:
            return (
                False,
                f"Kubectl subcommand '{subcommand}' is not in the allowed list",
            )
        return True, None

    def _sanitize_command(self, cmd: str) -> Tuple[str, List[str]]:
        """
        Validate commands while respecting quoted strings and shell syntax.
        Returns:
            (sanitized_command, blocked_messages)
        """
        segments = self._split_on_operators(cmd)
        safe_parts = []
        blocked_messages = []
        for segment, operator in segments:
            if not segment:
                if operator:
                    safe_parts.append(f" {operator} ")
                continue
            try:
                tokens = shlex.split(segment)
                if not tokens:
                    safe_parts.append(segment)
                    if operator:
                        safe_parts.append(f" {operator} ")
                    continue
                base_cmd = tokens[0]
                # Check if it's a variable assignment (VAR=value)
                if "=" in base_cmd and not base_cmd.startswith("="):
                    safe_parts.append(segment)
                    if operator:
                        safe_parts.append(f" {operator} ")
                    continue
                # Skip validation for shell built-ins/reserved words
                if base_cmd in self.SHELL_RESERVED_WORDS:
                    safe_parts.append(segment)
                    if operator:
                        safe_parts.append(f" {operator} ")
                    continue
                # Check explicitly blocked commands
                if base_cmd in self.BLOCKED_COMMANDS:
                    msg = f"[BLOCKED] Command '{base_cmd}' is explicitly prohibited for security"
                    blocked_messages.append(msg)
                    safe_parts.append(f"echo {shlex.quote(msg)} >&2")
                    if operator:
                        safe_parts.append(f" {operator} ")
                    continue
                # Special validation for git, docker, kubectl
                if base_cmd == "git" and base_cmd in self.ALLOWED_COMMANDS:
                    is_safe, error_msg = self._validate_git_command(tokens)
                    if not is_safe:
                        msg = f"[BLOCKED] {error_msg}"
                        blocked_messages.append(msg)
                        safe_parts.append(f"echo {shlex.quote(msg)} >&2")
                        if operator:
                            safe_parts.append(f" {operator} ")
                        continue
                if base_cmd == "docker" and base_cmd in self.ALLOWED_COMMANDS:
                    is_safe, error_msg = self._validate_docker_command(tokens)
                    if not is_safe:
                        msg = f"[BLOCKED] {error_msg}"
                        blocked_messages.append(msg)
                        safe_parts.append(f"echo {shlex.quote(msg)} >&2")
                        if operator:
                            safe_parts.append(f" {operator} ")
                        continue
                if base_cmd == "kubectl" and base_cmd in self.ALLOWED_COMMANDS:
                    is_safe, error_msg = self._validate_kubectl_command(tokens)
                    if not is_safe:
                        msg = f"[BLOCKED] {error_msg}"
                        blocked_messages.append(msg)
                        safe_parts.append(f"echo {shlex.quote(msg)} >&2")
                        if operator:
                            safe_parts.append(f" {operator} ")
                        continue
                # Check if command is in allowed list
                if base_cmd not in self.ALLOWED_COMMANDS:
                    msg = f"[BLOCKED] Command '{base_cmd}' is not in the allowed list"
                    blocked_messages.append(msg)
                    safe_parts.append(f"echo {shlex.quote(msg)} >&2")
                    if operator:
                        safe_parts.append(f" {operator} ")
                    continue
                # Command is safe
                safe_parts.append(segment)
                if operator:
                    safe_parts.append(f" {operator} ")
            except ValueError as e:
                msg = f"[BLOCKED] Command parsing failed: {e}"
                blocked_messages.append(msg)
                safe_parts.append(f"echo {shlex.quote(msg)} >&2")
                if operator:
                    safe_parts.append(f" {operator} ")
        safe_cmd = "".join(safe_parts).strip()
        return safe_cmd, blocked_messages

    def _add_to_history(self, cmd: str, result: Dict[str, Any]) -> None:
        """Add command execution to history."""
        if not self._enable_history:
            return
        history_entry = {
            "timestamp": subprocess.run(
                ["date", "+%Y-%m-%d %H:%M:%S"], capture_output=True, text=True
            ).stdout.strip(),
            "command": cmd,
            "cwd": result["data"]["cwd"],
            "returncode": result["data"]["returncode"],
            "status": result["status"],
        }
        self._command_history.append(history_entry)
        if len(self._command_history) > self._max_history_size:
            self._command_history = self._command_history[-self._max_history_size :]
        logger.info("Added command to history")

    def exec_bash_command(self, cmd: Union[str, List, Dict]) -> Dict[str, Any]:
        """
        Execute bash command with comprehensive safety checks.
        Args:
            cmd: Command as string, list, or dict with 'cmd' key
        Returns:
            Dict with status, data (stdout, stderr, returncode, cwd)
        """
        original_cmd = cmd
        if isinstance(cmd, dict):
            cmd = cmd.get("cmd", "")
        elif isinstance(cmd, list):
            cmd = " ".join(str(part) for part in cmd)
        elif not isinstance(cmd, str):
            cmd = str(cmd)
        if not cmd or not cmd.strip():
            logger.warning("Empty command provided")
            return {
                "status": "error",
                "error": "No command provided",
                "data": {
                    "stdout": "",
                    "stderr": "No command provided",
                    "returncode": 1,
                    "cwd": self.cwd,
                },
            }
        cmd = cmd.strip()
        logger.info(f"Executing command: {cmd[:100]}{'...' if len(cmd) > 100 else ''}")
        try:
            safe_cmd, blocked_messages = self._sanitize_command(cmd)
            if blocked_messages:
                logger.warning(f"Blocked parts in command: {blocked_messages}")
            MARKER = "__OMNI_CWD_END__"
            wrapped_cmd = f"cd {shlex.quote(self.cwd)} && {{ {safe_cmd}; }}; echo -n '{MARKER}'; pwd -P"
            result = subprocess.run(
                ["/bin/bash", "-c", wrapped_cmd],
                capture_output=True,
                text=True,
                timeout=self._timeout,
                env={**subprocess.os.environ, "LANG": "C.UTF-8"},
            )
            stdout_raw = result.stdout
            stderr_raw = result.stderr
            full_stderr = stderr_raw
            if blocked_messages:
                blocked_str = "\n".join(blocked_messages)
                full_stderr = blocked_str + ("\n" + full_stderr if full_stderr else "")
            if MARKER in stdout_raw:
                stdout_part, cwd_part = stdout_raw.rsplit(MARKER, 1)
                stdout_clean = stdout_part
                new_cwd = cwd_part.strip()
                try:
                    new_cwd_path = Path(new_cwd).resolve()
                    if new_cwd_path.is_dir():
                        old_cwd = self.cwd
                        self.cwd = str(new_cwd_path)
                        if old_cwd != self.cwd:
                            logger.info(f"CWD changed: {old_cwd} -> {self.cwd}")
                except Exception as e:
                    logger.error(f"Failed to update CWD: {e}")
            else:
                stdout_clean = stdout_raw

            def truncate(s: str) -> str:
                if len(s) > self._max_output:
                    half = self._max_output // 2
                    return (
                        s[:half]
                        + f"\n\n... [OUTPUT TRUNCATED - {len(s) - self._max_output} chars omitted] ...\n\n"
                        + s[-half:]
                    )
                return s

            stdout_final = truncate(stdout_clean)
            stderr_final = truncate(full_stderr.rstrip("\n"))
            if result.returncode == 0 and not stdout_final and not stderr_final:
                stdout_final = "Command completed successfully with no output."
            response = {
                "status": "success" if result.returncode == 0 else "error",
                "data": {
                    "stdout": stdout_final,
                    "stderr": stderr_final,
                    "returncode": result.returncode,
                    "cwd": self.cwd,
                },
            }
            self._add_to_history(cmd, response)
            logger.info(f"Command completed with returncode {result.returncode}")
            return response
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {self._timeout}s")
            return {
                "status": "error",
                "error": f"Command timed out after {self._timeout} seconds",
                "data": {
                    "stdout": "",
                    "stderr": f"Command execution exceeded timeout limit of {self._timeout}s",
                    "returncode": -1,
                    "cwd": self.cwd,
                },
            }
        except Exception as e:
            logger.exception("Bash execution failed with unexpected error")
            error_msg = f"Execution failed: {type(e).__name__}: {str(e)}"
            return {
                "status": "error",
                "error": error_msg,
                "data": {
                    "stdout": "",
                    "stderr": error_msg,
                    "returncode": -1,
                    "cwd": self.cwd,
                },
            }

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get command history."""
        if limit:
            return self._command_history[-limit:]
        return self._command_history.copy()

    def clear_history(self) -> None:
        """Clear command history."""
        self._command_history.clear()
        logger.info("Command history cleared")

    def to_json_schema(self) -> dict:
        """Return JSON schema for tool integration."""
        return {
            "type": "object",
            "properties": {
                "cmd": {
                    "type": "string",
                    "description": (
                        "A bash command string that may include:\n"
                        "- Simple commands (e.g., 'ls -la', 'cat file.txt')\n"
                        "- Pipelines (e.g., 'df -h | grep /home')\n"
                        "- Redirections (e.g., 'echo \"data\" > file.txt')\n"
                        "- Conditional execution (e.g., 'mkdir dir && cd dir')\n"
                        "- Complex quoting (e.g., echo 'name;age|city' > data.csv)\n"
                        "- Docker commands (e.g., 'docker ps', 'docker logs container')\n"
                        "- Kubernetes commands (e.g., 'kubectl get pods', 'kubectl describe node')\n"
                        "- Log analysis (e.g., 'journalctl -u service', 'grep error log.txt')\n\n"
                        "The command will be executed in a secure environment.\n"
                        "Disallowed commands will be blocked with [BLOCKED] messages in stderr.\n"
                        "Always check both stdout and stderr in the response."
                    ),
                }
            },
            "required": ["cmd"],
        }

    @staticmethod
    def get_system_prompt() -> str:
        """Return system prompt for LLM integration."""
        allowed_sample = ", ".join(list(sorted(Bash.ALLOWED_COMMANDS))[:20]) + ", ..."
        return f"""You are DevOps Copilot, a production-grade secure Bash assistant for DevOps tasks, including file operations, system monitoring, container management, Kubernetes, log analysis, configuration auditing, and workspace reporting. You use only safe, allowed commands in a secure sandboxed environment.

### Allowed Commands (Sample)
{allowed_sample}
See full list in ALLOWED_COMMANDS set. Key tools include:
- File operations: ls, cat, grep, find, awk, sed, touch, mkdir, cp, mv
- System monitoring: df, du, free, top, htop, vmstat, iostat, sar
- Version control: git (read-only, e.g., log, status, diff)
- Containers: docker (read-only, e.g., ps, logs, inspect)
- Kubernetes: kubectl (read-only, e.g., get, describe, logs)
- Log analysis: journalctl, dmesg, grep, jq, yq
- Networking: ping, traceroute, netstat, ss, curl, wget

### Execution Environment
- Commands execute in a **secure sandboxed environment**
- Supports **pipes (`|`)**, **redirections (`>`, `>>`)**, **conditionals (`&&`, `||`)**, and **control structures**
- Complex quoting is fully supported (e.g., 'text ; with | special chars')
- Disallowed commands return `[BLOCKED]` in `stderr`
- **Allowed parts execute** — always check `stdout` and `stderr`
- Responses must be in XML format: `<thought>Your reasoning</thought><final_answer>Your answer</final_answer>`

### Response Format
Every command returns:
- `stdout`: Output from successful commands
- `stderr`: Error messages or `[BLOCKED]` notices
- `returncode`: Exit code (0 = success)
- `cwd`: Current working directory

### Best Practices
1. **Inspect `stderr`** for `[BLOCKED]` messages
2. **Handle partial execution** — some commands may run
3. **Use output** to guide next steps
4. **Confirm CWD** with `ls` or `pwd` after `cd`
5. **Explain blocked commands** and suggest alternatives
6. **Handle edge cases**: quotes, pipes, special characters
7. **Be efficient**: combine operations when safe
8. **For containers/Kubernetes**: use read-only commands (e.g., `docker ps`, `kubectl get`)
9. **For log analysis**: chain commands (e.g., `journalctl -u service | grep error`)

### Example Tasks
- **Log Analysis**: `journalctl -u nginx | grep "error" | tail -n 10`
- **Config Audit**: `find /etc -name "*.conf" | xargs grep "key=value"`
- **Workspace Report**: `ls -R | grep ".md$" && du -sh .`
- **Disk Usage**: `df -h && du -sh * | sort -hr`
- **Container Check**: `docker ps -a && docker logs my-container`
- **Kubernetes Status**: `kubectl get pods --all-namespaces`

### Prohibited Actions
- File deletion (rm, shred)
- System modification (sudo, chmod, reboot)
- Code execution (python, bash scripts)
- Package installation (apt, pip)
- Write operations in docker/kubectl (run, apply)

Be precise, security-conscious, and helpful. Prioritize user safety while enabling powerful DevOps workflows. Always respond in XML format with `<thought>` and `<final_answer>` tags."""


# New ASCII Art for OmniDevopsCopilot
ASCII_ART = r"""
   ___                   _   ___                       ___           _ _      _   
  / _ \  _ __ ___  _ __ (_) |   \ _____ _____ _ __ ___|  / ___ _ __(_) | ___| |_ 
 | | | || '_ ` _ \| '_ \| | | |) / _ \ V / _ \ '_ (_-<| | / _ \ '_ \ | |/ _ \ __|
 | |_| || | | | | | | | | | |___/\___/\_/\___/ .__/__/|_| \___/ .__/_|_|\___/\__|
  \___/ |_| |_| |_|_| |_|_|                   |_|              |_|                
        🔒 Secure • 🧠 Intelligent • 🚀 DevOps-Powered Assistant
                    ⚡ Powered by OmniCoreAgent Framework
"""

WELCOME_MESSAGE = """
# Welcome to **OmniDevopsCopilot**
A secure, AI-powered assistant for DevOps tasks, built for production-grade workflows.

**🤖 Framework**: Built on [OmniCoreAgent](https://github.com/Abiorh001/omnicoreagent) - A robust agent framework for production systems

✅ **Supported Commands**: `ls`, `grep`, `docker ps`, `kubectl get`, `journalctl`, and more  
❌ **Blocked Operations**: `rm`, `sudo`, `docker run`, `kubectl apply`, etc.  
💻 **Capabilities**: File operations, system monitoring, container management, Kubernetes, log analysis, configuration auditing, and workspace reporting  
📟 **Commands**: `/help`, `/history`, `/clear`, `/tools`, `/events`,`/store_info`, `/switch_store [redis|in_memory]`, `/exit`

### Example Queries
- Analyze build logs for errors
- Verify configuration files in services/
- Generate a workspace report in Markdown
- Audit disk usage
- Check running containers
- List Kubernetes pods
"""


class DevOpsCopilotRunner:
    def __init__(self):
        self.agent: Optional[OmniAgent] = None
        self.memory_router: Optional[MemoryRouter] = None
        self.event_router: Optional[EventRouter] = None
        self.bash_agent = Bash(cwd=os.getcwd(), timeout_seconds=60)
        self.connected = False
        self.session_id = "cli_session_001"
        self.console = Console() if RICH_AVAILABLE else None

    def print_styled(self, content: str, style: str = ""):
        """Print with rich styling or plain text."""
        if RICH_AVAILABLE:
            if style == "ascii":
                self.console.print(Text.from_ansi(ASCII_ART), justify="center")
            elif style == "welcome":
                self.console.print(Markdown(WELCOME_MESSAGE))
            elif style == "user":
                self.console.print(f"\n[bold blue]>[/bold blue] {content}")
            elif style == "agent":
                self.console.print(
                    Panel(content, title="🤖 Omni DevOps Copilot", border_style="green")
                )
            elif style == "error":
                self.console.print(f"[bold red]❌ {content}[/bold red]")
            elif style == "info":
                self.console.print(f"[bold cyan]ℹ️  {content}[/bold cyan]")
            else:
                self.console.print(content)
        else:
            if style == "ascii":
                print(ASCII_ART)
            elif style == "welcome":
                print(WELCOME_MESSAGE)
            elif style == "user":
                print(f"\n> {content}")
            elif style == "agent":
                print(f"\n{'=' * 50}\n🤖 Omni DevOps Copilot:\n{content}\n{'=' * 50}")
            elif style == "error":
                print(f"❌ {content}")
            elif style == "info":
                print(f"ℹ️  {content}")
            else:
                print(content)

    def extract_final_answer(self, response: str) -> str:
        """Extract <final_answer> content from XML response."""
        match = re.search(r"<final_answer>(.*?)</final_answer>", response, re.DOTALL)
        return match.group(1).strip() if match else response

    async def initialize(self):
        if self.connected:
            return

        self.print_styled("🚀 Initializing DevOps Copilot...", "info")
        logging.info("Initializing DevOps Copilot")

        # Initialize Bash agent & system prompt
        system_prompt = self.bash_agent.get_system_prompt()

        # Register tool
        tool_registry = ToolRegistry()

        @tool_registry.register_tool(
            name="exec_bash_command",
            description="Execute a safe bash command for DevOps tasks in a restricted environment.",
            inputSchema=self.bash_agent.to_json_schema(),
        )
        def exec_bash_command(cmd: str) -> dict:
            result = self.bash_agent.exec_bash_command(cmd)
            logging.info(f"Executed command: {cmd}, Result: {result}")
            return result

        self.memory_router = MemoryRouter("redis")
        self.event_router = EventRouter("redis_stream")

        # Initialize OmniAgent
        self.agent = OmniAgent(
            name="OmniDevOpsCopilot",
            system_instruction=system_prompt,
            model_config={
                "provider": "openai",
                "model": "gpt-4.1",
                "temperature": 0,
                "max_context_length": 1000,
            },
            local_tools=tool_registry,
            agent_config={
                "agent_name": "OmniDevOpsCopilot",
                "max_steps": 15,
                "tool_call_timeout": 20,
                "request_limit": 0,
                "total_tokens_limit": 0,
                "memory_config": {"mode": "sliding_window", "value": 100},
                "memory_results_limit": 5,
                "memory_similarity_threshold": 0.5,
                "enable_tools_knowledge_base": False,
                "tools_results_limit": 10,
                "tools_similarity_threshold": 0.1,
            },
            memory_router=self.memory_router,
            event_router=self.event_router,
            debug=True,
        )
        if not self.agent.is_event_store_available():
            self.print_styled("Warning: Event store not available.", "error")
            logging.warning("Event store not available")
        self.connected = True
        self.print_styled("✅ DevOps Copilot is ready!", "info")
        logging.info("DevOps Copilot initialized")

    async def handle_chat(
        self, query: str, session_id: str
    ) -> Optional[Dict[str, Any]]:
        if not self.connected:
            await self.initialize()

        if not self.agent:
            self.print_styled("Agent failed to initialize.", "error")
            logging.error("Agent failed to initialize")
            return None

        logging.info(f"Processing query: {query}, Session: {session_id}")
        try:
            # Run the query
            result = await self.agent.run(query=query, session_id=session_id)

            # Extract final answer for display
            response = result.get("response", "No response received.")
            final_answer = self.extract_final_answer(response)
            return {
                "response": final_answer,
                "session_id": result.get("session_id"),
                "agent_name": result.get("agent_name"),
            }
        except Exception as e:
            self.print_styled(f"Agent error occurs: {str(e)}")

    async def run_cli(self):
        """Main CLI loop."""
        self.print_styled("", "ascii")
        self.print_styled("", "welcome")

        def signal_handler(sig, frame):
            self.print_styled("👋 Shutting down gracefully...", "info")
            logging.info("Shutting down gracefully")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        while True:
            try:
                user_input = (
                    Prompt.ask(
                        "\n[bold blue][[/bold blue][bold green]OmniDevOpsCopilot[/bold green][bold blue]][/bold blue]"
                    )
                    if RICH_AVAILABLE
                    else input("\n[OmniDevOpsCopilot] ")
                )
                user_input = user_input.strip()
            except (EOFError, KeyboardInterrupt):
                self.print_styled("👋 Shutting down...", "info")
                logging.info("Shutting down")
                break

            if not user_input:
                continue

            if user_input.lower() in {"/exit", "/quit"}:
                self.print_styled(
                    "👋 Goodbye! Thanks for using OmniDevOpsCopilot.", "info"
                )
                logging.info("Exiting OmniDevOpsCopilot")
                break
            elif user_input.lower() == "/help":
                help_text = """
# OmniDevOpsCopilot Commands

- **DevOps Tasks**: Run queries like:
  - Analyze build logs for errors
  - Verify configuration files in services/
  - Generate a workspace report in Markdown
  - Audit disk usage
  - Check running containers
  - List Kubernetes pods
  - Generate system snapshot
  - Extract error patterns from a log
  - Validate directory structure
  - Monitor free memory
  - Normalize CSV files
  - Cross-reference file lists

- **CLI Commands**:
  - `/history`: View past commands (stored in Redis)
  - `/clear`: Clear session history
  - `/tools`: List available tools
  - `/events`: View stored events
  - `/store_info`: Show memory and event store info
  - `/switch_store [redis|in_memory]`: Switch memory/event store
  - `/exit`: Quit

# Safety
- **Allowed**: Safe commands (`ls`, `grep`, `docker ps`, `kubectl get`, `journalctl`, etc.)
- **Blocked**: Destructive operations (`rm`, `sudo`, `docker run`, `kubectl apply`, etc.)

# Examples
```bash
> journalctl -u nginx | grep error
> docker ps -a
> kubectl get pods --all-namespaces
> find /etc -name "*.conf" | xargs grep "key=value"
> df -h && du -sh * | sort -hr
                """.strip()
                self.print_styled(help_text, "info")
                continue
            elif user_input.lower() == "/history":
                history = await self.agent.get_session_history(self.session_id)
                self.print_styled(str(history), "info")
                logging.info(f"Retrieved session history: {history}")
                continue
            elif user_input.lower() == "/clear":
                await self.agent.clear_session_history(self.session_id)
                self.print_styled("Session history cleared.", "info")
                logging.info("Cleared session history")
                continue
            elif user_input.lower() == "/tools":
                tools = await self.agent.list_all_available_tools()
                self.print_styled(str(tools), "info")
                logging.info(f"Listed tools: {tools}")
                continue
            elif user_input.lower() == "/events":
                events = await self.agent.get_events(self.session_id)
                self.print_styled(str(events), "info")
                logging.info(f"Retrieved events: {events}")
                continue
            elif user_input.startswith("/switch_store"):
                parts = user_input.split()
                if len(parts) != 2 or parts[1] not in {"redis", "in_memory"}:
                    self.print_styled("Usage: /switch_store [redis|in_memory]", "error")
                    continue
                store_type = parts[1]
                try:
                    self.agent.switch_memory_store(store_type)
                    self.agent.switch_event_store(store_type)
                    self.print_styled(f"Switched to {store_type} store.", "info")
                    logging.info(f"Switched to {store_type} store")
                except Exception as e:
                    self.print_styled(f"Failed to switch store: {e}", "error")
                    logging.error(f"Failed to switch store: {e}")
                continue
            elif user_input.lower() == "/store_info":
                info = {
                    "memory_store_type": self.agent.get_memory_store_type(),
                    "event_store_type": self.agent.get_event_store_type(),
                    "event_store_available": self.agent.is_event_store_available(),
                    "event_store_info": self.agent.get_event_store_info(),
                }
                self.print_styled(str(info), "info")
                logging.info(f"Store info: {info}")
                continue

            self.print_styled(user_input, "user")
            response = await self.handle_chat(
                query=user_input, session_id=self.session_id
            )
            if response:
                self.print_styled(
                    response.get("response", "No response received."), "agent"
                )
                logging.info(f"Query response: {response}")

    async def shutdown(self):
        if self.agent:
            try:
                await self.agent.cleanup()
                self.print_styled("Resources cleaned up.", "info")
                logging.info("Resources cleaned up")
            except Exception as e:
                self.print_styled(f"⚠️ Cleanup warning: {e}", "error")
                logging.error(f"Cleanup warning: {e}")


async def main():
    runner = DevOpsCopilotRunner()
    try:
        await runner.run_cli()
    finally:
        await runner.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
