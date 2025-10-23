import hashlib
import json
import logging
import platform
import re
import subprocess
import sys
import uuid
from collections import defaultdict, deque
from pathlib import Path
from typing import Any
from types import SimpleNamespace
from rich.console import Console, Group
from rich.panel import Panel
from rich.pretty import Pretty
from rich.text import Text
from datetime import datetime, timezone
from decouple import config as decouple_config
import xml.etree.ElementTree as ET
from omnicoreagent.core.constants import AGENTS_REGISTRY
from omnicoreagent.core.system_prompts import generate_react_agent_role_prompt
import asyncio
from typing import Any, Callable
from html import escape
import ast

console = Console()
# Configure logging
logger = logging.getLogger("omnicoreagent")
logger.setLevel(logging.INFO)

# Vector database feature flag
ENABLE_VECTOR_DB = decouple_config("ENABLE_VECTOR_DB", default=False, cast=bool)
# Embedding API key for LLM-based embeddings
EMBEDDING_API_KEY = decouple_config("EMBEDDING_API_KEY", default=None)


def is_vector_db_enabled() -> bool:
    """Check if vector database features are enabled."""
    return ENABLE_VECTOR_DB


def is_embedding_requirements_met() -> bool:
    """Check if embedding requirements are met (both vector DB and API key are set)."""
    return ENABLE_VECTOR_DB and EMBEDDING_API_KEY is not None


# Remove any existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Create console handler with immediate flush
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create file handler with immediate flush
log_file = Path("omnicoreagent.log")
file_handler = logging.FileHandler(log_file, mode="a")
file_handler.setLevel(logging.INFO)

# Create formatters
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Set formatters
console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Configure handlers to flush immediately
console_handler.flush = sys.stdout.flush
file_handler.flush = lambda: file_handler.stream.flush()
import asyncio
import inspect
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Coroutine, Any


class BackgroundTaskManager:
    """Unified helper for running background, async, or blocking tasks safely."""

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = set()

    # Fire-and-forget for SYNC functions
    def run_background(self, func: Callable[..., Any], *args, **kwargs):
        """
        Run a synchronous function in a background thread (fire-and-forget).
        Use this for non-async I/O or CPU-bound functions.
        """

        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception:
                traceback.print_exc()

        asyncio.create_task(asyncio.to_thread(wrapper))

    # Fire-and-forget for lightweight ASYNC functions
    def run_background_async(self, coro: Coroutine):
        """
        Run an async coroutine in the same event loop (fire-and-forget).
        Use only for lightweight, non-blocking coroutines.
        """

        async def runner():
            try:
                await coro
            except Exception:
                traceback.print_exc()

        asyncio.create_task(runner())

    # Strict isolation for DB or heavy async functions
    def run_background_strict(self, coro):
        """Fire and forget a coroutine safely, with internal error handling."""
        if asyncio.iscoroutine(coro):
            task = asyncio.create_task(self._run_safe(coro))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)
        else:
            logger.warning(f"Tried to run non-coroutine task: {coro}")

    async def _run_safe(self, coro):
        """Wrap background coroutine in safety net."""
        try:
            await coro
        except asyncio.CancelledError:
            logger.debug("Background task cancelled.")
        except Exception as e:
            logger.exception(f"Background task failed: {e}")

    # Run blocking function and await its result
    def run_in_executor(
        self, func: Callable[..., Any], *args, **kwargs
    ) -> asyncio.Task:
        """
        Run a blocking function in the threadpool and return an awaitable task.
        Use this when you need the result (not fire-and-forget).
        """
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.executor, lambda: func(*args, **kwargs))


def clean_json_response(json_response):
    """Clean and extract JSON from the response."""
    try:
        # First try to parse as is
        json.loads(json_response)
        return json_response
    except json.JSONDecodeError:
        # If that fails, try to extract JSON
        try:
            # Remove any markdown code blocks
            if "```" in json_response:
                # Extract content between first ``` and last ```
                start = json_response.find("```") + 3
                end = json_response.rfind("```")
                # Skip the "json" if it's present after first ```
                if json_response[start : start + 4].lower() == "json":
                    start += 4
                json_response = json_response[start:end].strip()

            # Find the first { and last }
            start = json_response.find("{")
            end = json_response.rfind("}") + 1
            if start >= 0 and end > start:
                json_response = json_response[start:end]

            # Validate the extracted JSON
            json.loads(json_response)
            return json_response
        except (json.JSONDecodeError, ValueError) as e:
            raise json.JSONDecodeError(
                f"Could not extract valid JSON from response: {str(e)}",
                json_response,
                0,
            )


