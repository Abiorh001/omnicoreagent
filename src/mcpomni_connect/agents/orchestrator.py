from mcpomni_connect.agents.base import BaseReactAgent
from mcpomni_connect.agents.types import AgentConfig
from mcpomni_connect.agents.types import ParsedResponse
from mcpomni_connect.agents.react_agent import ReactAgent
from mcpomni_connect.constants import AGENTS_REGISTRY
from typing import Any, Callable, Optional
import json
from mcpomni_connect.utils import logger
from mcpomni_connect.system_prompts import generate_react_agent_prompt_template
from mcpomni_connect.agents.token_usage import (
    Usage,
    UsageLimitExceeded,
    session_stats,
    usage,
)


class OrchestratorAgent(BaseReactAgent):
    def __init__(
        self,
        config: AgentConfig,
        agents_registry: AGENTS_REGISTRY,
        chat_id: int,
        current_date_time: str,
        debug: bool = False,
    ):
        super().__init__(
            agent_name=config.agent_name,
            max_steps=config.max_steps,
            tool_call_timeout=config.tool_call_timeout,
            request_limit=config.request_limit,
            total_tokens_limit=config.total_tokens_limit,
            mcp_enabled=config.mcp_enabled,
        )
        self.agents_registry = agents_registry
        self.chat_id = chat_id
        self.current_date_time = current_date_time
        self.orchestrator_messages = []
        self.max_steps = 20
        self.debug = debug

    async def extract_action_json(self, response: ParsedResponse):
        action_data = await super().extract_action_json(response=response)
        # Parse the JSON

        try:
            action_json = action_data.get("data")
            action = json.loads(action_json)
            agent_name_to_act = action.get("agent_name")
            # strip away if Agent or agent is part of the agent name
            agent_name_to_act = (
                agent_name_to_act.replace("Agent", "").replace("agent", "").strip()
            )
            task_to_act = action.get("task")
            # if tool_name is None or tool_args is None, return an error
            if agent_name_to_act is None or task_to_act is None:
                return {
                    "error": "Invalid JSON format",
                    "action": False,
                }

            # Validate JSON structure and tool exists
            if "agent_name" in action and "task" in action:
                for (
                    agent_name,
                    agent_description,
                ) in self.agents_registry.items():
                    agent_names = [
                        agent_name.lower() for agent_name in self.agents_registry.keys()
                    ]
                    if agent_name_to_act.lower() in agent_names:
                        return {
                            "action": True,
                            "agent_name": agent_name_to_act,
                            "task": task_to_act,
                        }
            logger.warning("Agent not found: %s", agent_name_to_act)
            return {
                "action": False,
                "error": f"Agent {agent_name_to_act} not found",
            }
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON format",
                "action": False,
            }

    async def create_agent_system_prompt(
        self,
        agent_name: str,
        available_tools: dict[str, Any],
    ) -> str:
        server_name = agent_name
        agent_role = self.agents_registry[server_name]
        agent_system_prompt = generate_react_agent_prompt_template(
            agent_role_prompt=agent_role,
            current_date_time=self.current_date_time,
        )
        return agent_system_prompt

    async def update_llm_working_memory(self, message_history: Callable[[], Any]):
        """Update the LLM's working memory with the current message history"""
        short_term_memory_message_history = await message_history(
            agent_name="orchestrator", chat_id=self.chat_id
        )

        for _, message in enumerate(short_term_memory_message_history):
            if message["role"] == "user":
                # append all the user messages in the message history to the messages that will be sent to LLM
                self.orchestrator_messages.append(
                    {"role": "user", "content": message["content"]}
                )

            elif message["role"] == "assistant":
                # Add all the assistant messages in the message history to the messages that will be sent to LLM
                self.orchestrator_messages.append(
                    {"role": "assistant", "content": message["content"]}
                )

            elif message["role"] == "system":
                # add only the system message to the messages that will be sent to LLM.
                # it will be the first message sent to LLM and only one at all times
                self.orchestrator_messages.append(
                    {"role": "system", "content": message["content"]}
                )

    async def act(
        self,
        sessions: dict,
        agent_name: str,
        task: str,
        add_message_to_history: Callable[[str, str, Optional[dict]], Any],
        llm_connection: Callable,
        available_tools: dict[str, Any],
        message_history: Callable[[], Any],
        tool_call_timeout: int,
        max_steps: int,
        request_limit: int,
        total_tokens_limit: int,
    ) -> str:
        """Execute agent and return JSON-formatted observation"""
        try:
            agent_system_prompt = await self.create_agent_system_prompt(
                agent_name=agent_name,
                available_tools=available_tools,
            )
            logger.info(f"request limit: {request_limit}")
            agent_config = AgentConfig(
                agent_name=agent_name,
                tool_call_timeout=tool_call_timeout,
                max_steps=max_steps,
                request_limit=request_limit,
                total_tokens_limit=total_tokens_limit,
                mcp_enabled=True,
            )
            extra_kwargs = {
                "sessions": sessions,
                "available_tools": available_tools,
                "tools_registry": None,
                "is_generic_agent": False,
                "chat_id": self.chat_id,
            }
            react_agent = ReactAgent(config=agent_config)
            observation = await react_agent._run(
                system_prompt=agent_system_prompt,
                query=task,
                llm_connection=llm_connection,
                add_message_to_history=add_message_to_history,
                message_history=message_history,
                debug=self.debug,
                **extra_kwargs,
            )

            # if the observation is empty return general error message
            if not observation:
                observation = "No observation available right now. try again later. or try a different agent."
            # add the observation to the orchestrator messages and the message history
            self.orchestrator_messages.append(
                {
                    "role": "user",
                    "content": f"{agent_name} Agent Observation:\n{observation}",
                }
            )
            await add_message_to_history(
                agent_name="orchestrator",
                role="user",
                content=f"{agent_name} Agent Observation:\n{observation}",
                chat_id=self.chat_id,
            )
            return observation
        except Exception as e:
            logger.error("Error executing agent: %s", str(e))

    async def agent_registry_tool(self, available_tools: dict[str, Any]) -> str:
        """
        This function is used to create a tool that will return the agent registry
        """
        agent_registries = []
        for server_name, tools in available_tools.items():
            agent_entry = {
                "agent_name": server_name,
                "agent_description": self.agents_registry[server_name],
                "capabilities": [],
            }
            for tool in tools:
                name = str(tool.name) if tool.name else "No Name available"
                agent_entry["capabilities"].append(name)
            agent_registries.append(agent_entry)
        return "\n".join(
            [
                "### Agent Registry",
                "| Agent Name     | Description                         | Capabilities                     |",
                "|----------------|-------------------------------------|----------------------------------|",
                *[
                    f"| {entry['agent_name']} | {entry['agent_description']} | {', '.join(entry['capabilities'])} |"
                    for entry in agent_registries
                ],
            ]
        )

    async def run(
        self,
        sessions: dict,
        query: str,
        add_message_to_history: Callable[[str, str, Optional[dict]], Any],
        llm_connection: Callable,
        available_tools: dict[str, Any],
        message_history: Callable[[], Any],
        orchestrator_system_prompt: str,
        tool_call_timeout: int,
        max_steps: int,
        request_limit: int,
        total_tokens_limit: int,
    ) -> Optional[str]:
        """Execute ReAct loop with JSON communication"""
        # Initialize messages with system prompt
        self.orchestrator_messages = [
            {"role": "system", "content": orchestrator_system_prompt}
        ]

        # Add initial user message to message history
        await add_message_to_history(
            agent_name="orchestrator", role="user", content=query, chat_id=self.chat_id
        )
        await self.update_llm_working_memory(message_history)
        agent_registry_output = await self.agent_registry_tool(available_tools)
        self.orchestrator_messages.append(
            {
                "role": "assistant",
                "content": f"This is the list of agents and their capabilities **AgentsRegistryObservation**:\n\n{agent_registry_output}",
            }
        )
        current_steps = 0
        while current_steps < self.max_steps:
            current_steps += 1
            self.usage_limits.check_before_request(usage=usage)
            try:
                if self.debug:
                    logger.info(
                        f"Sending {len(self.orchestrator_messages)} messages to LLM"
                    )
                response = await llm_connection.llm_call(self.orchestrator_messages)
                if response:
                    # check if it has usage
                    if hasattr(response, "usage"):
                        request_usage = Usage(
                            requests=current_steps,
                            request_tokens=response.usage.prompt_tokens,
                            response_tokens=response.usage.completion_tokens,
                            total_tokens=response.usage.total_tokens,
                        )
                        usage.incr(request_usage)
                        # Check if we've exceeded token limits
                        self.usage_limits.check_tokens(usage)
                        # Show remaining resources
                        remaining_tokens = self.usage_limits.remaining_tokens(usage)
                        used_tokens = usage.total_tokens
                        used_requests = usage.requests
                        remaining_requests = self.request_limit - used_requests
                        session_stats.update(
                            {
                                "used_requests": used_requests,
                                "used_tokens": used_tokens,
                                "remaining_requests": remaining_requests,
                                "remaining_tokens": remaining_tokens,
                                "request_tokens": request_usage.request_tokens,
                                "response_tokens": request_usage.response_tokens,
                                "total_tokens": request_usage.total_tokens,
                            }
                        )
                        if self.debug:
                            logger.info(
                                f"API Call Stats - Requests: {used_requests}/{self.request_limit}, "
                                f"Tokens: {used_tokens}/{self.usage_limits.total_tokens_limit}, "
                                f"Request Tokens: {request_usage.request_tokens}, "
                                f"Response Tokens: {request_usage.response_tokens}, "
                                f"Total Tokens: {request_usage.total_tokens}, "
                                f"Remaining Requests: {remaining_requests}, "
                                f"Remaining Tokens: {remaining_tokens}"
                            )
                    if hasattr(response, "choices"):
                        response = response.choices[0].message.content.strip()
                    elif hasattr(response, "message"):
                        response = response.message.content.strip()
            except UsageLimitExceeded as e:
                error_message = f"Usage limit error: {e}"
                logger.error(error_message)
                return error_message
            except Exception as e:
                error_message = f"API error: {e}"
                logger.error(error_message)
                return error_message

            parsed_response = await self.extract_action_or_answer(
                response=response, debug=self.debug
            )
            # check for final answe
            if parsed_response.answer is not None:
                # add the final answer to the message history and the messages that will be sent to LLM
                self.orchestrator_messages.append(
                    {
                        "role": "assistant",
                        "content": parsed_response.answer,
                    }
                )
                await add_message_to_history(
                    agent_name="orchestrator",
                    role="assistant",
                    content=parsed_response.answer,
                    chat_id=self.chat_id,
                )
                # reset the steps
                current_steps = 0
                return parsed_response.answer

            elif parsed_response.action is not None:
                extract_action_json_data = await self.extract_action_json(
                    response=response
                )
                await self.act(
                    sessions=sessions,
                    agent_name=extract_action_json_data["agent_name"],
                    task=extract_action_json_data["task"],
                    add_message_to_history=add_message_to_history,
                    llm_connection=llm_connection,
                    available_tools=available_tools,
                    message_history=message_history,
                    max_steps=max_steps,
                    tool_call_timeout=tool_call_timeout,
                    total_tokens_limit=total_tokens_limit,
                    request_limit=request_limit,
                )
                continue
            elif parsed_response.error is not None:
                error_message = parsed_response.error
            else:
                # append the invalid response to the messages and the message history
                error_message = (
                    "Invalid response format. Please use the correct required format"
                )
            self.orchestrator_messages.append(
                {
                    "role": "user",
                    "content": f"Error: {error_message}",
                }
            )
            await add_message_to_history(
                agent_name="orchestrator",
                role="user",
                content=error_message,
                chat_id=self.chat_id,
            )
