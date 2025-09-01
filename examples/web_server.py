#!/usr/bin/env python3
"""
FastAPI Web Server for OmniAgent Interface
Runs independently to avoid event loop conflicts
"""

import asyncio
import json
import os
from datetime import datetime
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# OmniAgent imports
from omnicoreagent import OmniAgent, MemoryRouter, EventRouter, ToolRegistry, logger


# -------------------------------
# Tool registry builder
# -------------------------------
async def create_comprehensive_tool_registry() -> ToolRegistry:
    tool_registry = ToolRegistry()

    # Mathematical tools
    @tool_registry.register_tool("calculate_area")
    def calculate_area(length: float, width: float) -> str:
        area = length * width
        return f"Area of rectangle ({length} x {width}): {area} square units"

    @tool_registry.register_tool("calculate_perimeter")
    def calculate_perimeter(length: float, width: float) -> str:
        perimeter = 2 * (length + width)
        return f"Perimeter of rectangle ({length} x {width}): {perimeter} units"

    # Text processing tools
    @tool_registry.register_tool("format_text")
    def format_text(text: str, style: str = "normal") -> str:
        if style == "uppercase":
            return text.upper()
        elif style == "lowercase":
            return text.lower()
        elif style == "title":
            return text.title()
        elif style == "reverse":
            return text[::-1]
        return text

    @tool_registry.register_tool("word_count")
    def word_count(text: str) -> str:
        words = text.split()
        return f"Word count: {len(words)} words"

    # System information tools
    @tool_registry.register_tool("system_info")
    def get_system_info() -> str:
        import platform, time

        return f"""System Information:
• OS: {platform.system()} {platform.release()}
• Architecture: {platform.machine()}
• Python Version: {platform.python_version()}
• Current Time: {time.strftime("%Y-%m-%d %H:%M:%S")}"""

    # Data analysis tools
    @tool_registry.register_tool("analyze_numbers")
    def analyze_numbers(numbers: str) -> str:
        try:
            num_list = [float(x.strip()) for x in numbers.split(",")]
            total = sum(num_list)
            average = total / len(num_list)
            return f"""Number Analysis:
• Count: {len(num_list)} numbers
• Sum: {total}
• Average: {average:.2f}
• Min: {min(num_list)}
• Max: {max(num_list)}"""
        except Exception as e:
            return f"Error analyzing numbers: {str(e)}"

    # File system tools
    @tool_registry.register_tool("list_directory")
    def list_directory(path: str = ".") -> str:
        try:
            if not os.path.exists(path):
                return f"Directory {path} does not exist"

            items = os.listdir(path)
            files = [i for i in items if os.path.isfile(os.path.join(path, i))]
            dirs = [i for i in items if os.path.isdir(os.path.join(path, i))]
            return f"""Directory: {path}
• Files: {len(files)} ({files[:5]}{"..." if len(files) > 5 else ""})
• Directories: {len(dirs)} ({dirs[:5]}{"..." if len(dirs) > 5 else ""})"""
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    logger.info("Created comprehensive ToolRegistry with tools")
    return tool_registry


# -------------------------------
# Lifespan
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    logger.info("🚀 Initializing OmniAgent for Web Interface...")

    memory_router = MemoryRouter(memory_store_type="in_memory")
    event_router = EventRouter(event_store_type="in_memory")
    tool_registry = await create_comprehensive_tool_registry()

    agent = OmniAgent(
        name="web_interface_agent",
        system_instruction="You are a comprehensive AI assistant with access to many tools.",
        model_config={"provider": "openai", "model": "gpt-4.1", "temperature": 0.3},
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
        agent_config={"max_steps": 15, "tool_call_timeout": 60},
        memory_router=memory_router,
        event_router=event_router,
        debug=True,
    )

    app.state.omniagent = agent
    yield
    # cleanup if needed


# -------------------------------
# FastAPI app
# -------------------------------
app = FastAPI(title="OmniAgent Interface", version="0.0.22", lifespan=lifespan)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static + templates
app.mount("/static", StaticFiles(directory="examples/static"), name="static")
templates = Jinja2Templates(directory="examples/templates")


# -------------------------------
# Routes
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("omni_agent_interface.html", {"request": request})


@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    session_id = (
        data.get("session_id")
        or f"web_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            agent = request.app.state.omniagent
            result = await agent.run(query=message, session_id=session_id)
            response = result.get("response", "No response received")

            for i in range(0, len(response), 50):
                yield f"data: {json.dumps({'type': 'chunk', 'content': response[i : i + 50], 'session_id': session_id})}\n\n"
                await asyncio.sleep(0.1)

            yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e), 'session_id': session_id})}\n\n"

    return StreamingResponse(generate_response(), media_type="text/plain")


@app.get("/tools")
async def get_tools(request: Request):
    agent = request.app.state.omniagent
    return {"tools": agent.local_tools.list_tools()}


@app.get("/history/{session_id}")
async def get_history(session_id: str, request: Request):
    agent = request.app.state.omniagent
    return {"history": await agent.get_session_history(session_id)}


@app.post("/clear-history/{session_id}")
async def clear_history(session_id: str, request: Request):
    agent = request.app.state.omniagent
    await agent.clear_session_history(session_id)
    return {"status": "cleared"}


@app.get("/agent-info")
async def get_agent_info(request: Request):
    agent = request.app.state.omniagent
    return {
        "name": agent.name,
        "memory_router": agent.memory_router.get_memory_store_info(),
        "event_router": agent.get_event_store_info(),
        "tools_count": len(agent.local_tools.list_tools()),
    }


@app.post("/switch-backend")
async def switch_backend(request: Request):
    data = await request.json()
    agent = request.app.state.omniagent
    backend_type, backend_name = data.get("type"), data.get("backend")
    if backend_type == "memory":
        agent.memory_router = MemoryRouter(backend_name)
        return {
            "status": "success",
            "message": f"Memory backend switched to {backend_name}",
        }
    elif backend_type == "event":
        agent.switch_event_store(backend_name)
        return {
            "status": "success",
            "message": f"Event backend switched to {backend_name}",
        }
    return {"status": "error", "message": "Invalid backend type"}


# -------------------------------
# Start server
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