async def generate_react_agent_role_prompt_func(
    mcp_server_tools: dict[str, Any],
    llm_connection: Callable,
) -> str:
    """Generate the react agent role prompt for a specific server."""
    react_agent_role_prompt = generate_react_agent_role_prompt(
        mcp_server_tools=mcp_server_tools,
    )
    messages = [
        {"role": "system", "content": react_agent_role_prompt},
        {"role": "user", "content": "Generate the agent role prompt"},
    ]
    response = await llm_connection.llm_call(messages)
    if response:
        if hasattr(response, "choices"):
            return response.choices[0].message.content.strip()
        elif hasattr(response, "message"):
            return response.message.content.strip()
    return ""


async def ensure_agent_registry(
    available_tools: dict[str, Any],
    llm_connection: Callable,
) -> dict[str, str]:
    """
    Ensure that agent registry entries exist for all servers in available_tools.
    Missing entries will be generated concurrently.
    """
    tasks = []
    missing_servers = []

    for server_name in available_tools.keys():
        if server_name not in AGENTS_REGISTRY:
            missing_servers.append(server_name)
            tasks.append(
                asyncio.create_task(
                    generate_react_agent_role_prompt_func(
                        mcp_server_tools=available_tools[server_name],
                        llm_connection=llm_connection,
                    )
                )
            )

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for server_name, result in zip(missing_servers, results):
            if isinstance(result, Exception):
                continue
            AGENTS_REGISTRY[server_name] = result

    return AGENTS_REGISTRY


