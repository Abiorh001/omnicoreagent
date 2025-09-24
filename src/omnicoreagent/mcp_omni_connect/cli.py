import json
from enum import Enum
from typing import Any
from pprint import pformat
from pathlib import Path
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.align import Align
from omnicoreagent.core.events.event_router import EventRouter
from omnicoreagent.core.memory_store.memory_router import MemoryRouter
from omnicoreagent.core.agents.orchestrator import OrchestratorAgent
from omnicoreagent.core.agents.react_agent import ReactAgent
from omnicoreagent.core.agents.tool_calling_agent import ToolCallingAgent
from omnicoreagent.core.agents.types import AgentConfig
from omnicoreagent.mcp_omni_connect.client import MCPClient
from omnicoreagent.core.constants import AGENTS_REGISTRY, date_time_func
from omnicoreagent.core.llm import LLMConnection
from omnicoreagent.core.llm_support import LLMToolSupport
from omnicoreagent.mcp_omni_connect.prompts import (
    get_prompt,
    get_prompt_with_react_agent,
    list_prompts,
)
from omnicoreagent.mcp_omni_connect.refresh_server_capabilities import (
    refresh_capabilities,
)
from omnicoreagent.mcp_omni_connect.resources import (
    list_resources,
    read_resource,
    subscribe_resource,
    unsubscribe_resource,
)
from omnicoreagent.core.system_prompts import (
    generate_orchestrator_prompt_template,
    generate_react_agent_prompt,
    generate_react_agent_role_prompt,
    generate_system_prompt,
)
from omnicoreagent.mcp_omni_connect.tools import list_tools
from omnicoreagent.core.utils import (
    CLIENT_MAC_ADDRESS,
    logger,
    format_timestamp,
    ensure_agent_registry,
)
from omnicoreagent.core.tools.semantic_tools import SemanticToolManager


CLIENT_MAC_ADDRESS = CLIENT_MAC_ADDRESS.replace(":", "_")


class CommandType(Enum):
    """Command types for the MCP client"""

    HELP = "help"
    QUERY = "query"
    DEBUG = "debug"
    REFRESH = "refresh"
    TOOLS = "tools"
    RESOURCES = "resources"
    RESOURCE = "resource"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PROMPTS = "prompts"
    PROMPT = "prompt"
    HISTORY = "history"
    CLEAR_HISTORY = "clear_history"
    SAVE_HISTORY = "save_history"
    LOAD_HISTORY = "load_history"

    MEMORY_STORE = "memory_store"
    EVENT_STORE = "event_store"
    MODE = "mode"
    QUIT = "quit"
    API_STATS = "api_stats"
    ADD_SERVERS = "add_servers"
    REMOVE_SERVER = "remove_server"
    MEMORY_MODE = "memory_mode"


