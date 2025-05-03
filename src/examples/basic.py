import asyncio
from mcpomni_connect.client import Configuration, MCPClient
from mcpomni_connect.llm import LLMConnection
from mcpomni_connect.system_prompts import (
    generate_orchestrator_prompt_template,
    generate_react_agent_prompt,
)
from mcpomni_connect.agents.orchestrator import OrchestratorAgent
from mcpomni_connect.constants import AGENTS_REGISTRY, date_time_func, logger
from mcpomni_connect.memory import (
    InMemoryShortTermMemory,
)
from mcpomni_connect.agents.react_agent import ReactAgent
from mcpomni_connect.agents.types import AgentConfig
from uuid import uuid4


class MCPClientConnect:
    def __init__(self, client: MCPClient, llm_connection: LLMConnection):
        self.client = client
        self.llm_connection = llm_connection
        self.MAX_CONTEXT_TOKENS = self.llm_connection.config.load_config(
            "servers_config.json"
        )["LLM"]["max_context_length"]
        self.MODE = {"auto": False, "chat": False, "orchestrator": True}
        self.client.debug = True
        self.in_memory_short_term_memory = InMemoryShortTermMemory(
            max_context_tokens=self.MAX_CONTEXT_TOKENS
        )

    async def handle_query(self, query: str):
        chat_id = str(uuid4())
        agent_config = AgentConfig(
            agent_name="react_agent",
            tool_call_timeout=30,
            max_steps=15,
            request_limit=100,
            total_tokens_limit=1000000,
            mcp_enabled=True,
        )
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


logger.info("Initializing MCP client...")
config = Configuration()
client = MCPClient(config)
client.debug = True
llm_connection = LLMConnection(config)
client_connection = MCPClientConnect(client=client, llm_connection=llm_connection)

# Connect to servers


async def chat_loop():
    await client.connect_to_servers()
    while True:
        user_input = input("Enter your query: ")
        if user_input.lower() in ("quit", "exit"):
            break
        response = await client_connection.handle_query(query=user_input)
        print(f"Response: {response}")


asyncio.run(chat_loop())
