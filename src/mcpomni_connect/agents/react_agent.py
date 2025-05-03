from typing import Callable, Optional, Any
from mcpomni_connect.agents.base import BaseReactAgent
from mcpomni_connect.agents.types import AgentConfig


class ReactAgent(BaseReactAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(
            agent_name=config.agent_name,
            max_steps=config.max_steps,
            tool_call_timeout=config.tool_call_timeout,
            request_limit=config.request_limit,
            total_tokens_limit=config.total_tokens_limit,
            mcp_enabled=config.mcp_enabled,
        )

    async def _run(
        self,
        system_prompt: str,
        query: str,
        llm_connection: Callable,
        add_message_to_history: Callable[[str, str, Optional[dict]], Any],
        message_history: Callable[[], Any],
        debug: bool = False,
        **kwargs,
    ):
        response = await self.run(
            system_prompt=system_prompt,
            query=query,
            llm_connection=llm_connection,
            add_message_to_history=add_message_to_history,
            message_history=message_history,
            debug=debug,
            sessions=kwargs.get("sessions"),
            available_tools=kwargs.get("available_tools"),
            tools_registry=kwargs.get("tools_registry"),
            is_generic_agent=kwargs.get("is_generic_agent"),
            chat_id=kwargs.get("chat_id"),
        )
        return response
