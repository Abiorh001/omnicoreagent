#!/usr/bin/env python3
"""
Unified OmniAgent Interface - CLI and Web modes
Demonstrates all OmniAgent features with interactive interface
"""

import asyncio
import sys
import os
import argparse
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from mcpomni_connect.omni_agent import OmniAgent
from mcpomni_connect.memory_store.memory_router import MemoryRouter
from mcpomni_connect.events.event_router import EventRouter
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry
from mcpomni_connect.utils import logger


class OmniAgentInterface:
    """Unified interface for OmniAgent with CLI and Web modes."""

    def __init__(self, mode: str = "cli"):
        self.mode = mode
        self.agent = None
        self.session_id = None
        self.is_running = False

    async def initialize_agent(self):
        """Initialize the OmniAgent with all features."""
        logger.info("🚀 Initializing OmniAgent Interface...")

        # Create memory and event routers
        memory_store = MemoryRouter(memory_store_type="in_memory")
        event_router = EventRouter(event_store_type="in_memory")

        # Create comprehensive tool registry
        tool_registry = await self.create_comprehensive_tool_registry()

        # Create OmniAgent with all features
        self.agent = OmniAgent(
            name="unified_interface_agent",
            system_instruction="You are a comprehensive AI assistant with access to mathematical, text processing, system information, data analysis, and file system tools. You can perform complex calculations, format text, analyze data, and provide system information. Always use the appropriate tools for the task and provide clear, helpful responses.",
            model_config={
                "provider": "openai",
                "model": "gpt-4.1",
                "temperature": 0.7,
                "max_context_length": 50000,
            },
            mcp_tools=[
                {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        "/home/abiorh/Desktop",
                        "/home/abiorh/ai/",
                    ],
                }
            ],
            local_tools=tool_registry,
            agent_config={
                "max_steps": 15,
                "tool_call_timeout": 60,
                "request_limit": 1000,
                "memory_config": {"mode": "token_budget", "value": 10000},
            },
            memory_store=memory_store,
            event_router=event_router,
            debug=True,
        )

        logger.info("✅ OmniAgent initialized successfully")

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

    def print_welcome_header(self):
        """Print welcome header based on mode."""
        if self.mode == "cli":
            print("\n" + "=" * 80)
            print("🤖 OMNIGENT UNIFIED INTERFACE - CLI MODE")
            print("=" * 80)
            print("Available Commands:")
            print("  /help              - Show this help")
            print("  /memory            - Show memory information")
            print("  /events            - Show event information")
            print("  /tools             - List available tools")
            print("  /history           - Show conversation history")
            print("  /clear             - Clear conversation history")
            print("  /save <file>       - Save conversation to file")
            print("  /load <file>       - Load conversation from file")
            print("  /switch <backend>  - Switch memory/event backends")
            print("  /quit              - Exit the interface")
            print("  <message>          - Send message to agent")
            print("=" * 80)
        else:
            print("🌐 Web interface initialized")

    async def handle_cli_command(self, command: str) -> bool:
        """Handle CLI commands. Returns True if should continue, False to quit."""
        command = command.strip()

        if command == "/quit":
            print("👋 Goodbye!")
            return False

        elif command == "/help":
            self.print_welcome_header()
            return True

        elif command == "/memory":
            if self.agent:
                info = self.agent.memory_store.get_memory_store_info()
                print(f"🧠 Memory Store: {info}")
            return True

        elif command == "/events":
            if self.agent:
                info = self.agent.get_event_store_info()
                print(f"📡 Event Store: {info}")
            return True

        elif command == "/tools":
            if self.agent and self.agent.local_tools:
                tools = self.agent.local_tools.list_tools()
                print("🔧 Available Tools:")
                for tool in tools:
                    print(f"  • {tool['name']}: {tool['description']}")
            return True

        elif command == "/history":
            if self.agent and self.session_id:
                history = await self.agent.get_session_history(self.session_id)
                print(f"📜 Conversation History ({len(history)} messages):")
                for i, msg in enumerate(history[-10:], 1):  # Show last 10 messages
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")[:100]
                    print(f"  {i}. {role}: {content}...")
            return True

        elif command == "/clear":
            if self.agent and self.session_id:
                await self.agent.clear_session_history(self.session_id)
                print("🧹 Conversation history cleared")
            return True

        elif command.startswith("/save "):
            file_path = command[6:].strip()
            if self.agent and self.session_id:
                try:
                    await self.agent.memory_store.save_message_history_to_file(
                        file_path
                    )
                    print(f"💾 Conversation saved to {file_path}")
                except Exception as e:
                    print(f"❌ Error saving conversation: {e}")
            return True

        elif command.startswith("/load "):
            file_path = command[6:].strip()
            if self.agent and self.session_id:
                try:
                    await self.agent.memory_store.load_message_history_from_file(
                        file_path
                    )
                    print(f"📂 Conversation loaded from {file_path}")
                except Exception as e:
                    print(f"❌ Error loading conversation: {e}")
            return True

        elif command.startswith("/switch "):
            backend = command[8:].strip()
            if self.agent:
                try:
                    if "memory" in backend:
                        self.agent.memory_store = MemoryRouter(
                            backend.replace("memory:", "")
                        )
                        print(f"🔄 Switched memory store to {backend}")
                    elif "event" in backend:
                        self.agent.switch_event_store(backend.replace("event:", ""))
                        print(f"🔄 Switched event store to {backend}")
                except Exception as e:
                    print(f"❌ Error switching backend: {e}")
            return True

        else:
            # Not a command, treat as message
            return await self.process_message(command)

    async def process_message(self, message: str) -> bool:
        """Process a message through the agent."""
        if not self.agent:
            print("❌ Agent not initialized")
            return True

        if not self.session_id:
            self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"🆔 New session created: {self.session_id}")

        try:
            print(f"\n🤖 Processing: {message}")
            result = await self.agent.run(message, self.session_id)

            if result and "response" in result:
                print(f"\n✅ Response: {result['response']}")
            else:
                print("\n❌ No response received")

        except Exception as e:
            print(f"\n❌ Error processing message: {e}")

        return True

    async def run_cli_mode(self):
        """Run the interface in CLI mode."""
        self.print_welcome_header()

        print("\n💬 Start chatting with the agent! (Type /help for commands)")

        while self.is_running:
            try:
                if self.mode == "cli":
                    user_input = input("\n👤 You: ").strip()
                else:
                    # For web mode, this would come from web interface
                    user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    should_continue = await self.handle_cli_command(user_input)
                    if not should_continue:
                        break
                else:
                    should_continue = await self.process_message(user_input)
                    if not should_continue:
                        break

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break

    async def run_web_mode(self):
        """Run the interface in web mode using separate FastAPI server."""
        try:
            import subprocess
            import sys
            import os
        except ImportError:
            print("❌ Web mode requires subprocess module")
            return

        print("🌐 Starting FastAPI web interface...")
        print("📱 Web interface will be available at: http://localhost:8000")
        print("📚 API documentation at: http://localhost:8000/docs")
        print("🔄 Starting web server in separate process...")

        # Run the web server in a separate process
        web_server_path = os.path.join(os.path.dirname(__file__), "web_server.py")

        try:
            subprocess.run([sys.executable, web_server_path], check=True)
        except KeyboardInterrupt:
            print("\n👋 Web server stopped")
        except subprocess.CalledProcessError as e:
            print(f"❌ Web server error: {e}")
        except FileNotFoundError:
            print(f"❌ Web server file not found: {web_server_path}")
            print("💡 Make sure web_server.py exists in the examples directory")

    async def run(self):
        """Run the interface in the specified mode."""
        await self.initialize_agent()
        self.is_running = True

        if self.mode == "cli":
            await self.run_cli_mode()
        elif self.mode == "web":
            await self.run_web_mode()
        else:
            print(f"❌ Unknown mode: {self.mode}")

        # Cleanup
        if self.agent:
            await self.agent.cleanup()


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="OmniAgent Unified Interface")
    parser.add_argument(
        "--mode",
        choices=["cli", "web"],
        default="cli",
        help="Interface mode: cli or web",
    )

    args = parser.parse_args()

    interface = OmniAgentInterface(mode=args.mode)
    await interface.run()


if __name__ == "__main__":
    asyncio.run(main())
