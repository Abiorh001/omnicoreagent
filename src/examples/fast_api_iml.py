import json
from contextlib import asynccontextmanager
from mcpomni_connect.client import Configuration, MCPClient
from mcpomni_connect.llm import LLMConnection
from fastapi import FastAPI, Form, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import datetime
from mcpomni_connect.constants import AGENTS_REGISTRY, date_time_func, logger
from mcpomni_connect.memory import (
    InMemoryShortTermMemory,
)
from mcpomni_connect.system_prompts import (
    generate_orchestrator_prompt_template,
    generate_react_agent_prompt,
)
from pydantic import BaseModel
from mcpomni_connect.agents.orchestrator import OrchestratorAgent
from mcpomni_connect.agents.react_agent import ReactAgent
from mcpomni_connect.agents.types import AgentConfig


class MCPClientConnect:
    def __init__(self, client: MCPClient, llm_connection: LLMConnection):
        self.client = client
        self.llm_connection = llm_connection
        self.MAX_CONTEXT_TOKENS = self.llm_connection.config.load_config(
            "servers_config.json"
        )["LLM"]["max_context_length"]
        self.MODE = {"auto": True, "chat": False, "orchestrator": False}
        self.client.debug = True
        self.in_memory_short_term_memory = InMemoryShortTermMemory(
            max_context_tokens=self.MAX_CONTEXT_TOKENS
        )

    async def handle_query(self, query: str, chat_id: str = None):
        agent_config = AgentConfig(
            agent_name="react_agent",
            tool_call_timeout=30,
            max_steps=15,
            request_limit=100,
            total_tokens_limit=1000000,
            mcp_enabled=True,
        )
        logger.info(f"agent config: {agent_config}")
        if self.MODE["auto"]:
            react_agent_prompt = generate_react_agent_prompt(
                current_date_time=date_time_func["format_date"]()
            )

            extra_kwargs = {
                "sessions": self.client.sessions,
                "available_tools": self.client.available_tools,
                "is_generic_agent": True,
                "chat_id": chat_id,
            }
            react_agent = ReactAgent(config=agent_config)

            response = await react_agent._run(
                system_prompt=react_agent_prompt,
                query=query,
                llm_connection=self.llm_connection,
                add_message_to_history=(self.in_memory_short_term_memory.store_message),
                message_history=(self.in_memory_short_term_memory.get_messages),
                debug=self.client.debug,
                **extra_kwargs,
            )
        elif self.MODE["orchestrator"]:
            # initialize the orchestrator agent in memory
            orchestrator_agent_prompt = generate_orchestrator_prompt_template(
                current_date_time=date_time_func["format_date"]()
            )

            orchestrator_agent = OrchestratorAgent(
                config=agent_config,
                agents_registry=AGENTS_REGISTRY,
                chat_id=chat_id,
                current_date_time=date_time_func["format_date"](),
                debug=self.client.debug,
            )
            response = await orchestrator_agent.run(
                query=query,
                sessions=self.client.sessions,
                add_message_to_history=(self.in_memory_short_term_memory.store_message),
                llm_connection=self.llm_connection,
                available_tools=self.client.available_tools,
                message_history=(self.in_memory_short_term_memory.get_messages),
                orchestrator_system_prompt=orchestrator_agent_prompt,
                tool_call_timeout=30,
                max_steps=15,
                request_limit=100,
                total_tokens_limit=1000000,
            )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code executes before the application starts
    app.state.client = None
    app.state.client_connection = None
    config = Configuration()
    app.state.client = MCPClient(config)
    app.state.client.debug = True
    app.state.llm_connection = LLMConnection(config)
    app.state.client_connection = MCPClientConnect(
        client=app.state.client, llm_connection=app.state.llm_connection
    )
    logger.info("Initializing MCP client...")

    # Connect to servers
    await app.state.client.connect_to_servers()

    logger.info("MCP client initialized successfully")

    yield  # The application runs here

    # This code executes when the application is shutting down
    logger.info("Shutting down MCP client...")
    if app.state.client:
        await app.state.client.cleanup()
    logger.info("MCP client shut down successfully")


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


async def chat_endpoint(request: Request, user_input: str, chat_id: str):
    assistant_uuid = str(uuid.uuid4())
    try:
        response = await request.app.state.client_connection.handle_query(
            query=user_input, chat_id=chat_id
        )
        yield (
            json.dumps(
                format_msg("ksa", response, [], assistant_uuid, "assistant")
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


class ChatInput(BaseModel):
    query: str = Form(...)
    chat_id: str


@app.post("/chat/agent_chat")
async def chat(request: Request, chat_input: ChatInput):
    logger.info(f"Received query: {chat_input.query}")
    return StreamingResponse(
        chat_endpoint(
            request=request, user_input=chat_input.query, chat_id=chat_input.chat_id
        ),
        media_type="text/plain",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
