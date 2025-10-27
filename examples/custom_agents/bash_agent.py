import subprocess
import shlex
import os
import logging
from typing import Dict, Any, Optional, Set
from typing import Dict, List, Set, Tuple
from pathlib import Path
from omnicoreagent import OmniAgent, ToolRegistry, MemoryRouter, EventRouter
import sys
import asyncio
import signal
import re

# Try to import rich for enhanced UX
try:
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


logger = logging.getLogger(__name__)


import subprocess
import shlex
import re
from pathlib import Path
from typing import Dict, List, Literal, TypedDict, Any
import logging

logger = logging.getLogger(__name__)

ResponseFormat = Literal["concise", "detailed"]


class BashResult(TypedDict):
    summary: str
    success: bool
    cwd: str
    created_files: List[str]
    modified_files: List[str]
    errors: List[str]
    next_steps: List[str]
    raw_output: str  # only in detailed mode


class Bash:
    ALLOWED_COMMANDS = {
        "ls",
        "pwd",
        "cat",
        "head",
        "tail",
        "grep",
        "find",
        "which",
        "date",
        "stat",
        "wc",
        "du",
        "df",
        "whoami",
        "id",
        "uname",
        "hostname",
        "ps",
        "free",
        "lsof",
        "netstat",
        "ss",
        "env",
        "printenv",
        "basename",
        "dirname",
        "realpath",
        "file",
        "md5sum",
        "sha256sum",
        "sha1sum",
        "sort",
        "uniq",
        "cut",
        "tr",
        "awk",
        "sed",
        "diff",
        "comm",
        "column",
        "touch",
        "mkdir",
        "echo",
        "tee",
        "cp",
        "mv",
    }

    def __init__(self, cwd: str, timeout_seconds: int = 30):
        resolved = Path(cwd).resolve()
        if not resolved.is_dir() or resolved == Path("/"):
            raise ValueError("Invalid working directory")
        self.root = resolved
        self.cwd = str(resolved)
        self._timeout = timeout_seconds

    def _is_safe_path(self, p: str) -> bool:
        try:
            return (Path(self.cwd) / p).resolve().is_relative_to(self.root)
        except Exception:
            return False

    def _sanitize_and_track(self, cmd: str):
        """Returns (safe_cmd, tracking_info)"""
        parts = re.split(r"(\s*&&\s*|\s*\|\|\s*|\s*;\s*|\s*\|\s*)", cmd)
        safe_parts = []
        tracking = {
            "created": set(),
            "modified": set(),
            "errors": [],
            "allowed_segments": [],
        }

        for part in parts:
            s = part.strip()
            if s in ("&&", "||", ";", "|"):
                safe_parts.append(part)
            elif s:
                try:
                    tokens = shlex.split(s)
                    if not tokens:
                        safe_parts.append(part)
                        continue
                    base = tokens[0]

                    if base not in self.ALLOWED_COMMANDS:
                        msg = f"[BLOCKED] Command '{base}' is not allowed."
                        tracking["errors"].append(msg)
                        safe_parts.append(f"echo {shlex.quote(msg)} >&2")
                        continue

                    # Track potential file effects
                    if base == "touch":
                        for f in tokens[1:]:
                            if self._is_safe_path(f):
                                tracking["created"].add(f)
                                tracking["modified"].add(f)
                    elif base == "mkdir":
                        for f in tokens[1:]:
                            if not f.startswith("-") and self._is_safe_path(f):
                                tracking["created"].add(f)
                    elif base in ("cp", "mv", "tee"):
                        if base in ("cp", "mv") and len(tokens) >= 3:
                            dst = tokens[-1]
                            if self._is_safe_path(dst):
                                tracking["modified"].add(dst)
                        elif base == "tee":
                            for f in tokens[1:]:
                                if not f.startswith("-") and self._is_safe_path(f):
                                    tracking["modified"].add(f)

                    # Validate paths
                    unsafe = False
                    if base in ("cp", "mv", "touch", "mkdir", "tee"):
                        targets = self._extract_targets(base, tokens)
                        for t in targets:
                            if not self._is_safe_path(t):
                                msg = f"[BLOCKED] Unsafe path '{t}' in command '{s}'"
                                tracking["errors"].append(msg)
                                safe_parts.append(f"echo {shlex.quote(msg)} >&2")
                                unsafe = True
                                break
                        if unsafe:
                            continue

                    safe_parts.append(part)
                    tracking["allowed_segments"].append(s)

                except Exception as e:
                    msg = f"[BLOCKED] Parse error in '{s}': {e}"
                    tracking["errors"].append(msg)
                    safe_parts.append(f"echo {shlex.quote(msg)} >&2")
            else:
                safe_parts.append(part)

        return "".join(safe_parts), tracking

    def _extract_targets(self, cmd: str, tokens: List[str]) -> List[str]:
        if cmd in ("cp", "mv"):
            return [tokens[-1]] if len(tokens) >= 3 else []
        elif cmd == "tee":
            return [t for t in tokens[1:] if not t.startswith("-")]
        elif cmd == "touch":
            return tokens[1:]
        elif cmd == "mkdir":
            return [t for t in tokens[1:] if not t.startswith("-")]
        return []

    def exec_bash_command(
        self, cmd: str, response_format: ResponseFormat = "detailed"
    ) -> Dict[str, Any]:
        if not cmd.strip():
            return self._build_response(
                success=False,
                summary="No command provided.",
                errors=["Empty command."],
                response_format=response_format,
            )

        safe_cmd, tracking = self._sanitize_and_track(cmd)

        # Run sanitized command
        try:
            wrapped = f"cd {shlex.quote(self.cwd)} && {{ {safe_cmd}; }}; pwd"
            result = subprocess.run(
                ["/bin/bash", "-c", wrapped],
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
            raw_out = result.stdout
            stderr = result.stderr

            # Update cwd
            lines = raw_out.rstrip().split("\n")
            if lines:
                new_cwd = lines[-1].strip()
                try:
                    new_path = Path(new_cwd).resolve()
                    if new_path.is_relative_to(self.root):
                        self.cwd = str(new_path)
                except Exception:
                    pass
                output = "\n".join(lines[:-1])
            else:
                output = ""

            # Combine output + stderr
            full_raw = (output + "\n" + stderr).strip()

            # Build semantic response
            success = len(tracking["errors"]) == 0 and result.returncode == 0
            summary = self._generate_summary(tracking, success)

            return self._build_response(
                status="success",
                success=success,
                summary=summary,
                cwd=self.cwd,
                created_files=sorted(tracking["created"]),
                modified_files=sorted(tracking["modified"]),
                errors=tracking["errors"],
                raw_output=full_raw if response_format == "detailed" else "",
                response_format=response_format,
            )

        except subprocess.TimeoutExpired:
            return self._build_response(
                status="error",
                success=False,
                summary="Command timed out.",
                errors=[f"Execution exceeded {self._timeout} seconds."],
                response_format=response_format,
            )
        except Exception as e:
            return self._build_response(
                status="error",
                success=False,
                summary="Execution failed.",
                errors=[str(e)],
                response_format=response_format,
            )

    def _generate_summary(self, tracking: dict, overall_success: bool) -> str:
        parts = []

        if tracking["allowed_segments"]:
            parts.append(f"Executed: {'; '.join(tracking['allowed_segments'])}")

        if tracking["created"]:
            files = ", ".join(sorted(tracking["created"]))
            parts.append(f"Created files/dirs: {files}")

        if tracking["modified"]:
            files = ", ".join(sorted(set(tracking["modified"]) - tracking["created"]))
            if files:
                parts.append(f"Modified files: {files}")

        if tracking["errors"]:
            parts.append("Some commands were blocked for safety.")

        if not parts:
            return "No operations performed."

        return ". ".join(parts) + "."

    def _build_response(
        self,
        success: bool,
        summary: str,
        status: str,
        cwd: str = None,
        created_files: List[str] = None,
        modified_files: List[str] = None,
        errors: List[str] = None,
        raw_output: str = "",
        response_format: ResponseFormat = "detailed",
    ) -> Dict[str, Any]:
        base = {
            "status": status,
            "summary": summary,
            "success": success,
            "cwd": cwd or self.cwd,
        }

        if response_format == "detailed":
            base.update(
                {
                    "created_files": created_files or [],
                    "modified_files": modified_files or [],
                    "errors": errors or [],
                    "raw_output": raw_output,
                    "next_steps": self._suggest_next_steps(
                        errors, created_files, modified_files
                    ),
                }
            )
        else:
            # Concise: only summary + success + cwd
            pass

        return base

    def _suggest_next_steps(self, errors, created, modified):
        suggestions = []
        if created:
            suggestions.append(f"List contents with: ls {' '.join(created[:2])}")
        if "rm" in str(errors) or "delete" in str(errors):
            suggestions.append(
                "Deletion is not allowed. Use file inspection tools instead."
            )
        if not errors and not (created or modified):
            suggestions.append("Try a different command to inspect or create files.")
        return suggestions

    # --- Tool Schema & Prompt ---
    def to_json_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "cmd": {"type": "string", "description": "Bash command to execute."},
                "response_format": {
                    "type": "string",
                    "enum": ["concise", "detailed"],
                    "default": "detailed",
                    "description": "Level of detail in response. Use 'concise' to save context.",
                },
            },
            "required": ["cmd"],
        }

    @staticmethod
    def get_system_prompt() -> str:
        return """You are an intelligent Bash agent that helps users manage files and inspect systems.

**Tool Behavior**:
- You can run commands like: ls, cat, mkdir, cp, mv, echo, grep, find, etc.
- Dangerous commands (rm, chmod, sudo, etc.) are automatically blocked with clear messages.
- All file operations are confined to your workspace.
- The tool returns a **natural language summary** of what happened, not raw shell output.

**How to Use Responses**:
- Read the `summary` field first — it tells you what succeeded or failed.
- Check `errors` if something went wrong.
- Use `created_files` or `modified_files` to know what changed.
- Follow `next_steps` suggestions when available.
- In `concise` mode, you get only the summary — use when context is tight.

**Best Practices**:
- Prefer single, focused commands.
- If a command is blocked, choose a safe alternative.
- After creating a directory, list its contents to confirm.
- Never assume a command succeeded — always check the response.

You are a precise, adaptive, and secure assistant. Prioritize clarity and safety."""