class CommandHelp:
    """Help documentation for CLI commands"""

    @staticmethod
    def get_command_help(command_type: str) -> dict[str, Any]:
        """Get detailed help for a specific command type"""
        help_docs = {
            "add_servers": {
                "description": "Add one or more MCP servers from a JSON config file",
                "usage": "/add_servers:<path_to_config.json>",
                "examples": [
                    "/add_servers:config.json  # Add servers from config",
                    "/add_servers:/etc/mcp/servers.json",
                ],
                "subcommands": {},
                "tips": [
                    "Make sure the config JSON has valid MCP server definitions",
                    "Supports adding multiple servers at once",
                ],
            },
            "remove_server": {
                "description": "Remove and disconnect a specific MCP server",
                "usage": "/remove_server:<server_name>",
                "examples": [
                    "/remove_server:mcp-yahoo-finance  # Remove a specific server",
                ],
                "subcommands": {},
                "tips": [
                    "Only remove servers you're not actively using",
                    "This disconnects the session and frees up resources",
                ],
            },
            "mode": {
                "description": "Toggle between auto and chat mode",
                "usage": "/mode:<auto|chat|orchestrator>",
                "examples": [
                    "/mode:auto  # Toggle to auto mode",
                    "/mode:chat  # Toggle to chat mode",
                    "/mode:orchestrator  # Toggle to orchestrator mode",
                ],
                "subcommands": {},
                "tips": [
                    "Use to toggle between auto and chat mode",
                    "Use to toggle to orchestrator mode",
                ],
            },
            "memory_store": {
                "description": "Switch between different memory store backends",
                "usage": "/memory_store:<backend>[:<database_url>]",
                "examples": [
                    "/memory_store:in_memory  # Use in-memory storage",
                    "/memory_store:redis  # Use Redis storage",
                    "/memory_store:database  # Use database storage (defaults to SQLite)",
                    "/memory_store:database:postgresql://user:pass@localhost/db  # Use PostgreSQL",
                ],
                "subcommands": {
                    "in_memory": {
                        "description": "Fast in-memory storage (default)",
                        "usage": "/memory_store:in_memory",
                        "examples": ["/memory_store:in_memory"],
                        "tips": ["Best for development and testing"],
                    },
                    "redis": {
                        "description": "Redis-based persistent storage",
                        "usage": "/memory_store:redis",
                        "examples": ["/memory_store:redis"],
                        "tips": ["Requires Redis server running"],
                    },
                    "database": {
                        "description": "Database-based persistent storage",
                        "usage": "/memory_store:database[:<database_url>]",
                        "examples": [
                            "/memory_store:database  # Use SQLite (default)",
                            "/memory_store:database:postgresql://user:pass@localhost/db",
                        ],
                        "tips": ["Uses SQLite by default if no URL provided."],
                    },
                },
                "tips": [
                    "Choose based on your persistence and performance needs",
                    "Database backend supports PostgreSQL, MySQL, SQLite",
                    "Redis provides fast in-memory persistence",
                    "In-memory is fastest but loses data on restart",
                ],
            },
            "event_store": {
                "description": "Switch between different event store backends",
                "usage": "/event_store:<backend>",
                "examples": [
                    "/event_store:in_memory  # Use in-memory event storage",
                    "/event_store:redis_stream  # Use Redis Streams",
                ],
                "subcommands": {
                    "in_memory": {
                        "description": "Fast in-memory event storage (default)",
                        "usage": "/event_store:in_memory",
                        "examples": ["/event_store:in_memory"],
                        "tips": ["Best for development and testing"],
                    },
                    "redis_stream": {
                        "description": "Redis Streams for persistent event storage",
                        "usage": "/event_store:redis_stream",
                        "examples": ["/event_store:redis_stream"],
                        "tips": ["Requires Redis server running"],
                    },
                },
                "tips": [
                    "Event stores handle real-time event streaming",
                    "Redis Streams provide persistent event storage",
                    "In-memory is fastest but loses events on restart",
                ],
            },
            "memory_mode": {
                "description": "Switch short-term memory strategy for the agent",
                "usage": "/memory_mode[:<mode>[:<value>]]",
                "examples": [
                    "/memory_mode:sliding_window:5  # Keep last 5 messages",
                    "/memory_mode:token_budget:3000  # Keep messages under 3000 tokens",
                ],
                "subcommands": {
                    "sliding_window": {
                        "description": "Use fixed-size message window",
                        "usage": "/memory_mode:sliding_window:<N>",
                        "examples": ["/memory_mode:sliding_window:10"],
                        "tips": [
                            "Best for short conversations or minimal context carryover."
                        ],
                    },
                    "token_budget": {
                        "description": "Keep messages under token limit",
                        "usage": "/memory_mode:token_budget:<max_tokens>",
                        "examples": ["/memory_mode:token_budget:4000"],
                        "tips": ["Useful when managing LLM input length across tools."],
                    },
                },
                "tips": [
                    "Choose a memory strategy based on how you want agents to retain context.",
                ],
            },
            "tools": {
                "description": "List and manage available tools across all connected servers",
                "usage": "/tools",
                "examples": ["/tools  # List all available tools"],
                "subcommands": {},
                "tips": [
                    "Tools are automatically discovered from connected servers",
                    "Use /debug to see more detailed tool information",
                    "Tools can be chained together for complex operations",
                ],
            },
            "prompts": {
                "description": "List and manage available prompts",
                "usage": "/prompts",
                "examples": ["/prompts  # List all available prompts"],
                "subcommands": {},
                "tips": [
                    "Prompts are discovered dynamically from servers",
                    "Each prompt may have different argument requirements",
                    "Use /help:prompt for detailed prompt usage",
                ],
            },
            "prompt": {
                "description": "Execute a specific prompt with arguments",
                "usage": "/prompt:<name>/<arguments>",
                "examples": [
                    "/prompt:weather/location=tokyo",
                    '/prompt:analyze/{"data":"sample","type":"full"}',
                    "/prompt:search/query=test/limit=10",
                ],
                "subcommands": {},
                "tips": [
                    "Arguments can be provided in key=value format",
                    "Complex arguments can use JSON format",
                    "Use /prompts to see available prompts",
                    "Arguments are validated before execution",
                    "If a prompt does not have arguments, you can just use /prompt:<name>",
                ],
            },
            "resources": {
                "description": "List available resources across all servers",
                "usage": "/resources",
                "examples": ["/resources  # List all available resources"],
                "subcommands": {},
                "tips": [
                    "Resources are discovered from all connected servers",
                    "Use /resource:<uri> to access specific resources",
                    "Resources can be files, APIs, or other data sources",
                ],
            },
            "resource": {
                "description": "Access and analyze a specific resource",
                "usage": "/resource:<uri>",
                "examples": [
                    "/resource:file:///path/to/file",
                    "/resource:http://api.example.com/data",
                ],
                "subcommands": {},
                "tips": [
                    "URIs can be files, URLs, or other resource identifiers",
                    "Resources are automatically parsed based on type",
                    "Content is formatted for easy reading",
                ],
            },
            "debug": {
                "description": "Toggle debug mode for detailed information",
                "usage": "/debug",
                "examples": ["/debug  # Toggle debug mode on/off"],
                "subcommands": {},
                "tips": [
                    "Debug mode shows additional information",
                    "Useful for troubleshooting issues",
                    "Shows detailed server responses",
                ],
            },
            "refresh": {
                "description": "Refresh server capabilities and connections",
                "usage": "/refresh",
                "examples": ["/refresh  # Refresh all server connections"],
                "subcommands": {},
                "tips": [
                    "Use when adding new servers",
                    "Updates tool and prompt listings",
                    "Reconnects to disconnected servers",
                ],
            },
            "help": {
                "description": "Get help on available commands",
                "usage": "/help or /help:<command>",
                "examples": [
                    "/help  # Show all commands",
                    "/help:prompt  # Show prompt help",
                    "/help:tools  # Show tools help",
                ],
                "subcommands": {},
                "tips": [
                    "Use /help for general overview",
                    "Get detailed help with /help:<command>",
                    "Examples show common usage patterns",
                ],
            },
            "history": {
                "description": "Show the message history",
                "usage": "/history",
                "examples": ["/history  # Show the message history"],
                "subcommands": {},
                "tips": ["Use to see the message history"],
            },
            "clear_history": {
                "description": "Clear the message history",
                "usage": "/clear_history",
                "examples": ["/clear_history  # Clear the message history"],
                "subcommands": {},
                "tips": ["Use to clear the message history"],
            },
            "save_history": {
                "description": "Save the message history to a file",
                "usage": "/save_history:path/to/file",
                "examples": [
                    "/save_history:path/to/file  # Save the message history to a file"
                ],
                "subcommands": {},
                "tips": ["Use to save the message history to a file"],
            },
            "load_history": {
                "description": "Load the message history from a file",
                "usage": "/load_history:path/to/file",
                "examples": [
                    "/load_history:path/to/file  # Load the message history from a file"
                ],
                "subcommands": {},
                "tips": ["Use to load the message history from a file"],
            },
            "subscribe": {
                "description": "Subscribe to a resource",
                "usage": "/subscribe:/resource:<uri>",
                "examples": [
                    "/subscribe:/resource:http://api.example.com/data  # Subscribe to a resource"
                ],
                "subcommands": {},
                "tips": ["Use to subscribe to a resource"],
            },
            "unsubscribe": {
                "description": "Unsubscribe from a resource",
                "usage": "/unsubscribe:/resource:<uri>",
                "examples": [
                    "/unsubscribe:/resource:http://api.example.com/data  # Unsubscribe from a resource"
                ],
                "subcommands": {},
                "tips": ["Use to unsubscribe from a resource"],
            },
        }
        return help_docs.get(command_type, {})