def hash_text(text: str) -> str:
    """Generate a simple hash for a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class RobustLoopDetector:
    def __init__(
        self,
        maxlen: int = 20,
        consecutive_threshold: int = 5,
        pattern_detection: bool = True,
        max_pattern_length: int = 3,
        debug: bool = True,
    ):
        """
        Initialize a robust loop detector.

        - maxlen: number of past interactions to track
        - consecutive_threshold: number of consecutive calls to same tool to detect loop
        - pattern_detection: enable repeating pattern detection
        - max_pattern_length: max pattern length for pattern detection
        - debug: enable debug logging
        """
        self.global_interactions = deque(maxlen=maxlen)
        self.tool_interactions: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=maxlen)
        )
        self.consecutive_threshold = consecutive_threshold
        self.pattern_detection = pattern_detection
        self.max_pattern_length = max_pattern_length

        self._last_tool = None
        self._consecutive_count = 0
        self.debug = debug

    def record_tool_call(
        self, tool_name: str, tool_input: str, tool_output: str
    ) -> None:
        """Record a new tool call interaction."""
        signature = (
            tool_name,
            hash_text(tool_input),
            hash_text(tool_output),
        )

        # Update global and per-tool history
        self.global_interactions.append(signature)
        self.tool_interactions[tool_name].append(signature)

        # Update consecutive counter
        if tool_name == self._last_tool:
            self._consecutive_count += 1
        else:
            self._last_tool = tool_name
            self._consecutive_count = 1

        if self.debug:
            logger.info(
                f"[LoopDetector] Tool '{tool_name}' called. "
                f"Consecutive count: {self._consecutive_count}"
            )

    def reset(self, tool_name: str | None = None) -> None:
        """Reset loop memory."""
        if tool_name:
            self.tool_interactions.pop(tool_name, None)
        else:
            self.global_interactions.clear()
            self.tool_interactions.clear()
        self._last_tool = None
        self._consecutive_count = 0

        if self.debug:
            logger.info("[LoopDetector] Reset performed.")

    def _is_tool_stuck_consecutive(self, tool_name: str) -> bool:
        """Check if a tool has been called consecutively enough times to be stuck."""
        stuck = (
            tool_name == self._last_tool
            and self._consecutive_count >= self.consecutive_threshold
        )
        if self.debug and stuck:
            logger.info(
                f"[LoopDetector] Tool '{tool_name}' is stuck due to "
                f"{self._consecutive_count} consecutive calls."
            )
        return stuck

    def _has_tool_pattern_loop(self, tool_name: str) -> bool:
        """Detect repeating patterns for a tool."""
        interactions = list(self.tool_interactions.get(tool_name, []))
        if len(interactions) < 2 or not self.pattern_detection:
            return False
        for pattern_len in range(
            1, min(self.max_pattern_length + 1, len(interactions) // 2 + 1)
        ):
            pattern = interactions[-pattern_len:]
            prev_pattern = interactions[-2 * pattern_len : -pattern_len]
            if pattern == prev_pattern:
                if self.debug:
                    logger.info(
                        f"[LoopDetector] Tool '{tool_name}' has repeating pattern: {pattern_len} steps."
                    )
                return True
        return False

    def is_looping(self, tool_name: str | None = None) -> bool:
        """Check if a tool or global state is looping."""
        if tool_name:
            return self._is_tool_stuck_consecutive(
                tool_name
            ) or self._has_tool_pattern_loop(tool_name)
        # Global: check all tools
        return any(
            self._is_tool_stuck_consecutive(name) or self._has_tool_pattern_loop(name)
            for name in self.tool_interactions.keys()
        )

    def get_loop_type(self, tool_name: str | None = None) -> list[str]:
        """Get detailed loop type for a tool."""
        types = []
        if tool_name:
            if self._is_tool_stuck_consecutive(tool_name):
                types.append("consecutive_calls")
            if self._has_tool_pattern_loop(tool_name):
                types.append("repeating_pattern")
        else:
            for name in self.tool_interactions.keys():
                if self._is_tool_stuck_consecutive(name):
                    types.append(f"{name}: consecutive_calls")
                if self._has_tool_pattern_loop(name):
                    types.append(f"{name}: repeating_pattern")
        return types


def strip_comprehensive_narrative(text):
    """
    Removes <comprehensive_narrative> tags. Returns original text if any error occurs.
    """
    try:
        if not isinstance(text, str):
            return str(text)
        return re.sub(r"</?comprehensive_narrative>", "", text).strip()
    except (TypeError, re.error):
        return str(text)


def json_to_smooth_text(content):
    """
    Converts LLM content (string or JSON string) into smooth, human-readable text.
    - If content is JSON in string form, parse and flatten it.
    - If content is plain text, return as-is.
    - Safe fallback: returns original content if anything fails.
    """
    try:
        # if content is str, try to parse as JSON
        if isinstance(content, str):
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                # Not JSON, treat as plain text
                return content
        else:
            data = content  # already dict/list/scalar

        # recursively flatten
        def _flatten(obj):
            if isinstance(obj, dict):
                sentences = []
                for k, v in obj.items():
                    pretty_key = k.replace("_", " ").capitalize()
                    sentences.append(f"{pretty_key}: {_flatten(v)}")
                return " ".join(sentences)
            elif isinstance(obj, list):
                items = [_flatten(v) for v in obj]
                if len(items) == 1:
                    return items[0]
                return ", ".join(items[:-1]) + " and " + items[-1]
            else:
                return str(obj)

        return _flatten(data)

    except Exception:
        # fallback: return original string content
        return str(content)


def normalize_enriched_tool(enriched: str) -> str:
    """
    Normalize enriched tool XML (<tool_document>) into a hybrid
    natural-language + structured format optimized for embedding & retrieval.
    """

    try:
        root = ET.fromstring(enriched)
    except Exception:
        # fallback: return as plain text if parsing fails
        return enriched.strip()

    name = root.findtext("expanded_name", default="Unnamed Tool")
    description = root.findtext("long_description", default="").strip()

    parts = [f"Tool: {name}\n{description}"]

    params_root = root.find("argument_schema")
    if params_root is not None:
        params = []
        for param in params_root.findall("parameter"):
            pname = param.findtext("name", default="unknown")
            ptype = param.findtext("type", default="unspecified")
            preq = param.findtext("required", default="false")
            pdesc = (param.findtext("description") or "").strip()
            params.append(f"- {pname} ({ptype}, required={preq}): {pdesc}")
        if params:
            parts.append("Parameters:\n" + "\n".join(params))

    questions_root = root.find("synthetic_questions")
    if questions_root is not None:
        questions = [
            f"- {(q.text or '').strip()}"
            for q in questions_root.findall("question")
            if (q.text or "").strip()
        ]
        if questions:
            parts.append("Example Questions:\n" + "\n".join(questions))

    topics_root = root.find("key_topics")
    if topics_root is not None:
        topics = [
            (t.text or "").strip()
            for t in topics_root.findall("topic")
            if (t.text or "").strip()
        ]
        if topics:
            parts.append("Key Topics: " + ", ".join(topics))

    return "\n\n".join(parts).strip()


def handle_stuck_state(original_system_prompt: str, message_stuck_prompt: bool = False):
    """
    Creates a modified system prompt that includes stuck detection guidance.

    Parameters:
    - original_system_prompt: The normal system prompt you use
    - message_stuck_prompt: If True, use a shorter version of the stuck prompt

    Returns:
    - Modified system prompt with stuck guidance prepended
    """
    if message_stuck_prompt:
        stuck_prompt = (
            "⚠️ You are stuck in a loop. This must be addressed immediately.\n\n"
            "REQUIRED ACTIONS:\n"
            "1. **STOP** the current approach\n"
            "2. **ANALYZE** why the previous attempts failed\n"
            "3. **TRY** a completely different method\n"
            "4. **IF** the issue cannot be resolved:\n"
            "   - Explain clearly why not\n"
            "   - Provide alternative solutions\n"
            "   - DO NOT repeat the same failed action\n\n"
            "   - DO NOT try again. immediately stop and do not try again.\n\n"
            "   - Tell user your last known good state, error message and the current state of the conversation.\n\n"
            "❗ CONTINUING THE SAME APPROACH WILL RESULT IN FURTHER FAILURES"
        )
    else:
        stuck_prompt = (
            "⚠️ It looks like you're stuck or repeating an ineffective approach.\n"
            "Take a moment to do the following:\n"
            "1. **Reflect**: Analyze why the previous step didn't work (e.g., tool call failure, irrelevant observation).\n"
            "2. **Try Again Differently**: Use a different tool, change the inputs, or attempt a new strategy.\n"
            "3. **If Still Unsolvable**:\n"
            "   - **Clearly explain** to the user *why* the issue cannot be solved.\n"
            "   - Provide any relevant reasoning or constraints.\n"
            "   - Offer one or more alternative solutions or next steps.\n"
            "   - DO NOT try again. immediately stop and do not try again.\n\n"
            "   - Tell user your last known good state, error message and the current state of the conversation.\n\n"
            "❗ Do not repeat the same failed strategy or go silent."
        )

    # Create a temporary modified system prompt
    modified_system_prompt = (
        f"{stuck_prompt}\n\n"
        f"Your previous approaches to solve this problem have failed. You need to try something completely different.\n\n"
        # f"{original_system_prompt}"
    )

    return modified_system_prompt


def normalize_metadata(obj):
    if isinstance(obj, dict):
        return {k: normalize_metadata(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_metadata(i) for i in obj]
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    return obj


def dict_to_namespace(d):
    return json.loads(json.dumps(d), object_hook=lambda x: SimpleNamespace(**x))


def utc_now_str() -> str:
    return datetime.now(timezone.utc).isoformat()


def format_timestamp(ts) -> str:
    if not isinstance(ts, datetime):
        ts = datetime.fromisoformat(ts)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def strip_json_comments(text: str) -> str:
    """
    Removes // and /* */ style comments from JSON-like text,
    but only if they're outside of double-quoted strings.
    """

    def replacer(match):
        s = match.group(0)
        if s.startswith('"'):
            return s  # keep strings intact
        return ""  # remove comments

    pattern = r'"(?:\\.|[^"\\])*"' + r"|//.*?$|/\*.*?\*/"
    return re.sub(pattern, replacer, text, flags=re.DOTALL | re.MULTILINE)


def show_tool_response(agent_name, tool_name, tool_args, observation):
    content = Group(
        Text(agent_name.upper(), style="bold magenta"),
        Text(f"→ Calling tool: {tool_name}", style="bold blue"),
        Text("→ Tool input:", style="bold yellow"),
        Pretty(tool_args),
        Text("→ Tool response:", style="bold green"),
        Pretty(observation),
    )

    panel = Panel.fit(content, title="🔧 TOOL CALL LOG", border_style="bright_black")
    console.print(panel)


def normalize_tool_args(value: Any) -> Any:
    """
    Deeply normalize tool arguments.
    - If value is a list with single dict, unwrap it
    - Converts stringified booleans to bool
    - Converts stringified numbers to int/float
    - Converts "null"/"none" to None
    - Converts stringified JSON or Python literals to Python objects
    - Handles nested dicts, lists, tuples
    - Preserves strings with XML/multi-line content
    """

    # UNWRAP single-element list containing a dict
    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], dict):
        value = value[0]

    def _normalize(v: Any) -> Any:
        # 1. Handle strings
        if isinstance(v, str):
            val = v.strip()
            # null / none
            if val.lower() in ("null", "none"):
                return None
            # boolean
            if val.lower() == "true":
                return True
            if val.lower() == "false":
                return False
            # integer / float
            try:
                if "." in val or "e" in val.lower():
                    return float(val)
                return int(val)
            except ValueError:
                pass
            # JSON parsing (double-quoted)
            try:
                parsed_json = json.loads(val)
                return _normalize(parsed_json)
            except (ValueError, json.JSONDecodeError):
                pass
            # Python literal_eval (single quotes, tuples, lists, dicts)
            if val.startswith(("[", "{", "(")) and val.endswith(("]", "}", ")")):
                try:
                    parsed_literal = ast.literal_eval(val)
                    return _normalize(parsed_literal)
                except (ValueError, SyntaxError):
                    pass
            # Comma-separated string → list (avoid splitting inside quotes)
            # BUT: Don't split if it looks like XML or has < > characters
            if (
                "," in val
                and not (val.startswith('"') or val.startswith("'"))
                and "<" not in val
            ):
                parts = [p.strip() for p in val.split(",") if p.strip()]
                if len(parts) > 1:
                    return [_normalize(p) for p in parts]
            # fallback to original string
            return v
        # 2. Handle dict recursively
        elif isinstance(v, dict):
            return {k: _normalize(val) for k, val in v.items()}
        # 3. Handle list recursively
        elif isinstance(v, list):
            return [_normalize(i) for i in v]
        # 4. Handle tuple recursively
        elif isinstance(v, tuple):
            return tuple(_normalize(i) for i in v)
        # 5. Other types: leave as-is
        return v

    return _normalize(value)


def get_mac_address() -> str:
    """Get the MAC address of the client machine.

    Returns:
        str: The MAC address as a string, or a fallback UUID if MAC address cannot be determined.
    """
    try:
        if platform.system() == "Linux":
            # Try to get MAC address from /sys/class/net/
            for interface in ["eth0", "wlan0", "en0"]:
                try:
                    with open(f"/sys/class/net/{interface}/address") as f:
                        mac = f.read().strip()
                        if mac:
                            return mac
                except FileNotFoundError:
                    continue

            # Fallback to using ip command
            result = subprocess.run(
                ["ip", "link", "show"], capture_output=True, text=True
            )
            for line in result.stdout.split("\n"):
                if "link/ether" in line:
                    return line.split("link/ether")[1].split()[0]

        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(["ifconfig"], capture_output=True, text=True)
            for line in result.stdout.split("\n"):
                if "ether" in line:
                    return line.split("ether")[1].split()[0]

        elif platform.system() == "Windows":
            result = subprocess.run(["getmac"], capture_output=True, text=True)
            for line in result.stdout.split("\n"):
                if ":" in line and "-" in line:  # Look for MAC address format
                    return line.split()[0]

    except Exception as e:
        logger.warning(f"Could not get MAC address: {e}")

    # If all else fails, generate a UUID
    return str(uuid.uuid4())


def build_xml_observations_block(tools_results):
    if not tools_results:
        return "<observations></observations>"

    lines = ["<observations>"]
    tool_counter = defaultdict(int)

    for result in tools_results:
        tool_name = str(result.get("tool_name", "unknown_tool"))
        tool_counter[tool_name] += 1
        unique_id = f"{tool_name}#{tool_counter[tool_name]}"

        output_value = result.get("data") or result.get("message") or "No output"
        if isinstance(output_value, (dict, list)):
            output_str = json.dumps(output_value, separators=(",", ":"))
        else:
            output_str = str(output_value)

        safe_output = escape(output_str, quote=False)
        lines.append(
            f'  <observation tool_name="{unique_id}">{safe_output}</observation>'
        )

    lines.append("</observations>")
    return "\n".join(lines)


# Create a global instance of the MAC address
CLIENT_MAC_ADDRESS = get_mac_address()

# Opik integration for tracing, logging, and observability
OPIK_AVAILABLE = False
track = None

try:
    api_key = decouple_config("OPIK_API_KEY", default=None)
    workspace = decouple_config("OPIK_WORKSPACE", default=None)

    if api_key and workspace:
        from opik import track as opik_track

        OPIK_AVAILABLE = True
        track = opik_track
        logger.debug("Opik imported successfully with valid credentials")
    else:
        logger.debug("Opik available but no valid credentials - using fake decorator")

        # Create fake decorator when no credentials - must handle both @track and @track("name")
        def track(name_or_func=None):
            if callable(name_or_func):
                # Called as @track (function passed directly)
                return name_or_func
            else:
                # Called as @track("name") - return decorator function
                def decorator(func):
                    return func

                return decorator

            return decorator

            return decorator
except ImportError:
    # No-op decorator if Opik is not available
    def track(name_or_func=None):
        if callable(name_or_func):
            # Called as @track (function passed directly)
            return name_or_func
        else:
            # Called as @track("name") - return decorator function
            def decorator(func):
                return func

            return decorator

    logger.debug("Opik not available, using no-op decorator")
