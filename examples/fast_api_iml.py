#!/usr/bin/env python3
"""
FastAPI Server with OmniAgent

This example shows how to integrate OmniAgent with FastAPI for web-based AI interactions.
Provides RESTful API endpoints for chat, events, and resource management.
"""

import datetime
import json
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# TOP-LEVEL IMPORTS (Recommended for most use cases)
from omnicoreagent import OmniAgent, MemoryRouter, EventRouter, logger

# LOW-LEVEL IMPORTS (Alternative approach for advanced users)
# from omnicoreagent.omni_agent import OmniAgent
# from omnicoreagent.core.memory_store.memory_router import MemoryRouter
# from omnicoreagent.core.events.event_router import EventRouter
# from omnicoreagent.core.utils import logger


class OmniAgentServer:
    """FastAPI server wrapper for OmniAgent with web-friendly interfaces."""

    def __init__(self):
        """Initialize the OmniAgent server."""

        # Create memory and event routers
        self.memory_store = MemoryRouter(memory_store_type="mongodb")
        self.event_router = EventRouter(event_store_type="database")

        # Create the OmniAgent
        self.agent = OmniAgent(
            name="fastapi_agent",
            system_instruction="""You are a helpful AI assistant integrated with a web API.
            You can help users with various tasks including answering questions,
            file operations, and other tool-based interactions.
            Always provide clear, helpful responses suitable for web interfaces.""",
            model_config={
                "provider": "openai",  # Change to your preferred provider
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_context_length": 5000,
            },
            mcp_tools=[
                {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        str(Path.home()),  # Access user's home directory
                    ],
                }
            ],
            agent_config={
                "max_steps": 15,
                "tool_call_timeout": 60,
                "request_limit": 1000,
                "memory_config": {"mode": "sliding_window", "value": 80000},
            },
            memory_store=self.memory_store,
            event_router=self.event_router,
            debug=True,
        )

    async def handle_query(self, query: str, session_id: str = None) -> dict:
        """Handle a user query and return the agent's response.

        Args:
            query: User's query/message
            session_id: Optional session ID for conversation continuity

        Returns:
            Dict with response and session_id
        """
        try:
            logger.info(f"Processing query: {query[:50]}...")

            # Run the agent
            result = await self.agent.run(query, session_id)

            logger.info(f"Response generated for session: {result['session_id']}")
            return result

        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "session_id": session_id or "error_session",
            }

    async def handle_resource_query(
        self, resource_uri: str, session_id: str = None
    ) -> str:
        """Handle a resource-specific query.

        Args:
            resource_uri: URI of the resource to query
            session_id: Optional session ID

        Returns:
            Resource content or error message
        """
        try:
            # For resource queries, we can use the agent to process the resource
            query = f"Please read and provide information about the resource: {resource_uri}"
            result = await self.handle_query(query, session_id)
            return result["response"]
        except Exception as e:
            logger.error(f"Failed to process resource query: {e}")
            return f"Error processing resource: {str(e)}"

    async def list_available_resources(self) -> dict:
        """List available resources (simplified for demo)."""
        try:
            # Use the agent to help list available resources
            query = "Can you show me what files and directories are available in the current working area?"
            result = await self.handle_query(query)
            return {
                "status": "success",
                "message": "Available resources listed via agent",
                "response": result["response"],
            }
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            return {"status": "error", "message": f"Error listing resources: {str(e)}"}

    async def get_session_history(self, session_id: str) -> list[dict]:
        """Get conversation history for a session."""
        try:
            return await self.agent.get_session_history(session_id)
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []

    async def clear_session_memory(self, session_id: str) -> bool:
        """Clear memory for a specific session."""
        try:
            await self.agent.clear_session_history(session_id)
            logger.info(f"Cleared memory for session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear session memory: {e}")
            return False

    def get_agent_info(self) -> dict:
        """Get information about the agent configuration."""
        return {
            "agent_name": self.agent.name,
            "memory_store_type": "in_memory",
            "memory_store_info": self.memory_store.get_memory_store_info(),
            "event_store_type": self.agent.get_event_store_type(),
            "debug_mode": self.agent.debug,
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code executes before the application starts
    logger.info("Initializing OmniAgent server...")

    try:
        app.state.agent_server = OmniAgentServer()
        logger.info("OmniAgent server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OmniAgent server: {e}")
        raise

    yield  # The application runs here

    # This code executes when the application is shutting down
    logger.info("Shutting down OmniAgent server...")
    if hasattr(app.state, "agent_server"):
        # Cleanup if needed
        logger.info("OmniAgent server shut down successfully")


# Initialize FastAPI with the lifespan
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def format_msg(usid, msg, meta, message_id, role="assistant"):
    response_message = {
        "message_id": message_id,
        "usid": usid,
        "role": role,
        "content": msg,
        "meta": meta,
        "likeordislike": None,
        "time": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    }
    return response_message


@app.get("/events/{session_id}")
async def stream_events(request: Request, session_id: str):
    """Stream events for a specific session."""

    async def event_generator():
        try:
            async for event in request.app.state.agent_server.agent.stream_events(
                session_id
            ):
                yield f"event: {event.type}\ndata: {event.json()}\n\n"
        except Exception as e:
            logger.error(f"Error streaming events: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def chat_endpoint(request: Request, user_input: str, session_id: str):
    """Handle chat endpoint with streaming response."""
    assistant_uuid = str(uuid.uuid4())
    try:
        result = await request.app.state.agent_server.handle_query(
            query=user_input, session_id=session_id
        )

        yield (
            json.dumps(
                format_msg("ksa", result["response"], [], assistant_uuid, "assistant")
            ).encode("utf-8")
            + b"\n"
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        yield (
            json.dumps(
                format_msg("ksa", str(e), [], str(uuid.uuid4()), "error")
            ).encode("utf-8")
            + b"\n"
        )


async def stream_resource(request: Request, resource_uri: str, session_id: str):
    """Handle resource streaming."""
    try:
        response = await request.app.state.agent_server.handle_resource_query(
            resource_uri=resource_uri, session_id=session_id
        )

        # Return as a simple generator
        async def response_generator():
            yield response.encode("utf-8")

        return response_generator()
    except Exception as e:
        logger.error(f"Error processing resource: {e}")
        error_msg = str(e)

        async def error_generator():
            yield f"Error: {error_msg}".encode("utf-8")

        return error_generator()


class ChatInput(BaseModel):
    query: str = Form(...)
    chat_id: str


@app.post("/chat/agent_chat")
async def chat(request: Request, chat_input: ChatInput):
    """Main chat endpoint supporting both regular queries and resource queries."""
    if chat_input.query.startswith("resource:"):
        resource_uri = chat_input.query.split("resource:")[1].strip()
        response = await stream_resource(
            request=request, resource_uri=resource_uri, session_id=chat_input.chat_id
        )
        return StreamingResponse(response, media_type="text/plain")
    else:
        logger.info(f"Received query: {chat_input.query}")
        return StreamingResponse(
            chat_endpoint(
                request=request,
                user_input=chat_input.query,
                session_id=chat_input.chat_id,
            ),
            media_type="text/plain",
        )


@app.get("/resources")
async def list_resources_endpoint(request: Request):
    """List available resources."""
    response = await request.app.state.agent_server.list_available_resources()
    return response


@app.get("/session/{session_id}/history")
async def get_session_history(request: Request, session_id: str):
    """Get conversation history for a specific session."""
    try:
        history = await request.app.state.agent_server.get_session_history(session_id)
        return {
            "status": "success",
            "session_id": session_id,
            "history": history,
            "message_count": len(history),
        }
    except Exception as e:
        logger.error(f"Error getting session history: {e}")
        return {"status": "error", "message": str(e)}


@app.delete("/session/{session_id}/memory")
async def clear_session_memory(request: Request, session_id: str):
    """Clear memory for a specific session."""
    try:
        success = await request.app.state.agent_server.clear_session_memory(session_id)
        return {
            "status": "success" if success else "error",
            "session_id": session_id,
            "message": "Memory cleared successfully"
            if success
            else "Failed to clear memory",
        }
    except Exception as e:
        logger.error(f"Error clearing session memory: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/agent/info")
async def get_agent_info(request: Request):
    """Get information about the agent configuration."""
    try:
        info = request.app.state.agent_server.get_agent_info()
        return {"status": "success", "agent_info": info}
    except Exception as e:
        logger.error(f"Error getting agent info: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
