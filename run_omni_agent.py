#!/usr/bin/env python3
"""
OmniAgent Unified Interface
A comprehensive CLI/Web interface for OmniAgent with all features.
"""

import asyncio
import argparse
import sys
import subprocess
from pathlib import Path
from typing import Optional

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcpomni_connect.omni_agent.agent import OmniAgent
from mcpomni_connect.memory_store.memory_router import MemoryRouter
from mcpomni_connect.events.event_router import EventRouter
from mcpomni_connect.omni_agent.background_agent.background_agent_manager import (
    BackgroundAgentManager,
)
from mcpomni_connect.omni_agent.background_agent.task_registry import TaskRegistry
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry
from mcpomni_connect.utils import logger


class OmniAgentCLI:
    """Comprehensive CLI interface for OmniAgent."""

    def __init__(self):
        """Initialize the CLI interface."""
        self.agent: Optional[OmniAgent] = None
        self.memory_router: Optional[MemoryRouter] = None
        self.event_router: Optional[EventRouter] = None
        self.background_manager: Optional[BackgroundAgentManager] = None
        self.session_id: Optional[str] = None

    async def create_comprehensive_tool_registry(self) -> ToolRegistry:
        """Create a comprehensive tool registry with various tool types."""
        tool_registry = ToolRegistry()

        # Mathematical tools
        @tool_registry.register_tool("calculate_area")
        def calculate_area(length: float, width: float) -> str:
            """Calculate the area of a rectangle."""
            area = length * width
            return f"Area of rectangle ({length} x {width}): {area} square units"

        @tool_registry.register_tool("calculate_perimeter")
        def calculate_perimeter(length: float, width: float) -> str:
            """Calculate the perimeter of a rectangle."""
            perimeter = 2 * (length + width)
            return f"Perimeter of rectangle ({length} x {width}): {perimeter} units"

        # Text processing tools
        @tool_registry.register_tool("format_text")
        def format_text(text: str, style: str = "normal") -> str:
            """Format text in different styles."""
            if style == "uppercase":
                return text.upper()
            elif style == "lowercase":
                return text.lower()
            elif style == "title":
                return text.title()
            elif style == "reverse":
                return text[::-1]
            else:
                return text

        @tool_registry.register_tool("word_count")
        def word_count(text: str) -> str:
            """Count words in text."""
            words = text.split()
            return f"Word count: {len(words)} words"

        # System information tools
        @tool_registry.register_tool("system_info")
        def get_system_info() -> str:
            """Get basic system information."""
            import platform
            import time

            info = f"""System Information:
• OS: {platform.system()} {platform.release()}
• Architecture: {platform.machine()}
• Python Version: {platform.python_version()}
• Current Time: {time.strftime("%Y-%m-%d %H:%M:%S")}"""
            return info

        # Data analysis tools
        @tool_registry.register_tool("analyze_numbers")
        def analyze_numbers(numbers: str) -> str:
            """Analyze a list of numbers."""
            try:
                num_list = [float(x.strip()) for x in numbers.split(",")]
                if not num_list:
                    return "No numbers provided"

                total = sum(num_list)
                average = total / len(num_list)
                minimum = min(num_list)
                maximum = max(num_list)

                return f"""Number Analysis:
• Count: {len(num_list)} numbers
• Sum: {total}
• Average: {average:.2f}
• Min: {minimum}
• Max: {maximum}"""
            except Exception as e:
                return f"Error analyzing numbers: {str(e)}"

        # File system tools
        @tool_registry.register_tool("list_directory")
        def list_directory(path: str = ".") -> str:
            """List contents of a directory."""
            import os

            try:
                if not os.path.exists(path):
                    return f"Directory {path} does not exist"

                items = os.listdir(path)
                files = [
                    item for item in items if os.path.isfile(os.path.join(path, item))
                ]
                dirs = [
                    item for item in items if os.path.isdir(os.path.join(path, item))
                ]

                return f"""Directory: {path}
• Files: {len(files)} ({files[:5]}{"..." if len(files) > 5 else ""})
• Directories: {len(dirs)} ({dirs[:5]}{"..." if len(dirs) > 5 else ""})"""
            except Exception as e:
                return f"Error listing directory: {str(e)}"

        logger.info("Created comprehensive ToolRegistry with 7 tools")
        return tool_registry

    async def initialize(self):
        """Initialize all components."""
        print("🚀 Initializing OmniAgent CLI...")

        # Initialize routers
        self.memory_router = MemoryRouter("in_memory")
        self.event_router = EventRouter("in_memory")

        # Create comprehensive tool registry
        tool_registry = await self.create_comprehensive_tool_registry()

        # Initialize agent with required parameters
        self.agent = OmniAgent(
            name="omniagent_cli",
            system_instruction="You are a helpful AI assistant with access to various tools. You can help users with tasks, answer questions, and perform calculations.",
            model_config={
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000,
            },
            local_tools=tool_registry,
            memory_store=self.memory_router,
            event_router=self.event_router,
        )

        # Initialize background agent manager
        self.background_manager = BackgroundAgentManager(
            memory_store=self.memory_router, event_router=self.event_router
        )

        print("✅ OmniAgent CLI initialized successfully")

    def print_welcome(self):
        """Print welcome message and available commands."""
        print("\n" + "=" * 80)
        print("🤖 OmniAgent CLI - Unified Interface")
        print("=" * 80)
        print("📋 Available Commands:")
        print("  /chat <message>           - Send a message to the agent")
        print("  /tools                    - List available tools")
        print("  /memory                   - Show memory information")
        print(
            "  /memory_store <type>      - Switch memory backend (in_memory/redis/database)"
        )
        print(
            "  /event_store <type>       - Switch event backend (in_memory/redis_stream)"
        )
        print("  /history                  - Show conversation history")
        print("  /clear_history            - Clear conversation history")
        print("  /save_history <file>      - Save history to file")
        print("  /load_history <file>      - Load history from file")
        print("  /background               - Background agent management")
        print("  /background_create        - Create a background agent")
        print("  /background_list          - List background agents")
        print("  /background_status        - Show background agent status")
        print("  /background_pause <id>    - Pause a background agent")
        print("  /background_resume <id>   - Resume a background agent")
        print("  /background_delete <id>   - Delete a background agent")
        print("  /task_register <id> <query> - Register a task for background agent")
        print("  /task_list               - List all registered tasks")
        print("  /task_update <id> <query> - Update a task")
        print("  /task_remove <id>        - Remove a task")
        print("  /events                  - Stream events in real-time")
        print("  /agent_info              - Show agent information")
        print("  /help                    - Show this help message")
        print("  /quit                    - Exit the CLI")
        print("=" * 80)
        print("💡 Tip: Use /help for detailed command information")
        print("=" * 80 + "\n")

    async def handle_chat(self, message: str):
        """Handle chat messages."""
        if not self.agent:
            print("❌ Agent not initialized")
            return

        print(f"🤖 Processing: {message}")

        # Generate session ID if not exists
        if not self.session_id:
            from datetime import datetime

            self.session_id = (
                f"cli_session_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}"
            )

        try:
            # Run the agent and get response
            result = await self.agent.run(message, session_id=self.session_id)
            response = result.get("response", "No response received")
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

    async def handle_tools(self):
        """List available tools."""
        if not self.agent:
            print("❌ Agent not initialized")
            return

        if self.agent.local_tools:
            tools = self.agent.local_tools.list_tools()
            print("🔧 Available Tools:")
            for tool in tools:
                print(f"  • {tool['name']}: {tool['description']}")
        else:
            print("🔧 No local tools available")

    async def handle_memory(self):
        """Show memory information."""
        if not self.memory_router:
            print("❌ Memory router not initialized")
            return

        info = self.memory_router.get_memory_store_info()
        print("🧠 Memory Information:")
        print(f"  Type: {info['type']}")
        print(f"  Available: {info['available']}")
        print(f"  Store Class: {info.get('store_class', 'N/A')}")

    async def handle_memory_store(self, store_type: str):
        """Switch memory backend."""
        if not self.memory_router:
            print("❌ Memory router not initialized")
            return

        try:
            self.memory_router.switch_memory_store(store_type)
            print(f"✅ Switched to {store_type} memory store")
        except Exception as e:
            print(f"❌ Error switching memory store: {e}")

    async def handle_event_store(self, store_type: str):
        """Switch event backend."""
        if not self.event_router:
            print("❌ Event router not initialized")
            return

        try:
            self.event_router.switch_event_store(store_type)
            print(f"✅ Switched to {store_type} event store")
        except Exception as e:
            print(f"❌ Error switching event store: {e}")

    async def handle_history(self):
        """Show conversation history."""
        if not self.session_id:
            print("❌ No active session")
            return

        if not self.agent:
            print("❌ Agent not initialized")
            return

        try:
            history = await self.agent.get_session_history(self.session_id)
            if history:
                print("📜 Conversation History:")
                for msg in history[-10:]:  # Show last 10 messages
                    print(
                        f"  {msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}..."
                    )
            else:
                print("📜 No conversation history found")
        except Exception as e:
            print(f"❌ Error getting history: {e}")

    async def handle_clear_history(self):
        """Clear conversation history."""
        if not self.session_id:
            print("❌ No active session")
            return

        if not self.agent:
            print("❌ Agent not initialized")
            return

        try:
            await self.agent.clear_session_history(self.session_id)
            print("✅ Conversation history cleared")
        except Exception as e:
            print(f"❌ Error clearing history: {e}")

    async def handle_save_history(self, filename: str):
        """Save conversation history to file."""
        if not self.session_id:
            print("❌ No active session")
            return

        if not self.memory_router:
            print("❌ Memory router not initialized")
            return

        try:
            self.memory_router.save_message_history_to_file(self.session_id, filename)
            print(f"✅ History saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving history: {e}")

    async def handle_load_history(self, filename: str):
        """Load conversation history from file."""
        if not self.session_id:
            print("❌ No active session")
            return

        if not self.memory_router:
            print("❌ Memory router not initialized")
            return

        try:
            self.memory_router.load_message_history_from_file(self.session_id, filename)
            print(f"✅ History loaded from {filename}")
        except Exception as e:
            print(f"❌ Error loading history: {e}")

    async def handle_background_create(self):
        """Create a background agent."""
        if not self.background_manager:
            print("❌ Background manager not initialized")
            return

        print("🤖 Creating background agent...")
        print("Available agent types:")
        print("  1. file_monitor - Monitor file system changes")
        print("  2. system_monitor - Monitor system status")
        print("  3. calculator - Perform calculations")
        print("  4. custom - Custom agent with specific tools")

        agent_type = input("Enter agent type (1-4): ").strip()

        agent_configs = {
            "1": {
                "agent_id": "file_monitor_agent",
                "interval": 30,
                "task_config": {
                    "query": "Monitor file system changes in /tmp and /var/log directories"
                },
            },
            "2": {
                "agent_id": "system_monitor_agent",
                "interval": 45,
                "task_config": {
                    "query": "Monitor system status and report critical issues"
                },
            },
            "3": {
                "agent_id": "calculator_agent",
                "interval": 60,
                "task_config": {
                    "query": "Perform periodic calculations and report results"
                },
            },
            "4": {
                "agent_id": "custom_agent",
                "interval": 30,
                "task_config": {"query": input("Enter custom task query: ")},
            },
        }

        if agent_type not in agent_configs:
            print("❌ Invalid agent type")
            return

        config = agent_configs[agent_type]
        try:
            session_id, event_info = self.background_manager.create_agent(config)
            print(f"✅ Background agent created: {config['agent_id']}")
            print(f"Session ID: {session_id}")
            print(f"Event Store: {event_info}")
        except Exception as e:
            print(f"❌ Error creating background agent: {e}")

    async def handle_background_list(self):
        """List background agents."""
        if not self.background_manager:
            print("❌ Background manager not initialized")
            return

        try:
            agents = self.background_manager.list_agents()
            if agents:
                print("🤖 Background Agents:")
                for agent_id in agents:
                    print(f"  • {agent_id}")
            else:
                print("🤖 No background agents found")
        except Exception as e:
            print(f"❌ Error listing agents: {e}")

    async def handle_background_status(self):
        """Show background agent status."""
        if not self.background_manager:
            print("❌ Background manager not initialized")
            return

        try:
            status = self.background_manager.get_manager_status()
            print("📊 Background Agent Manager Status:")
            print(f"  Running: {status['running']}")
            print(f"  Total Agents: {status['total_agents']}")
            print(f"  Scheduler Running: {status['scheduler_running']}")

            # Show individual agent statuses
            agents = self.background_manager.list_agents()
            if agents:
                print("\n🤖 Individual Agent Status:")
                for agent_id in agents:
                    agent_status = self.background_manager.get_agent_status(agent_id)
                    print(f"  {agent_id}:")
                    print(f"    Running: {agent_status['running']}")
                    print(f"    Scheduled: {agent_status['scheduled']}")
                    print(f"    Run Count: {agent_status['run_count']}")
                    print(f"    Error Count: {agent_status['error_count']}")
        except Exception as e:
            print(f"❌ Error getting status: {e}")

    async def handle_background_pause(self, agent_id: str):
        """Pause a background agent."""
        if not self.background_manager:
            print("❌ Background manager not initialized")
            return

        try:
            self.background_manager.pause_agent(agent_id)
            print(f"⏸️ Paused agent: {agent_id}")
        except Exception as e:
            print(f"❌ Error pausing agent: {e}")

    async def handle_background_resume(self, agent_id: str):
        """Resume a background agent."""
        if not self.background_manager:
            print("❌ Background manager not initialized")
            return

        try:
            self.background_manager.resume_agent(agent_id)
            print(f"▶️ Resumed agent: {agent_id}")
        except Exception as e:
            print(f"❌ Error resuming agent: {e}")

    async def handle_background_delete(self, agent_id: str):
        """Delete a background agent."""
        if not self.background_manager:
            print("❌ Background manager not initialized")
            return

        try:
            self.background_manager.delete_agent(agent_id)
            print(f"🗑️ Deleted agent: {agent_id}")
        except Exception as e:
            print(f"❌ Error deleting agent: {e}")

    async def handle_task_register(self, agent_id: str, query: str):
        """Register a task for a background agent."""
        if not self.background_manager:
            print("❌ Background manager not initialized")
            return

        try:
            self.background_manager.register_task(agent_id, {"query": query})
            print(f"✅ Registered task for agent: {agent_id}")
        except Exception as e:
            print(f"❌ Error registering task: {e}")

    async def handle_task_list(self):
        """List all registered tasks."""
        if not self.background_manager:
            print("❌ Background manager not initialized")
            return

        try:
            tasks = self.background_manager.list_tasks()
            if tasks:
                print("📋 Registered Tasks:")
                for agent_id, task in tasks.items():
                    print(f"  {agent_id}: {task.get('query', 'No query')}")
            else:
                print("📋 No registered tasks found")
        except Exception as e:
            print(f"❌ Error listing tasks: {e}")

    async def handle_task_update(self, agent_id: str, query: str):
        """Update a task."""
        if not self.background_manager:
            print("❌ Background manager not initialized")
            return

        try:
            self.background_manager.update_task_config(agent_id, {"query": query})
            print(f"✅ Updated task for agent: {agent_id}")
        except Exception as e:
            print(f"❌ Error updating task: {e}")

    async def handle_task_remove(self, agent_id: str):
        """Remove a task."""
        if not self.background_manager:
            print("❌ Background manager not initialized")
            return

        try:
            self.background_manager.remove_task(agent_id)
            print(f"✅ Removed task for agent: {agent_id}")
        except Exception as e:
            print(f"❌ Error removing task: {e}")

    async def handle_events(self):
        """Stream events in real-time."""
        if not self.event_router:
            print("❌ Event router not initialized")
            return

        print("📡 Streaming events (Press Ctrl+C to stop)...")
        try:
            async for event in self.event_router.stream():
                print(f"🎯 Event: {event.type} - {event.timestamp}")
                if hasattr(event, "payload") and event.payload:
                    print(f"  Payload: {event.payload}")
        except KeyboardInterrupt:
            print("\n⏹️ Event streaming stopped")
        except Exception as e:
            print(f"❌ Error streaming events: {e}")

    async def handle_agent_info(self):
        """Show agent information."""
        if not self.agent:
            print("❌ Agent not initialized")
            return

        print("🤖 Agent Information:")
        print(f"  Session ID: {self.session_id or 'None'}")
        print(f"  Memory Store: {self.agent.get_memory_store_type()}")
        print(f"  Event Store: {self.agent.get_event_store_type()}")
        print(f"  Memory Available: {self.agent.is_memory_store_available()}")
        print(f"  Event Store Available: {self.agent.is_event_store_available()}")

    async def handle_help(self):
        """Show detailed help."""
        self.print_welcome()

    async def run(self):
        """Run the CLI interface."""
        await self.initialize()
        self.print_welcome()

        print("💬 Start chatting with OmniAgent! Type /help for commands.")
        print()

        while True:
            try:
                user_input = input("🤖 OmniAgent> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["/quit", "/exit", "quit", "exit"]:
                    print("👋 Goodbye!")
                    break

                # Handle commands
                if user_input.startswith("/"):
                    parts = user_input.split(" ", 1)
                    command = parts[0].lower()
                    args = parts[1] if len(parts) > 1 else ""

                    if command == "/chat":
                        if args:
                            await self.handle_chat(args)
                        else:
                            print("❌ Please provide a message: /chat <message>")
                    elif command == "/tools":
                        await self.handle_tools()
                    elif command == "/memory":
                        await self.handle_memory()
                    elif command == "/memory_store":
                        if args:
                            await self.handle_memory_store(args)
                        else:
                            print("❌ Please provide store type: /memory_store <type>")
                    elif command == "/event_store":
                        if args:
                            await self.handle_event_store(args)
                        else:
                            print("❌ Please provide store type: /event_store <type>")
                    elif command == "/history":
                        await self.handle_history()
                    elif command == "/clear_history":
                        await self.handle_clear_history()
                    elif command == "/save_history":
                        if args:
                            await self.handle_save_history(args)
                        else:
                            print("❌ Please provide filename: /save_history <file>")
                    elif command == "/load_history":
                        if args:
                            await self.handle_load_history(args)
                        else:
                            print("❌ Please provide filename: /load_history <file>")
                    elif command == "/background_create":
                        await self.handle_background_create()
                    elif command == "/background_list":
                        await self.handle_background_list()
                    elif command == "/background_status":
                        await self.handle_background_status()
                    elif command == "/background_pause":
                        if args:
                            await self.handle_background_pause(args)
                        else:
                            print("❌ Please provide agent ID: /background_pause <id>")
                    elif command == "/background_resume":
                        if args:
                            await self.handle_background_resume(args)
                        else:
                            print("❌ Please provide agent ID: /background_resume <id>")
                    elif command == "/background_delete":
                        if args:
                            await self.handle_background_delete(args)
                        else:
                            print("❌ Please provide agent ID: /background_delete <id>")
                    elif command == "/task_register":
                        if args:
                            parts = args.split(" ", 1)
                            if len(parts) == 2:
                                await self.handle_task_register(parts[0], parts[1])
                            else:
                                print(
                                    "❌ Please provide agent ID and query: /task_register <id> <query>"
                                )
                        else:
                            print(
                                "❌ Please provide agent ID and query: /task_register <id> <query>"
                            )
                    elif command == "/task_list":
                        await self.handle_task_list()
                    elif command == "/task_update":
                        if args:
                            parts = args.split(" ", 1)
                            if len(parts) == 2:
                                await self.handle_task_update(parts[0], parts[1])
                            else:
                                print(
                                    "❌ Please provide agent ID and query: /task_update <id> <query>"
                                )
                        else:
                            print(
                                "❌ Please provide agent ID and query: /task_update <id> <query>"
                            )
                    elif command == "/task_remove":
                        if args:
                            await self.handle_task_remove(args)
                        else:
                            print("❌ Please provide agent ID: /task_remove <id>")
                    elif command == "/events":
                        await self.handle_events()
                    elif command == "/agent_info":
                        await self.handle_agent_info()
                    elif command == "/help":
                        await self.handle_help()
                    else:
                        print(f"❌ Unknown command: {command}")
                        print("💡 Type /help for available commands")
                else:
                    # Treat as chat message
                    await self.handle_chat(user_input)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="OmniAgent Unified Interface")
    parser.add_argument(
        "--mode",
        choices=["cli", "web"],
        default="cli",
        help="Interface mode (cli or web)",
    )

    args = parser.parse_args()

    if args.mode == "cli":
        # Run CLI interface
        cli = OmniAgentCLI()
        asyncio.run(cli.run())
    elif args.mode == "web":
        # Run web interface
        print("🌐 Starting web interface...")
        try:
            subprocess.run([sys.executable, "examples/web_server.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Web server error: {e}")
        except KeyboardInterrupt:
            print("\n👋 Web server stopped")
    else:
        print(f"❌ Unknown mode: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