class MCPClientCLI:
    def __init__(self, client: MCPClient, llm_connection: LLMConnection):
        self.client = client
        self.llm_connection = llm_connection

        # Use the already-loaded configuration from LLMConnection to avoid duplication
        if llm_connection is None:
            raise ValueError(
                "LLM connection is required but not available. Please check your LLM configuration."
            )

        config = llm_connection.get_loaded_config()
        self.agent_config = config["AgentConfig"]
        self.MAX_CONTEXT_TOKENS = config["LLM"]["max_context_length"]
        self.MODE = {"auto": False, "chat": True, "orchestrator": False}

        # Initialize MemoryRouter and EventRouter
        self.memory_router = MemoryRouter(memory_store_type="in_memory")
        self.event_router = EventRouter(event_store_type="in_memory")

        # Set memory config
        self.memory_router.set_memory_config(
            mode=self.agent_config.get("memory_config", {}).get("mode", "token_budget"),
            value=self.agent_config.get("memory_config", {}).get("value", 32000),
        )

        self.console = Console()
        self.command_help = CommandHelp()

    async def async_init(self):
        # also connect all the tools to the tools knowledge base if it's enabled
        enable_tools_knowledge_base = self.agent_config.get(
            "enable_tools_knowledge_base", False
        )
        if enable_tools_knowledge_base:
            llm_connection = self.llm_connection
            store_tool = self.memory_router.store_tool
            tool_exists = self.memory_router.tool_exists
            mcp_tools = self.client.available_tools

            semantic_tools_manager = SemanticToolManager(llm_connection=llm_connection)

            await semantic_tools_manager.batch_process_all_mcp_servers(
                mcp_tools=mcp_tools,
                store_tool=store_tool,
                tool_exists=tool_exists,
            )

    def parse_command(self, input_text: str) -> tuple[CommandType, str]:
        """Parse input to determine command type and payload"""
        input_text = input_text.strip().lower()

        if input_text == "quit":
            return CommandType.QUIT, ""
        elif input_text == "/debug":
            return CommandType.DEBUG, ""
        elif input_text == "/refresh":
            return CommandType.REFRESH, ""
        elif input_text == "/help":
            return CommandType.HELP, ""
        elif input_text.startswith("/help:"):
            return CommandType.HELP, input_text[6:].strip()
        elif input_text == "/tools":
            return CommandType.TOOLS, ""
        elif input_text == "/resources":
            return CommandType.RESOURCES, ""
        elif input_text == "/prompts":
            return CommandType.PROMPTS, ""
        elif input_text.startswith("/resource:"):
            return CommandType.RESOURCE, input_text[10:].strip()
        elif input_text.startswith("/subscribe:"):
            return CommandType.SUBSCRIBE, input_text[11:].strip()
        elif input_text.startswith("/unsubscribe:"):
            return CommandType.UNSUBSCRIBE, input_text[13:].strip()
        elif input_text.startswith("/prompt:"):
            return CommandType.PROMPT, input_text[8:].strip()
        elif input_text == "/history":
            return CommandType.HISTORY, ""
        elif input_text == "/clear_history":
            return CommandType.CLEAR_HISTORY, ""
        elif input_text.startswith("/save_history:"):
            return CommandType.SAVE_HISTORY, input_text[14:].strip()
        elif input_text.startswith("/load_history:"):
            return CommandType.LOAD_HISTORY, input_text[14:].strip()

        elif input_text.startswith("/memory_store:"):
            return CommandType.MEMORY_STORE, input_text[14:].strip()
        elif input_text.startswith("/event_store:"):
            return CommandType.EVENT_STORE, input_text[13:].strip()
        elif input_text.startswith("/mode:"):
            return CommandType.MODE, input_text[6:].strip()
        elif input_text.startswith("/add_servers:"):
            return CommandType.ADD_SERVERS, input_text[13:].strip()
        elif input_text.startswith("/remove_server:"):
            return CommandType.REMOVE_SERVER, input_text[15:].strip()
        elif input_text.startswith("/memory_mode:"):
            return CommandType.MEMORY_MODE, input_text[13:].strip()
        elif input_text == "/api_stats":
            return CommandType.API_STATS, ""
        else:
            if input_text:
                return CommandType.QUERY, input_text
            else:
                return None, None

    async def handle_debug_command(self, input_text: str = ""):
        """Handle debug toggle command"""
        self.client.debug = not self.client.debug
        self.console.print(
            f"[{'green' if self.client.debug else 'red'}]Debug mode "
            f"{'enabled' if self.client.debug else 'disabled'}[/]"
        )

    async def handle_add_servers(self, input_text: str):
        """Handle add new server or list of servers"""
        config_path = Path(input_text.strip()).expanduser().resolve()
        if not config_path.exists() or not config_path.is_file():
            self.console.print(f"[red]Config file not found: {config_path}[/red]")
            return
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Adding Servers...", total=None)
            try:
                response = await self.client.add_servers(config_file=config_path)
            except Exception as e:
                self.console.print(f"[red]Failed to add servers: {e}[/red]")
                return
        if not response:
            self.console.print(
                "[yellow]No response from server addition process.[/yellow]"
            )
            return
        if isinstance(response, (list, dict)):
            self.console.print(Panel(pformat(response), border_style="blue"))
        else:
            self.console.print(Panel(str(response), border_style="blue"))

    async def handle_remove_server(self, input_text: str):
        """Handle remove server"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Removing Server...", total=None)
            response = await self.client.remove_server(name=input_text)
        if not response:
            self.console.print(
                "[yellow]No response from server removing process.[/yellow]"
            )
            return
        self.console.print(Panel(str(response), border_style="blue"))

    async def handle_api_stats(self, input_text: str = ""):
        """handle api stats"""
        from omnicoreagent.core.agents.token_usage import session_stats

        stats = session_stats
        stats_content = f"""
[bold cyan]API Call Stats for Current Session:[/]

[bold green]Request Tokens:[/] {stats["request_tokens"]}
[bold green]Response Tokens:[/] {stats["response_tokens"]}
[bold green]Total Tokens:[/] {stats["total_tokens"]}

