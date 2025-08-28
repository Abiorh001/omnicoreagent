#!/usr/bin/env python3
"""
Enhanced OmniAgent Web Server - Professional Showcase Interface
Demonstrates ALL CLI capabilities through web interface
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# TOP-LEVEL IMPORTS
from omnicoreagent import (
    OmniAgent,
    MemoryRouter,
    EventRouter,
    BackgroundAgentManager,
    ToolRegistry,
    logger,
)


# Data Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class BackgroundAgentRequest(BaseModel):
    agent_id: str
    query: str
    schedule: Optional[str] = None


class TaskUpdateRequest(BaseModel):
    agent_id: str
    query: str


class AgentConfigRequest(BaseModel):
    name: str
    system_instruction: str
    llm_config: dict  # Changed from model_config to avoid Pydantic conflict
    agent_config: dict


class OmniAgentEnhancedServer:
    """Enhanced web server with ALL CLI capabilities."""

    def __init__(self):
        self.app = FastAPI(
            title="OmniAgent Professional Interface",
            description="Comprehensive AI Agent Framework with MCP Client Capabilities",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
        )

        # Core components
        self.agent: Optional[OmniAgent] = None
        self.memory_router: Optional[MemoryRouter] = None
        self.event_router: Optional[EventRouter] = None
        self.background_manager: Optional[BackgroundAgentManager] = None
        self.tool_registry: Optional[ToolRegistry] = None

        # WebSocket connections for real-time updates
        self.active_connections: List[WebSocket] = []

        # Session management
        self.sessions: Dict[str, dict] = {}

        self.setup_middleware()
        self.setup_routes()
        self.setup_tools()

    def setup_middleware(self):
        """Setup CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_tools(self):
        """Setup the comprehensive tool registry."""
        self.tool_registry = ToolRegistry()

        # Mathematical tools
        @self.tool_registry.register_tool("calculate_area")
        def calculate_area(length: float, width: float) -> str:
            area = length * width
            return f"Area of rectangle ({length} x {width}): {area} square units"

        @self.tool_registry.register_tool("calculate_perimeter")
        def calculate_perimeter(length: float, width: float) -> str:
            perimeter = 2 * (length + width)
            return f"Perimeter of rectangle ({length} x {width}): {perimeter} units"

        # Text processing tools
        @self.tool_registry.register_tool("format_text")
        def format_text(text: str, style: str = "normal") -> str:
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

        @self.tool_registry.register_tool("word_count")
        def word_count(text: str) -> str:
            words = text.split()
            return f"Word count: {len(words)} words"

        # System information tools
        @self.tool_registry.register_tool("system_info")
        def get_system_info() -> str:
            import platform
            import time

            info = f"""System Information:
• OS: {platform.system()} {platform.release()}
• Architecture: {platform.machine()}
• Python Version: {platform.python_version()}
• Current Time: {time.strftime("%Y-%m-%d %H:%M:%S")}"""
            return info

        # Data analysis tools
        @self.tool_registry.register_tool("analyze_numbers")
        def analyze_numbers(numbers: str) -> str:
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

    async def initialize_agent(self):
        """Initialize the OmniAgent with all components."""
        try:
            # Initialize memory and event routers
            self.memory_router = MemoryRouter(memory_store_type="in_memory")
            self.event_router = EventRouter(event_store_type="in_memory")

            # Initialize background agent manager
            self.background_manager = BackgroundAgentManager(
                memory_router=self.memory_router, event_router=self.event_router
            )

            # Initialize the main agent
            self.agent = OmniAgent(
                name="enhanced_web_agent",
                system_instruction="""You are an advanced AI assistant with access to multiple tools and capabilities.
                You can perform mathematical calculations, text processing, system analysis, and data analysis.
                Always provide clear, helpful responses and use the appropriate tools when needed.""",
                model_config={
                    "provider": "openai",
                    "model": "gpt-4.1",
                    "temperature": 0.7,
                    "max_context_length": 5000,
                },
                agent_config={
                    "max_steps": 15,
                    "tool_call_timeout": 60,
                    "memory_config": {"mode": "sliding_window", "value": 80000},
                },
                memory_router=self.memory_router,
                event_router=self.event_router,
                debug=True,
            )

            logger.info("✅ Enhanced OmniAgent initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            raise

    def setup_routes(self):
        """Setup all API routes."""

        # Mount static files
        self.app.mount(
            "/static", StaticFiles(directory="examples/static"), name="static"
        )

        # Templates
        templates = Jinja2Templates(directory="examples/templates")

        @self.app.on_event("startup")
        async def startup_event():
            """Initialize agent on startup."""
            logger.info("🔄 Initializing enhanced agent on startup...")
            try:
                await self.initialize_agent()
                logger.info("✅ Enhanced agent initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize agent: {e}")

        # Main interface
        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            return templates.TemplateResponse(
                "enhanced_omni_agent_interface.html", {"request": request}
            )

        # Chat endpoint with streaming
        @self.app.post("/api/chat")
        async def chat_endpoint(request: ChatRequest):
            """Handle chat messages with streaming response."""
            if not self.agent:
                raise HTTPException(status_code=503, detail="Agent not initialized")

            session_id = request.session_id or f"web_session_{uuid.uuid4().hex[:8]}"

            async def generate_response() -> AsyncGenerator[str, None]:
                try:
                    # Run the agent
                    result = await self.agent.run(request.message, session_id)
                    response = result.get("response", "No response received")

                    # Stream the response
                    chunk_size = 50
                    for i in range(0, len(response), chunk_size):
                        chunk = response[i : i + chunk_size]
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk, 'session_id': session_id})}\n\n"
                        await asyncio.sleep(0.05)  # Smooth streaming

                    # Send completion signal
                    yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id})}\n\n"

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    yield f"data: {json.dumps({'type': 'error', 'content': error_msg, 'session_id': session_id})}\n\n"

            return StreamingResponse(generate_response(), media_type="text/plain")

        # Background agent management
        @self.app.post("/api/background/create")
        async def create_background_agent(request: BackgroundAgentRequest):
            """Create a background agent."""
            if not self.background_manager:
                raise HTTPException(
                    status_code=503, detail="Background manager not initialized"
                )

            try:
                # Create full agent configuration following the correct pattern
                agent_config = {
                    "agent_id": request.agent_id,
                    "system_instruction": f"You are a background agent that performs the task: {request.query}",
                    "model_config": {
                        "provider": "openai",
                        "model": "gpt-4o",
                        "temperature": 0.7,
                        "max_context_length": 5000,
                    },
                    "agent_config": {
                        "max_steps": 10,
                        "tool_call_timeout": 60,
                        "memory_config": {"mode": "sliding_window", "value": 80000},
                    },
                    "task_config": {
                        "query": request.query,
                        "schedule": request.schedule or "immediate",
                        "interval": 30 if request.schedule else None,
                        "max_retries": 2,
                        "retry_delay": 30,
                    },
                }

                result = await self.background_manager.create_agent(agent_config)
                return {
                    "status": "success",
                    "agent_id": request.agent_id,
                    "message": "Background agent created",
                    "details": result,
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/background/list")
        async def list_background_agents():
            """List all background agents."""
            if not self.background_manager:
                raise HTTPException(
                    status_code=503, detail="Background manager not initialized"
                )

            try:
                agents = await self.background_manager.list_agents()
                return {"status": "success", "agents": agents}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/background/start")
        async def start_background_agent(request: BackgroundAgentRequest):
            """Start a background agent."""
            if not self.background_manager:
                raise HTTPException(
                    status_code=503, detail="Background manager not initialized"
                )

            try:
                await self.background_manager.start_agent(request.agent_id)
                return {
                    "status": "success",
                    "message": f"Agent {request.agent_id} started",
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/background/stop")
        async def stop_background_agent(request: BackgroundAgentRequest):
            """Stop a background agent."""
            if not self.background_manager:
                raise HTTPException(
                    status_code=503, detail="Background manager not initialized"
                )

            try:
                await self.background_manager.stop_agent(request.agent_id)
                return {
                    "status": "success",
                    "message": f"Agent {request.agent_id} stopped",
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Task management
        @self.app.post("/api/task/update")
        async def update_task(request: TaskUpdateRequest):
            """Update a background task."""
            if not self.background_manager:
                raise HTTPException(
                    status_code=503, detail="Background manager not initialized"
                )

            try:
                await self.background_manager.update_task(
                    request.agent_id, request.query
                )
                return {
                    "status": "success",
                    "message": f"Task updated for agent {request.agent_id}",
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/task/remove/{agent_id}")
        async def remove_task(agent_id: str):
            """Remove a background task."""
            if not self.background_manager:
                raise HTTPException(
                    status_code=503, detail="Background manager not initialized"
                )

            try:
                await self.background_manager.remove_task(agent_id)
                return {
                    "status": "success",
                    "message": f"Task removed for agent {agent_id}",
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Event streaming
        @self.app.get("/api/events")
        async def get_events():
            """Get recent events."""
            if not self.event_router:
                raise HTTPException(
                    status_code=503, detail="Event router not initialized"
                )

            try:
                events = await self.event_router.get_recent_events(limit=50)
                return {"status": "success", "events": events}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Agent information
        @self.app.get("/api/agent/info")
        async def get_agent_info():
            """Get agent information."""
            if not self.agent:
                raise HTTPException(status_code=503, detail="Agent not initialized")

            try:
                info = {
                    "name": self.agent.name,
                    "status": "active",
                    "memory_store": type(self.memory_router).__name__,
                    "event_store": type(self.event_router).__name__,
                    "background_agents": len(
                        await self.background_manager.list_agents()
                    )
                    if self.background_manager
                    else 0,
                }
                return {"status": "success", "info": info}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Tool information
        @self.app.get("/api/tools")
        async def get_tools():
            """Get available tools."""
            if not self.tool_registry:
                raise HTTPException(
                    status_code=503, detail="Tool registry not initialized"
                )

            try:
                tools = self.tool_registry.list_tools()
                return {"status": "success", "tools": tools}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # WebSocket for real-time updates
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)

            try:
                while True:
                    # Keep connection alive and handle real-time updates
                    await websocket.receive_text()
                    await websocket.send_text(
                        json.dumps(
                            {"type": "ping", "timestamp": datetime.now().isoformat()}
                        )
                    )
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)

        # Health check
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "agent_initialized": self.agent is not None,
                "background_manager_initialized": self.background_manager is not None,
                "active_connections": len(self.active_connections),
            }


def main():
    """Start the enhanced web server."""
    server = OmniAgentEnhancedServer()

    print("🚀 Starting Enhanced OmniAgent Web Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Interactive API: http://localhost:8000/redoc")
    print("🌐 Web Interface: http://localhost:8000")
    print("💡 Press Ctrl+C to stop")

    uvicorn.run(server.app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
