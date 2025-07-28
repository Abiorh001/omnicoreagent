#!/usr/bin/env python3
"""
FastAPI Web Server for OmniAgent Interface
Runs independently to avoid event loop conflicts
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import AsyncGenerator

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from mcpomni_connect.omni_agent import OmniAgent
from mcpomni_connect.memory_store.memory_router import MemoryRouter
from mcpomni_connect.events.event_router import EventRouter
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry
from mcpomni_connect.utils import logger


class OmniAgentWebServer:
    def __init__(self):
        self.app = FastAPI(title="OmniAgent Interface", version="1.0.0")
        self.agent = None
        self.setup_middleware()
        self.setup_routes()

    def setup_middleware(self):
        """Setup CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Setup all API routes."""

        # Mount static files
        self.app.mount(
            "/static", StaticFiles(directory="examples/static"), name="static"
        )

        # Templates
        templates = Jinja2Templates(directory="examples/templates")

        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            return templates.TemplateResponse(
                "omni_agent_interface.html", {"request": request}
            )

        @self.app.post("/chat")
        async def chat_endpoint(request: Request):
            """Handle chat messages with streaming response."""
            data = await request.json()
            message = data.get("message", "")
            session_id = data.get("session_id", None)

            if not session_id:
                session_id = f"web_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            async def generate_response() -> AsyncGenerator[str, None]:
                """Generate streaming response."""
                try:
                    if not self.agent:
                        yield f"data: {json.dumps({'type': 'error', 'content': 'Agent not initialized', 'session_id': session_id})}\n\n"
                        return

                    # Start the agent processing
                    result = await self.agent.run(message, session_id)
                    response = result.get("response", "No response received")

                    # Stream the response in chunks
                    chunk_size = 50
                    for i in range(0, len(response), chunk_size):
                        chunk = response[i : i + chunk_size]
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk, 'session_id': session_id})}\n\n"
                        await asyncio.sleep(0.1)  # Small delay for streaming effect

                    # Send completion signal
                    yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id})}\n\n"

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    yield f"data: {json.dumps({'type': 'error', 'content': error_msg, 'session_id': session_id})}\n\n"

            return StreamingResponse(
                generate_response(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                },
            )

        @self.app.get("/tools")
        async def get_tools():
            """Get available tools."""
            if self.agent and self.agent.local_tools:
                tools = self.agent.local_tools.list_tools()
                return {"tools": tools}
            return {"tools": []}

        @self.app.get("/history/{session_id}")
        async def get_history(session_id: str):
            """Get conversation history for a session."""
            if self.agent:
                history = await self.agent.get_session_history(session_id)
                return {"history": history}
            return {"history": []}

        @self.app.post("/clear-history/{session_id}")
        async def clear_history(session_id: str):
            """Clear conversation history for a session."""
            if self.agent:
                await self.agent.clear_session_history(session_id)
                return {"status": "cleared"}
            return {"status": "error"}

        @self.app.get("/agent-info")
        async def get_agent_info():
            """Get agent information."""
            if self.agent:
                return {
                    "name": self.agent.name,
                    "memory_store": self.agent.memory_store.get_memory_store_info(),
                    "event_store": self.agent.get_event_store_info(),
                    "tools_count": len(self.agent.local_tools.list_tools())
                    if self.agent.local_tools
                    else 0,
                }
            return {"error": "Agent not initialized"}

        @self.app.post("/switch-backend")
        async def switch_backend(request: Request):
            """Switch memory or event backend."""
            data = await request.json()
            backend_type = data.get("type")  # 'memory' or 'event'
            backend_name = data.get("backend")

            try:
                if backend_type == "memory":
                    self.agent.memory_store = MemoryRouter(backend_name)
                    return {
                        "status": "success",
                        "message": f"Memory backend switched to {backend_name}",
                    }
                elif backend_type == "event":
                    self.agent.switch_event_store(backend_name)
                    return {
                        "status": "success",
                        "message": f"Event backend switched to {backend_name}",
                    }
                else:
                    return {"status": "error", "message": "Invalid backend type"}
            except Exception as e:
                return {"status": "error", "message": str(e)}

    async def initialize_agent(self):
        """Initialize the OmniAgent with all features."""
        logger.info("🚀 Initializing OmniAgent for Web Interface...")

        # Create memory and event routers
        memory_store = MemoryRouter(memory_store_type="in_memory")
        event_router = EventRouter(event_store_type="in_memory")

        # Create comprehensive tool registry
        tool_registry = await self.create_comprehensive_tool_registry()

        # Create OmniAgent with all features
        self.agent = OmniAgent(
            name="web_interface_agent",
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

        logger.info("✅ OmniAgent initialized successfully for web interface")

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

    def run(self):
        """Run the FastAPI server."""
        print("🌐 Starting FastAPI web interface...")
        print("📱 Web interface will be available at: http://localhost:8000")
        print("📚 API documentation at: http://localhost:8000/docs")

        # Initialize agent in the background
        asyncio.create_task(self.initialize_agent())

        # Run the server
        uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    server = OmniAgentWebServer()
    server.run()