[bold yellow]Remaining Requests:[/] {stats["remaining_requests"]}
[bold yellow]Remaining Tokens:[/] {stats["remaining_tokens"]}
            """
        stats_box = Panel(
            stats_content,
            title="API Stats",
            style="bold cyan",
            border_style="bright_magenta",
            padding=(1, 2),
        )
        self.console.print(stats_box)

    async def handle_memory_store_command(self, input_text: str):
        """Handle memory store switching command"""
        try:
            if ":" in input_text:
                store_type, db_url = input_text.split(":", 1)
            else:
                store_type = input_text.strip()
                db_url = None

            store_type = store_type.strip().lower()

            if store_type == "database" and not db_url:
                db_url = "sqlite:///mcpomni_memory.db"

            # Create new memory router with specified store type
            if store_type == "database":
                self.memory_router = MemoryRouter(memory_store_type="database")
                if db_url:
                    # Update database URL if provided
                    self.memory_router.memory_store.db_url = db_url
            else:
                self.memory_router = MemoryRouter(memory_store_type=store_type)

            # Set memory config
            self.memory_router.set_memory_config(
                mode=self.agent_config.get("memory_config", {}).get(
                    "mode", "token_budget"
                ),
                value=self.agent_config.get("memory_config", {}).get("value", 10000),
            )

            store_info = self.memory_router.get_memory_store_info()
            self.console.print(
                f"[green]Memory store switched to: {store_type}[/green]\n"
                f"[dim]Store info: {store_info}[/dim]"
            )

        except Exception as e:
            self.console.print(f"[red]Failed to switch memory store: {e}[/red]")

    async def handle_event_store_command(self, input_text: str):
        """Handle event store switching command"""
        try:
            store_type = input_text.strip().lower()

            # Switch event store
            self.event_router.switch_event_store(store_type)

            store_info = self.event_router.get_event_store_info()
            self.console.print(
                f"[green]Event store switched to: {store_type}[/green]\n"
                f"[dim]Store info: {store_info}[/dim]"
            )

        except Exception as e:
            self.console.print(f"[red]Failed to switch event store: {e}[/red]")

    async def handle_memory_mode_command(self, input_text: str):
        """Handle memory mode command."""
        try:
            if ":" in input_text:
                mode, value = input_text.split(":", 1)
                value = int(value.strip()) if value.strip().isdigit() else None
            else:
                mode = input_text.strip()
                value = None

            self.memory_router.set_memory_config(mode=mode.strip(), value=value)

            value_str = f" with value {value}" if value is not None else ""
            self.console.print(
                f"[green]Memory mode set to '{mode}'{value_str}.[/green]"
            )

        except ValueError as ve:
            self.console.print(f"[red]Invalid input: {ve}[/red]")
        except Exception as e:
            self.console.print(f"[red]Failed to set memory mode: {e}[/red]")

    async def handle_mode_command(self, mode: str) -> str:
        """Handle mode switching command."""
        if mode.lower() == "chat":
            self.MODE["chat"] = True
            self.MODE["auto"] = False
            self.MODE["orchestrator"] = False
            self.console.print(
                "[green]Switched to Chat Mode - Direct model interaction[/]"
            )
        elif mode.lower() == "auto":
            self.MODE["auto"] = True
            self.MODE["chat"] = False
            self.MODE["orchestrator"] = False
            self.console.print(
                "[green]Switched to Auto Mode - Using ReAct Agent for tool execution[/]"
            )
        elif mode.lower() == "orchestrator":
            # ensure the agent registry is up to date before using the orchestrator mode
            self.console.print("[green]Switching to Orchestrator Mode...[/]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
                console=self.console,
            ) as progress:
                task = progress.add_task("Generating agent registry...", start=False)
                progress.start_task(task)
                updated_registry = await ensure_agent_registry(
                    available_tools=self.client.available_tools,
                    llm_connection=self.llm_connection,
                )
            self.MODE["orchestrator"] = True
            self.MODE["auto"] = False
            self.MODE["chat"] = False

            if updated_registry:
                self.console.print(
                    f"[green]Switched to Orchestrator Mode - Coordinating multiple tools and agents[/]"
                )
                for server, _ in updated_registry.items():
                    self.console.print(f"[blue]Server {server} registry updated[/]")
            else:
                self.console.print("[yellow]No agent registry entries generated[/]")

        else:
            self.console.print(
                "[red]Invalid mode. Available modes: chat, auto, orchestrator[/]"
            )

    async def handle_refresh_command(self, input_text: str = ""):
        """Handle refresh capabilities command"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Refreshing capabilities...", total=None)
            await refresh_capabilities(
                sessions=self.client.sessions,
                server_names=self.client.server_names,
                available_tools=self.client.available_tools,
                available_resources=self.client.available_resources,
                available_prompts=self.client.available_prompts,
                debug=self.client.debug,
                llm_connection=self.client.llm_connection,
                generate_react_agent_role_prompt=generate_react_agent_role_prompt,
            )
        self.console.print("[green]Capabilities refreshed successfully[/]")

    async def handle_help_command(self, command_type: str | None = None):
        """Show help information for commands"""
        if command_type:
            # Show specific command help
            help_info = self.command_help.get_command_help(command_type.lower())
            if help_info:
                panel = Panel(
                    f"[bold cyan]{command_type.upper()}[/]\n\n"
                    f"[bold white]Description:[/]\n{help_info['description']}\n\n"
                    f"[bold white]Usage:[/]\n{help_info['usage']}\n\n"
                    f"[bold white]Examples:[/]\n"
                    + "\n".join(help_info["examples"])
                    + "\n\n"
                    "[bold white]Tips:[/]\n"
                    + "\n".join(f"• {tip}" for tip in help_info["tips"]),
                    title="[bold blue]Command Help[/]",
                    border_style="blue",
                )
                self.console.print(panel)
            else:
                self.console.print(
                    f"[red]No help available for command: {command_type}[/]"
                )
        else:
            # Show general help with all commands
            help_table = Table(
                title="[bold blue]Available Commands[/]",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan",
            )
            help_table.add_column("Command", style="cyan")
            help_table.add_column("Description", style="white")
            help_table.add_column("Usage", style="green")

            for cmd_type in CommandType:
                help_info = self.command_help.get_command_help(cmd_type.value)
                if help_info:
                    help_table.add_row(
                        f"/{cmd_type.value}",
                        help_info["description"],
                        help_info["usage"],
                    )

            self.console.print(help_table)

            # Show general tips
            tips_panel = Panel(
                "• Use [cyan]/help:<command>[/] for detailed help on specific commands\n"
                "• Commands are case-insensitive\n"
                "• Use [cyan]quit[/] to exit the application\n"
                "• Enable debug mode with [cyan]/debug[/] for more information",
                title="[bold yellow]💡 Tips[/]",
                border_style="yellow",
            )
            self.console.print(tips_panel)

    async def handle_tools_command(self, input_text: str = ""):
        """Handle tools listing command"""
        tools = await list_tools(
            server_names=self.client.server_names,
            sessions=self.client.sessions,
        )
        tools_table = Table(title="Available Tools", box=box.ROUNDED)
        tools_table.add_column("Tool", style="cyan", no_wrap=False)
        tools_table.add_column("Description", style="green", no_wrap=False)

        for tool in tools:
            tools_table.add_row(
                tool.name, tool.description or "No description available"
            )
        self.console.print(tools_table)

    async def handle_resources_command(self, input_text: str = ""):
        """Handle resources listing command"""
        resources = await list_resources(
            server_names=self.client.server_names,
            sessions=self.client.sessions,
        )
        resources_table = Table(title="Available Resources", box=box.ROUNDED)
        resources_table.add_column("URI", style="cyan", no_wrap=False)
        resources_table.add_column("Name", style="blue")
        resources_table.add_column("Description", style="green", no_wrap=False)

        for resource in resources:
            resources_table.add_row(
                str(resource.uri),
                resource.name,
                resource.description or "No description available",
            )
        self.console.print(resources_table)

    async def handle_prompts_command(self, input_text: str = ""):
        """Handle prompts listing command"""
        prompts = await list_prompts(
            server_names=self.client.server_names,
            sessions=self.client.sessions,
        )
        prompts_table = Table(title="Available Prompts", box=box.ROUNDED)
        prompts_table.add_column("Name", style="cyan", no_wrap=False)
        prompts_table.add_column("Description", style="blue")
        prompts_table.add_column("Arguments", style="green")

        if not prompts:
            self.console.print("[yellow]No prompts available[/yellow]")
            return

        for prompt in prompts:
            # Safely handle None values and ensure string conversion
            name = (
                str(prompt.name)
                if hasattr(prompt, "name") and prompt.name
                else "Unnamed Prompt"
            )
            description = (
                str(prompt.description)
                if hasattr(prompt, "description") and prompt.description
                else "No description available"
            )
            arguments = prompt.arguments
            arguments_str = ""
            if hasattr(prompt, "arguments") and prompt.arguments:
                for arg in arguments:
                    arg_name = arg.name
                    arg_description = arg.description
                    required = arg.required
                    arguments_str += f"{arg_name}: {arg_description} ({'required' if required else 'optional'})\n"
            else:
                arguments_str = "No arguments available"

            prompts_table.add_row(name, description, arguments_str)

        self.console.print(prompts_table)

    async def handle_resource_command(self, uri: str):
        """Handle resource reading command"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Loading resource...", total=None)
            # Use LLM call if available, otherwise provide a no-op function
            llm_call_func = (
                self.llm_connection.llm_call if self.llm_connection else None
            )
            content = await read_resource(
                uri=uri,
                sessions=self.client.sessions,
                available_resources=self.client.available_resources,
                llm_call=llm_call_func,
                debug=self.client.debug,
                request_limit=self.agent_config["request_limit"],
                total_tokens_limit=self.agent_config["total_tokens_limit"],
            )

        if content.startswith("```") or content.startswith("#"):
            self.console.print(Markdown(content))
        else:
            self.console.print(Panel(content, title=uri, border_style="blue"))

    async def handle_subscribe(self, input_text: str):
        """Handle subscribe command"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Subscribing to resource...", total=None)
            if input_text.startswith("/resource:"):
                uri = input_text[10:].strip()
                content = await subscribe_resource(
                    sessions=self.client.sessions,
                    uri=uri,
                    available_resources=self.client.available_resources,
                )

        if content.startswith("```") or content.startswith("#"):
            self.console.print(Markdown(content))
        else:
            self.console.print(Panel(content, title=uri, border_style="blue"))

    async def handle_unsubscribe(self, input_text: str):
        """Handle unsubscribe command"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Unsubscribing from resource...", total=None)
            if input_text.startswith("/resource:"):
                uri = input_text[10:].strip()
                content = await unsubscribe_resource(
                    sessions=self.client.sessions,
                    uri=uri,
                    available_resources=self.client.available_resources,
                )

        if content.startswith("```") or content.startswith("#"):
            self.console.print(Markdown(content))
        else:
            self.console.print(Panel(content, title=uri, border_style="blue"))

    async def handle_prompt_command(self, input_text: str):
        """Handle prompt reading command"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task("Loading prompt...", total=None)
            name, arguments = self.parse_prompt_command(input_text)

            # Check if current LLM supports tools
            supported_tools = False
            if self.llm_connection and self.llm_connection.llm_config:
                supported_tools = LLMToolSupport.check_tool_support(
                    self.llm_connection.llm_config
                )

            if supported_tools:
                # Generate system prompt for tool-supporting LLMs
                system_prompt = generate_system_prompt(
                    current_date_time=date_time_func["format_date"](),
                    available_tools=self.client.available_tools,
                    llm_connection=self.llm_connection,
                )
                # Use LLM call if available
                llm_call_func = (
                    self.llm_connection.llm_call if self.llm_connection else None
                )
                content = await get_prompt(
                    sessions=self.client.sessions,
                    system_prompt=system_prompt,
                    llm_call=llm_call_func,
                    add_message_to_history=self.memory_router.store_message,
                    debug=self.client.debug,
                    available_prompts=self.client.available_prompts,
                    name=name,
                    arguments=arguments,
                    request_limit=self.agent_config["request_limit"],
                    total_tokens_limit=self.agent_config["total_tokens_limit"],
                    session_id=CLIENT_MAC_ADDRESS,
                )
                if content:
                    # Get latest tools
                    tools = await list_tools(
                        server_names=self.client.server_names,
                        sessions=self.client.sessions,
                    )
                    agent_config = AgentConfig(
                        agent_name="tool_calling_agent",
                        tool_call_timeout=self.agent_config.get("tool_call_timeout"),
                        max_steps=self.agent_config.get("max_steps"),
                        request_limit=self.agent_config.get("request_limit"),
                        total_tokens_limit=self.agent_config.get("total_tokens_limit"),
                    )
                    tool_calling_agent = ToolCallingAgent(
                        config=agent_config, debug=self.client.debug
                    )
                    response = await tool_calling_agent.run(
                        query=content,
                        session_id=CLIENT_MAC_ADDRESS,
                        system_prompt=system_prompt,
                        llm_connection=self.llm_connection,
                        sessions=self.client.sessions,
                        server_names=self.client.server_names,
                        tools_list=tools,
                        available_tools=self.client.available_tools,
                        add_message_to_history=(self.memory_router.store_message),
                        message_history=(self.memory_router.get_messages),
                    )
                content = response
            else:
                # Use ReAct agent for LLMs without tool support
                extra_kwargs = {
                    "sessions": self.client.sessions,
                    "mcp_tools": self.client.available_tools,
                    "session_id": CLIENT_MAC_ADDRESS,
                }

                agent_config = AgentConfig(
                    agent_name="react_agent",
                    tool_call_timeout=self.agent_config.get("tool_call_timeout"),
                    max_steps=self.agent_config.get("max_steps"),
                    request_limit=self.agent_config.get("request_limit"),
                    total_tokens_limit=self.agent_config.get("total_tokens_limit"),
                    memory_similarity_threshold=self.agent_config.get(
                        "memory_similarity_threshold", 0.5
                    ),
                    memory_results_limit=self.agent_config.get(
                        "memory_results_limit", 5
                    ),
                    enable_tools_knowledge_base=self.agent_config.get(
                        "enable_tools_knowledge_base", False
                    ),
                    tools_results_limit=self.agent_config.get(
                        "tools_results_limit", 10
                    ),
                    tools_similarity_threshold=self.agent_config.get(
                        "tools_similarity_threshold", 0.5
                    ),
                )
                # Generate ReAct agent prompt
                react_agent_prompt = generate_react_agent_prompt(
                    current_date_time=date_time_func["format_date"]()
                )
                initial_response = await get_prompt_with_react_agent(
                    sessions=self.client.sessions,
                    system_prompt=react_agent_prompt,
                    add_message_to_history=self.memory_router.store_message,
                    debug=self.client.debug,
                    available_prompts=self.client.available_prompts,
                    name=name,
                    arguments=arguments,
                    session_id=CLIENT_MAC_ADDRESS,
                )
                if initial_response:
                    react_agent = ReactAgent(config=agent_config)
                    content = await react_agent._run(
                        system_prompt=react_agent_prompt,
                        query=initial_response,
                        llm_connection=self.llm_connection,
                        add_message_to_history=(self.memory_router.store_message),
                        message_history=(self.memory_router.get_messages),
                        event_router=self.event_router,
                        debug=self.client.debug,
                        **extra_kwargs,
                    )
                else:
                    content = initial_response

        if content.startswith("```") or content.startswith("#"):
            self.console.print(Markdown(content))
        else:
            self.console.print(Panel(content, title=name, border_style="blue"))

    def parse_prompt_command(self, input_text: str) -> tuple[str, dict | None]:
        """Parse prompt command to determine name and arguments.

        Supports multiple formats:
        1. /prompt:name/{key1:value1,key2:value2}  # JSON-like format
        2. /prompt:name/key1=value1/key2=value2    # Key-value pair format
        3. /prompt:name                            # No arguments

        Args:
            input_text: The command text to parse

        Returns:
            Tuple of (prompt_name, arguments_dict)

        Raises:
            ValueError: If the command format is invalid
        """
        input_text = input_text.strip()

        # Split into name and arguments parts
        parts = input_text.split("/", 1)
        name = parts[0].strip()

        if len(parts) == 1:
            return name, None

        args_str = parts[1].strip()

        # Try parsing as JSON-like format first
        if args_str.startswith("{") and args_str.endswith("}"):
            try:
                # Convert single quotes to double quotes for JSON parsing
                args_str = args_str.replace("'", '"')
                arguments = json.loads(args_str)
                # Convert all values to strings
                return name, {k: str(v) for k, v in arguments.items()}
            except json.JSONDecodeError:
                pass

        # Try parsing as key-value pairs
        arguments = {}
        try:
            # Split by / and handle each key-value pair
            for pair in args_str.split("/"):
                if "=" not in pair:
                    raise ValueError(f"Invalid argument format: {pair}")
                key, value = pair.split("=", 1)
                key = key.strip()
                value = value.strip()
                arguments[key] = value

            return name, arguments
        except Exception as e:
            raise ValueError(
                f"Invalid argument format. Use either:\n"
                f"1. /prompt:name/{{key1:value1,key2:value2}}\n"
                f"2. /prompt:name/key1=value1/key2=value2\n"
                f"Error: {str(e)}"
            )

    async def stream_events_to_cli(self, session_id: str):
        """Streams events from event store and displays them in the CLI using Rich, with a live indicator."""

        # Live spinner shown while streaming
        spinner = Spinner("dots", text=" Waiting for agent response...", style="yellow")
        status_panel = Panel(
            Align.center(spinner, vertical="middle"),
            title="[bold yellow]Streaming Events...",
            border_style="yellow",
            padding=(1, 2),
        )

        with Live(status_panel, console=self.console, refresh_per_second=8):
            async for event in self.event_router.stream(session_id):
                event_type = event.type
                payload = event.payload  # This is a Pydantic model
                ts = format_timestamp(event.timestamp)
                agent = event.agent_name or "agent"

                if event_type == "user_message":
                    self.console.print(
                        Panel(
                            payload.message,
                            title=f"[bold blue]{agent} • User Message • {ts}[/bold blue]",
                            border_style="blue",
                        )
                    )

                elif event_type == "agent_message":
                    msg = payload.message
                    self.console.print(
                        Panel(
                            Markdown(msg),
                            title=f"[magenta]{agent} • Agent Message • {ts}[/magenta]",
                            border_style="magenta",
                        )
                    )

                elif event_type == "thought":
                    self.console.print(
                        f"[magenta]{ts} • Thought:[/magenta] {payload.content}"
                    )

                elif event_type == "tool_call_started":
                    self.console.print(
                        f"[cyan]{ts} • Tool Call Started:[/cyan] [bold]{payload.tool_name}[/bold] with args {payload.tool_args}"
                    )

                elif event_type == "tool_call_result":
                    result = payload.result or ""
                    tool_name = payload.tool_name or "unknown_tool"

                    self.console.print(
                        Panel(
                            result.strip(),
                            title=f"[bold cyan]{agent} • Tool Result: {tool_name} • {ts}[/bold cyan]",
                            border_style="cyan",
                        )
                    )

                elif event_type == "final_answer":
                    self.console.rule(f"[bold green]{agent} • Final Answer • {ts}")
                    self.console.print(Markdown(payload.message), style="bold green")
                    break  # End streaming when final answer is received

                elif event_type == "tool_call_error":
                    self.console.print(
                        Panel(
                            payload.error_message or "Unknown error",
                            title=f"[bold red]{agent} • Error • {ts}[/bold red]",
                            border_style="red",
                        )
                    )

                else:
                    self.console.print(f"[dim]{ts} • {event_type}[/dim]: {payload}")

    async def handle_query(self, query: str):
        """Handle general query processing"""
        try:
            # stream_task = asyncio.create_task(
            #     self.stream_events_to_cli(CLIENT_MAC_ADDRESS)
            # )
            if not query or query.isspace():
                return

            # Parse the command first
            cmd_type, payload = self.parse_command(query)
            if not cmd_type:
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task("Processing query...", total=None)

                # Get latest tools
                tools = await list_tools(
                    server_names=self.client.server_names,
                    sessions=self.client.sessions,
                )

                # Check if current LLM supports tools
                supported_tools = LLMToolSupport.check_tool_support(
                    self.llm_connection.llm_config
                )

                # if the LLM supports tools and the mode is chat, use the tool-supporting mode
                if supported_tools and self.MODE["chat"]:
                    # Generate system prompt for tool-supporting LLMs
                    system_prompt = generate_system_prompt(
                        current_date_time=date_time_func["format_date"](),
                        available_tools=self.client.available_tools,
                        llm_connection=self.llm_connection,
                    )
                    agent_config = AgentConfig(
                        agent_name="tool_calling_agent",
                        tool_call_timeout=self.agent_config.get("tool_call_timeout"),
                        max_steps=self.agent_config.get("max_steps"),
                        request_limit=self.agent_config.get("request_limit"),
                        total_tokens_limit=self.agent_config.get("total_tokens_limit"),
                    )
                    tool_calling_agent = ToolCallingAgent(
                        config=agent_config, debug=self.client.debug
                    )
                    response = await tool_calling_agent.run(
                        query=query,
                        session_id=CLIENT_MAC_ADDRESS,
                        system_prompt=system_prompt,
                        llm_connection=self.llm_connection,
                        sessions=self.client.sessions,
                        server_names=self.client.server_names,
                        tools_list=tools,
                        available_tools=self.client.available_tools,
                        add_message_to_history=(self.memory_router.store_message),
                        message_history=(self.memory_router.get_messages),
                        event_router=self.event_router.append,
                    )

                elif self.MODE["auto"]:
                    react_agent_prompt = generate_react_agent_prompt(
                        current_date_time=date_time_func["format_date"](),
                    )
                    extra_kwargs = {
                        "sessions": self.client.sessions,
                        "mcp_tools": self.client.available_tools,
                        "session_id": CLIENT_MAC_ADDRESS,
                    }

                    agent_config = AgentConfig(
                        agent_name="react_agent",
                        tool_call_timeout=self.agent_config.get("tool_call_timeout"),
                        max_steps=self.agent_config.get("max_steps"),
                        request_limit=self.agent_config.get("request_limit"),
                        total_tokens_limit=self.agent_config.get("total_tokens_limit"),
                        memory_similarity_threshold=self.agent_config.get(
                            "memory_similarity_threshold", 0.5
                        ),
                        memory_results_limit=self.agent_config.get(
                            "memory_results_limit", 5
                        ),
                        enable_tools_knowledge_base=self.agent_config.get(
                            "enable_tools_knowledge_base", False
                        ),
                        tools_results_limit=self.agent_config.get(
                            "tools_results_limit", 10
                        ),
                        tools_similarity_threshold=self.agent_config.get(
                            "tools_similarity_threshold", 0.5
                        ),
                    )

                    react_agent = ReactAgent(config=agent_config)
                    response = await react_agent._run(
                        system_prompt=react_agent_prompt,
                        query=query,
                        llm_connection=self.llm_connection,
                        add_message_to_history=(self.memory_router.store_message),
                        message_history=(self.memory_router.get_messages),
                        event_router=self.event_router.append,
                        debug=self.client.debug,
                        **extra_kwargs,
                    )
                elif self.MODE["orchestrator"]:
                    # initialize the orchestrator agent in memory
                    orchestrator_agent_prompt = generate_orchestrator_prompt_template(
                        current_date_time=date_time_func["format_date"]()
                    )
                    agent_config = AgentConfig(
                        agent_name="orchestrator_agent",
                        tool_call_timeout=self.agent_config.get("tool_call_timeout"),
                        max_steps=self.agent_config.get("max_steps"),
                        request_limit=self.agent_config.get("request_limit"),
                        total_tokens_limit=self.agent_config.get("total_tokens_limit"),
                    )
                    orchestrator_agent = OrchestratorAgent(
                        config=agent_config,
                        agents_registry=AGENTS_REGISTRY,
                        current_date_time=date_time_func["format_date"](),
                        debug=self.client.debug,
                    )
                    response = await orchestrator_agent.run(
                        query=query,
                        sessions=self.client.sessions,
                        add_message_to_history=(self.memory_router.store_message),
                        llm_connection=self.llm_connection,
                        mcp_tools=self.client.available_tools,
                        message_history=(self.memory_router.get_messages),
                        event_router=self.event_router.append,
                        orchestrator_system_prompt=orchestrator_agent_prompt,
                        tool_call_timeout=self.agent_config.get("tool_call_timeout"),
                        max_steps=self.agent_config.get("max_steps"),
                        request_limit=self.agent_config.get("request_limit"),
                        total_tokens_limit=self.agent_config.get("total_tokens_limit"),
                        session_id=CLIENT_MAC_ADDRESS,
                    )
                else:
                    response = "Your current model doesn't support function calling. You must use '/mode:auto' to switch to Auto Mode - it works with both function-calling and non-function-calling models, providing seamless tool execution through our ReAct Agent. For advanced tool orchestration, use '/mode:orchestrator'."
            # stream event
            # await stream_task
            if response:  # Only try to print if we have a response
                if "```" in response or "#" in response:
                    self.console.print(Markdown(response))
                else:
                    self.console.print(Panel(response, border_style="green"))
                return response
            else:
                logger.warning("Received empty response from query processing")
                self.console.print(
                    Panel(
                        "[yellow]⚠️  The model didn't generate a response. This could be due to:[/]\n\n"
                        "1. The Maximum number of steps was reached\n"
                        "2. The context might be too long\n"
                        "3. The model might need more specific instructions\n\n"
                        "[bold green]Try these solutions:[/]\n"
                        "• Break down your query into smaller parts\n"
                        "• Be more specific in your request\n"
                        "• Use /clear_history to reset the conversation\n"
                        "• Try rephrasing your question\n\n"
                        "[dim]You can continue with your next query or use /help for more assistance[/]",
                        title="[bold red]No Response Generated[/]",
                        border_style="yellow",
                    )
                )

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            self.console.print(f"[red]Error:[/] {str(e)}", style="bold red")

    async def handle_history_command(self, input_text: str = ""):
        """Handle history command"""
        prompts_table = Table(title="Message History", box=box.ROUNDED)
        prompts_table.add_column("Agent", style="cyan", no_wrap=True)
        prompts_table.add_column("Role", style="magenta")
        prompts_table.add_column("Content", style="white")

        messages = await self.memory_router.get_messages()

        if messages:
            for agent_name, agent_messages in messages.items():
                for message in agent_messages:
                    role = message.get("role", "unknown")
                    content = message.get("content", "")
                    prompts_table.add_row(agent_name, role, content)
        else:
            prompts_table.add_row("No messages", "N/A", "No history available")

        self.console.print(prompts_table)

    async def handle_clear_history_command(self, input_text: str = ""):
        """Handle clear history command"""
        await self.memory_router.clear_memory()
        self.console.print("[green]Message history cleared[/]")

    async def handle_save_history_command(self, input_text: str):
        """Handle save history command"""
        await self.memory_router.save_message_history_to_file(input_text)
        self.console.print(f"[green]Message history saved to {input_text}[/]")

    async def handle_load_history_command(self, input_text: str):
        """Handle load history command"""
        await self.memory_router.load_message_history_from_file(input_text)
        self.console.print(f"[green]Message history loaded from {input_text}[/]")

    async def chat_loop(self):
        """Run an interactive chat loop with rich UI"""
        self.print_welcome_header()

        # Command handlers mapping
        handlers = {
            CommandType.MEMORY_STORE: self.handle_memory_store_command,
            CommandType.EVENT_STORE: self.handle_event_store_command,
            CommandType.DEBUG: self.handle_debug_command,
            CommandType.REFRESH: self.handle_refresh_command,
            CommandType.HELP: self.handle_help_command,
            CommandType.TOOLS: self.handle_tools_command,
            CommandType.RESOURCES: self.handle_resources_command,
            CommandType.RESOURCE: self.handle_resource_command,
            CommandType.QUERY: self.handle_query,
            CommandType.PROMPTS: self.handle_prompts_command,
            CommandType.PROMPT: self.handle_prompt_command,
            CommandType.HISTORY: self.handle_history_command,
            CommandType.CLEAR_HISTORY: self.handle_clear_history_command,
            CommandType.SAVE_HISTORY: self.handle_save_history_command,
            CommandType.SUBSCRIBE: self.handle_subscribe,
            CommandType.UNSUBSCRIBE: self.handle_unsubscribe,
            CommandType.MODE: self.handle_mode_command,
            CommandType.LOAD_HISTORY: self.handle_load_history_command,
            CommandType.API_STATS: self.handle_api_stats,
            CommandType.ADD_SERVERS: self.handle_add_servers,
            CommandType.REMOVE_SERVER: self.handle_remove_server,
            CommandType.MEMORY_MODE: self.handle_memory_mode_command,
        }

        while True:
            try:
                query = Prompt.ask("\n[bold blue]Query[/]").strip()
                # get the command type and payload from the query
                command_type, payload = self.parse_command(query)

                if command_type == CommandType.QUIT:
                    break

                # get the handler for the command type from the handlers mapping
                handler = handlers.get(command_type)
                if handler:
                    await handler(payload)
            except KeyboardInterrupt:
                self.console.print("[yellow]Shutting down client...[/]", style="yellow")
                break
            except Exception as e:
                self.console.print(f"[red]Error:[/] {str(e)}", style="bold red")

        # Shutdown message
        self.console.print(
            Panel(
                "[yellow]Shutting down client...[/]",
                border_style="yellow",
                box=box.DOUBLE,
            )
        )

    def print_welcome_header(self):
        ascii_art = """[bold blue]
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║  ███╗   ███╗ ██████╗██████╗     ██████╗ ███╗   ███╗███╗   ██╗██╗       ║
    ║  ████╗ ████║██╔════╝██╔══██╗   ██╔═══██╗████╗ ████║████╗  ██║██║       ║
    ║  ██╔████╔██║██║     ██████╔╝   ██║   ██║██╔████╔██║██╔██╗ ██║██║       ║
    ║  ██║╚██╔╝██║██║     ██╔═══╝    ██║   ██║██║╚██╔╝██║██║╚██╗██║██║       ║
    ║  ██║ ╚═╝ ██║╚██████╗██║        ╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║       ║
    ║  ╚═╝     ╚═╝ ╚═════╝╚═╝         ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝       ║
    ║                                                                           ║
    ║     [cyan]Model[/] · [cyan]Context[/] · [cyan]Protocol[/]  →  [green]OMNI CONNECT[/]              ║
    ╚═══════════════════════════════════════════════════════════════════════════╝[/]
    """

        # Server status with emojis and cool styling
        server_status = [
            f"[bold green]●[/] [cyan]{name}[/]" for name in self.client.server_names
        ]

        content = f"""
{ascii_art}

[bold magenta]🚀 Universal MCP Client[/]

[bold white]Connected Servers:[/]
{" | ".join(server_status)}

[dim]▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰[/]
[cyan]Your Universal Gateway to MCP Servers[/]
[dim]▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰[/]
"""

        # Add some flair with a fancy border
        self.console.print(
            Panel(
                content,
                title="[bold blue]⚡ MCPOmni Connect ⚡[/]",
                subtitle="[bold cyan]v0.2.4[/]",
                border_style="blue",
                box=box.DOUBLE_EDGE,
            )
        )

        # Command list with emojis and better styling
        commands_table = Table(
            title="[bold magenta]Available Commands[/]",
            box=box.SIMPLE_HEAD,
            border_style="bright_blue",
        )
        commands_table.add_column("[bold cyan]Command[/]", style="cyan")
        commands_table.add_column("[bold green]Description[/]", style="green")
        commands_table.add_column("[bold yellow]Example[/]", style="yellow")

        commands = [
            (
                "/memory_store:<type>[:<database_url>]",
                "Switch memory store backend 💾",
                "/memory_store:in_memory, /memory_store:redis, /memory_store:database",
            ),
            (
                "/event_store:<type>",
                "Switch event store backend 📡",
                "/event_store:in_memory, /event_store:redis_stream",
            ),
            (
                "/memory_mode[:<mode>[:<value>]]",
                "Configure memory mode for all agents 💾",
                "/memory_mode  # Show current memory mode\n"
                "/memory_mode:sliding_window:5  # Keep last 5 messages\n"
                "/memory_mode:token_budget:4000  # Keep messages under 4000 tokens\n",
            ),
            (
                "/add_servers:<path>",
                "Add one or more MCP servers from a JSON config file",
                "/add_servers:<config.json>",
            ),
            (
                "/remove_server:<name>",
                "Remove and disconnect a specific MCP server",
                "/remove_server:<server_name>",
            ),
            ("/api_stats", "Retrieve API usage stats for the current session 📊", ""),
            (
                "/mode:<type>",
                "Toggle mode between autonomous agent, orchestrator, and chat mode 🤖",
                "/mode:auto  # Toggle to auto mode\n"
                "/mode:chat  # Toggle to chat mode\n"
                "/mode:orchestrator  # Toggle to orchestrator mode",
            ),
            ("/debug", "Toggle debug mode 🐛", ""),
            ("/refresh", "Refresh server capabilities 🔄", ""),
            ("/help", "Show help 🆘", "/help:command"),
            ("/history", "Show message history 📝", ""),
            ("/clear_history", "Clear message history 🧹", ""),
            (
                "/save_history",
                "Save message history to file 💾",
                "/save_history:path/to/file",
            ),
            (
                "/load_history",
                "Load message history from file 💾",
                "/load_history:path/to/file",
            ),
            ("/tools", "List available tools 🔧", ""),
            ("/resources", "List available resources 📚", ""),
            (
                "/resource:<uri>",
                "Read a specific resource 🔍",
                "/resource:file:///path/to/file",
            ),
            (
                "/subscribe:/<type>:<uri>",
                "Subscribe to a resource 📚",
                "/subscribe:/resource:file:///path/to/file",
            ),
            (
                "/unsubscribe:/<type>:<uri>",
                "Unsubscribe from a resource 📚",
                "/unsubscribe:/resource:file:///path/to/file",
            ),
            ("/prompts", "List available prompts 💬", ""),
            (
                "/prompt:<name>/<args>",
                "Read a prompt with arguments or without arguments 💬",
                "/prompt:weather/location=lagos/radius=2",
            ),
            ("quit", "Exit the application 👋", ""),
        ]

        for cmd, desc, example in commands:
            commands_table.add_row(cmd, desc, example)

        self.console.print(commands_table)

        # Add a note about prompt arguments
        self.console.print(
            Panel(
                "[bold yellow]📝 Prompt Arguments:[/]\n"
                "• Use [cyan]key=value[/] pairs separated by [cyan]/[/]\n"
                "• Or use [cyan]{key:value}[/] JSON-like format\n"
                "• Values are automatically converted to appropriate types\n"
                "• Use [cyan]/prompts[/] to see available prompts and their arguments",
                title="[bold blue]💡 Tip[/]",
                border_style="blue",
                box=box.ROUNDED,
            )
        )