# --- ASCII ART + BRANDING ---
ASCII_ART = r"""
___                _ ___          _      _                    _   
 / _ \ _ __ ___  _ _(_) _ ) __ _ __| |_   /_\  __ _ ___ _ _  | |_ 
| (_) | '  \   \| ' \ | _ \/ _` (_-< ' \ / _ \/ _` / -_) ' \ |  _|
 \___/|_|_|_|_||_|_||_|___/\__,_/__/_||_/_/ \_\__, |\___|_||_| \__|
                                              |___/
                                                                    
          🔒 Secure • 🧠 Intelligent • 🖥️  Bash-Powered Agent
"""

WELCOME_MESSAGE = """
You are now interacting with **OmniBashAgent** — a secure, AI-powered shell assistant.

✅ Only safe commands are allowed (e.g., `ls`, `cat`, `grep`, `touch`, `mkdir`)  
❌ Dangerous operations (`rm`, `sudo`, `>`, `|`, etc.) are blocked  
💡 Type `/help` for tips, `/exit` to quit

Start by asking or commanding:
> What's in this directory?
> List all Python files
> Create a note called todo.txt
"""


# --- CLI RUNNER ---
class OmniBashAgentRunner:
    def __init__(self):
        self.agent: Optional[OmniAgent] = None
        self.memory_router: Optional[MemoryRouter] = None
        self.event_router: Optional[EventRouter] = None
        self.connected = False
        self.session_id: Optional[str] = None
        self.console = Console() if RICH_AVAILABLE else None

    def print_styled(self, content: str, style: str = ""):
        """Print with rich styling if available, else plain."""
        if RICH_AVAILABLE:
            if style == "ascii":
                text = Text.from_ansi(ASCII_ART)
                self.console.print(text, justify="center")
            elif style == "welcome":
                self.console.print(Markdown(WELCOME_MESSAGE))
            elif style == "user":
                self.console.print(f"\n[bold blue]>[/bold blue] {content}")
            elif style == "agent":
                self.console.print(
                    Panel(content, title="🤖 OmniBashAgent", border_style="green")
                )
            elif style == "error":
                self.console.print(f"[bold red]❌ {content}[/bold red]")
            elif style == "info":
                self.console.print(f"[bold cyan]ℹ️  {content}[/bold cyan]")
            else:
                self.console.print(content)
        else:
            # Fallback to plain text
            if style == "ascii":
                print(ASCII_ART)
            elif style == "welcome":
                print(WELCOME_MESSAGE)
            elif style == "user":
                print(f"\n> {content}")
            elif style == "agent":
                print(f"\n{'=' * 50}\n🤖 OmniBashAgent:\n{content}\n{'=' * 50}")
            elif style == "error":
                print(f"❌ {content}")
            elif style == "info":
                print(f"ℹ️  {content}")
            else:
                print(content)

    async def initialize(self):
        if self.connected:
            return

        self.print_styled("🚀 Initializing OmniBashAgent...", "info")

        # Initialize Bash agent & system prompt
        bash_agent = Bash(cwd=os.getcwd())
        system_prompt = bash_agent.get_system_prompt()

        # Register tool
        tool_registry = ToolRegistry()

        @tool_registry.register_tool(
            name="exec_bash_command",
            description="Execute a safe bash command in a restricted environment.",
            inputSchema=bash_agent.to_json_schema(),
        )
        def exec_bash_command(cmd: str) -> dict:
            result = bash_agent.exec_bash_command(cmd)
            logger.info(f"Executed command: {cmd} | Result: {result}")
            return result

        # Initialize routers
        self.memory_router = MemoryRouter("in_memory")
        self.event_router = EventRouter("in_memory")

        # Initialize OmniAgent
        self.agent = OmniAgent(
            name="OmniBashAgent",
            system_instruction=system_prompt,
            model_config={
                "provider": "openai",
                "model": "gpt-4.1",
                "temperature": 0,
                "max_context_length": 1000,
            },
            local_tools=tool_registry,
            agent_config={
                "agent_name": "OmniAgent",
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
            debug=False,
        )
        self.connected = True
        self.print_styled("✅ OmniBashAgent is ready!", "info")

    async def handle_chat(self, query: str, session_id: str) -> Optional[str]:
        if not self.connected:
            await self.initialize()

        if not self.agent:
            self.print_styled("Agent failed to initialize.", "error")
            return None

        try:
            result = await self.agent.run(query=query, session_id=session_id)
            return result.get("response", "No response received.")
        except Exception as e:
            self.print_styled(f"Agent error: {e}", "error")
            return None

    async def run_cli(self):
        """Main CLI loop."""
        # Show ASCII + welcome
        self.print_styled("", "ascii")
        self.print_styled("Welcome to OmniBashAgent CLI", "info")
        self.print_styled("", "welcome")

        def signal_handler(sig, frame):
            print("\n\n👋 Shutting down gracefully...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        while True:
            try:
                if RICH_AVAILABLE:
                    from rich.prompt import Prompt

                    user_input = Prompt.ask(
                        "\n[bold blue][[/bold blue][bold green]OmniBash[/bold green][bold blue]][/bold blue]"
                    )
                else:
                    user_input = input("\n[OmniBash] ")
            except EOFError:
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            if user_input.lower() in {"/exit", "/quit", "exit", "quit"}:
                self.print_styled("👋 Goodbye! Thanks for using OmniBashAgent.", "info")
                break
            elif user_input.lower() == "/help":
                help_text = """
**Commands:**
- Ask natural language questions: *"What files are here?"*
- Give commands: *"List all .py files"*, *"Create a file called notes.txt"*
- Use allowed Bash commands indirectly via the agent

**Safety:**
- All file writes are safe (only `touch`, `mkdir` allowed for now)
- No deletion, overwrites, or system changes possible

Type `/exit` to quit.
                """.strip()
                self.print_styled(help_text, "info")
                continue

            self.print_styled(user_input, "user")
            response = await self.handle_chat(
                query=user_input, session_id="cli_session_001"
            )
            if response:
                self.print_styled(response, "agent")

    async def shutdown(self):
        if self.agent:
            try:
                await self.agent.cleanup()
            except Exception as e:
                if RICH_AVAILABLE:
                    self.console.print(f"[yellow]⚠️  Cleanup warning: {e}[/yellow]")
                else:
                    print(f"⚠️  Cleanup warning: {e}")


# --- ENTRY POINT ---
async def main():
    runner = OmniBashAgentRunner()
    try:
        await runner.run_cli()
    finally:
        await runner.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
