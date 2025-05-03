from typing import Callable, Optional, Any, List
from mcpomni_connect.agents.base import BaseReactAgent
from mcpomni_connect.utils import logger
from mcpomni_connect.agents.types import AgentConfig
from mcpomni_connect.system_prompts import generate_react_agent_prompt
from mcpomni_connect.constants import date_time_func


# TODO still working on this
class SequentialAgent(BaseReactAgent):
    def __init__(self, config: AgentConfig):
        self.instructions = config.instructions
        self.agent_config = config

        super().__init__(
            config.agent_name,
            config.max_steps,
            config.tool_call_timeout,
            config.mcp_enabled,
        )

    async def run_agent(
        self,
        query: str,
        llm_connection: Callable,
        add_message_to_history: Callable[[str, str, Optional[dict]], Any],
        message_history: Callable[[], Any],
        debug: bool = False,
        **kwargs,
    ):
        system_prompt = generate_react_agent_prompt(
            current_date_time=date_time_func["format_date"](),
            instructions=self.instructions,
        )

        return await self.run(
            system_prompt=system_prompt,
            query=query,
            llm_connection=llm_connection,
            add_message_to_history=add_message_to_history,
            message_history=message_history,
            debug=debug,
            sessions=kwargs.get("sessions"),
            available_tools=kwargs.get("available_tools"),
            tools_registry=kwargs.get("tools_registry"),
            is_generic_agent=False,
        )


class SequentialAgentRunner:
    def __init__(self, agent_configs: List[AgentConfig]):
        self.agents = [SequentialAgent(config) for config in agent_configs]

    async def run_all(
        self,
        initial_query: str,
        llm_connection: Callable,
        add_message_to_history: Callable[[str, str, Optional[dict]], Any],
        message_history: Callable[[], Any],
        debug: bool = False,
        **kwargs,
    ):
        current_query = initial_query
        for agent in self.agents:
            logger.info(f"Running agent: {agent.agent_config.agent_name}")
            current_query = await agent.run_agent(
                query=current_query,
                llm_connection=llm_connection,
                add_message_to_history=add_message_to_history,
                message_history=message_history,
                debug=debug,
                **kwargs,
            )
        return current_query
