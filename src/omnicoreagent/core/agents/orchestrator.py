from collections.abc import Callable
from typing import Any

from omnicoreagent.core.agents.base import BaseReactAgent
from omnicoreagent.core.agents.react_agent import ReactAgent
from omnicoreagent.core.agents.token_usage import (
    Usage,
    UsageLimitExceeded,
    session_stats,
    usage,
)
from omnicoreagent.core.agents.types import AgentConfig, ParsedResponse
from omnicoreagent.core.constants import AGENTS_REGISTRY
from omnicoreagent.core.system_prompts import generate_react_agent_prompt_template
from omnicoreagent.core.utils import logger, track
import json
import re
from omnicoreagent.core.events.base import (
    Event,
    EventType,
    UserMessagePayload,
    AgentMessagePayload,
    ToolCallErrorPayload,
    ToolCallResultPayload,
    FinalAnswerPayload,
    ToolCallStartedPayload,
)


class OrchestratorAgent(BaseReactAgent):
    def __init__(
        self,
        config: AgentConfig,
        agents_registry: AGENTS_REGISTRY,
        current_date_time: str,
        debug: bool = False,
    ):
        super().__init__(
            agent_name=config.agent_name,
            max_steps=config.max_steps,
            tool_call_timeout=config.tool_call_timeout,
            request_limit=config.request_limit,
            total_tokens_limit=config.total_tokens_limit,
            memory_results_limit=config.memory_results_limit,
            memory_similarity_threshold=config.memory_similarity_threshold,
        )
        self.agents_registry = agents_registry
        self.current_date_time = current_date_time
        self.orchestrator_messages = []
        self.max_steps = 20
        self.debug = debug

    @track("extract_action_or_answer")
    async def extract_action_or_answer(
        self,
        response: str,
        debug: bool = False,
    ) -> ParsedResponse:
        """Override to prevent orchestrator from parsing tool calls from sub-agents."""
        # Orchestrator should only parse agent calls and final answers, not tool calls
        return await self.extract_agent_action_or_answer(response, debug)

    @track("extract_agent_action_or_answer")
    async def extract_agent_action_or_answer(
        self,
        response: str,
        debug: bool = False,
    ) -> ParsedResponse:
        """Parse LLM response to extract XML-formatted agent calls or final answers."""
        try:
            # Check for XML-style agent call format
            if "<agent_call>" in response and "</agent_call>" in response:
                if debug:
                    logger.info(
                        "XML agent call format detected in response: %s", response
                    )
                agent_name_match = re.search(
                    r"<agent_name>(.*?)</agent_name>", response, re.DOTALL
                )
                task_match = re.search(r"<task>(.*?)</task>", response, re.DOTALL)
                if agent_name_match and task_match:
                    agent_name = agent_name_match.group(1).strip()
                    task = task_match.group(1).strip()
                    # strip away if Agent or agent is part of the agent name
                    agent_name = (
                        agent_name.replace("Agent", "").replace("agent", "").strip()
                    )

                    # Validate agent exists in registry
                    agent_names = [name.lower() for name in self.agents_registry.keys()]
                    if agent_name.lower() in agent_names:
                        action_json = json.dumps(
                            {"agent_name": agent_name, "task": task}
                        )
                        return ParsedResponse(action=True, data=action_json)
                    else:
                        logger.warning("Agent not found: %s", agent_name)
                        return ParsedResponse(error=f"Agent {agent_name} not found")
                else:
                    return ParsedResponse(
                        error="Invalid XML agent call format - missing agent_name or task"
                    )

            # Check for XML-style final answer format
            if "<final_answer>" in response and "</final_answer>" in response:
                if debug:
                    logger.info(
                        "XML final answer format detected in response: %s", response
                    )
                final_answer_match = re.search(
                    r"<final_answer>(.*?)</final_answer>", response, re.DOTALL
                )
                if final_answer_match:
                    answer = final_answer_match.group(1).strip()
                    return ParsedResponse(answer=answer)
                else:
                    return ParsedResponse(error="Invalid XML final answer format")

            # If no XML tags found, treat as conversational response (likely final answer after agent observation)
            if debug:
                logger.info(
                    "No XML tags found, treating as conversational response: %s",
                    response,
                )
            return ParsedResponse(answer=response.strip())

        except Exception as e:
            logger.error("Error parsing model response: %s", str(e))
            return ParsedResponse(error=str(e))

    @track("create_agent_system_prompt")
    async def create_agent_system_prompt(
        self,
        agent_name: str,
        mcp_tools: dict[str, Any],
    ) -> str:
        server_name = agent_name
        agent_role = self.agents_registry[server_name]
        agent_system_prompt = generate_react_agent_prompt_template(
            agent_role_prompt=agent_role,
            current_date_time=self.current_date_time,
        )
        return agent_system_prompt

    @track("update_llm_working_memory")
    async def update_llm_working_memory(
        self, message_history: Callable[[], Any], session_id: str
    ):
        """Update the LLM's working memory with the current message history"""
        short_term_memory_message_history = await message_history(
            agent_name="orchestrator", session_id=session_id
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

    @track("act")
    async def act(
        self,
        sessions: dict,
        agent_name: str,
        task: str,
        add_message_to_history: Callable[[str, str, dict | None], Any],
        llm_connection: Callable,
        mcp_tools: dict[str, Any],
        message_history: Callable[[], Any],
        tool_call_timeout: int,
        max_steps: int,
        request_limit: int,
        total_tokens_limit: int,
        session_id: str,
        event_router: Callable[[str, Event], Any] = None,  # Event router callable
    ) -> str:
        """Execute agent and return JSON-formatted observation"""
        try:

            @track("agent_system_prompt_creation")
            async def create_prompt():
                return await self.create_agent_system_prompt(
                    agent_name=agent_name,
                    mcp_tools=mcp_tools,
                )

            agent_system_prompt = await create_prompt()

            # tool call start event
            @track("tool_call_event_creation")
            async def create_tool_call_event():
                event = Event(
                    type=EventType.TOOL_CALL_STARTED,
                    payload=ToolCallStartedPayload(
                        tool_name=agent_name,
                        tool_args={"task": task},
                        tool_call_id=None,
                    ),
                    agent_name="orchestrator",
                )
                if event_router:
                    await event_router(session_id=session_id, event=event)

            await create_tool_call_event()

            @track("agent_config_creation")
            def create_agent_config():
                return AgentConfig(
                    agent_name=agent_name,
                    tool_call_timeout=tool_call_timeout,
                    max_steps=max_steps,
                    request_limit=request_limit,
                    total_tokens_limit=total_tokens_limit,
                )

            agent_config = create_agent_config()

            extra_kwargs = {
                "sessions": sessions,
                "mcp_tools": mcp_tools,
                "session_id": session_id,
            }
            react_agent = ReactAgent(config=agent_config)

            @track("react_agent_execution")
            async def execute_react_agent():
                return await react_agent._run(
                    system_prompt=agent_system_prompt,
                    query=task,
                    llm_connection=llm_connection,
                    add_message_to_history=add_message_to_history,
                    message_history=message_history,
                    debug=self.debug,
                    event_router=event_router,  # Pass event_router callable
                    **extra_kwargs,
                )

            observation = await execute_react_agent()

            # if the observation is empty return general error message
            if not observation:
                observation = "No observation available right now. try again later. or try a different agent."

            # add the observation to the orchestrator messages and the message history
            @track("observation_message_update")
            async def update_observation_messages():
                self.orchestrator_messages.append(
                    {
                        "role": "user",
                        "content": f"{agent_name} Agent Observation:\n{observation}",
                    }
                )
                await add_message_to_history(
                    role="user",
                    content=f"{agent_name} Agent Observation:\n{observation}",
                    session_id=session_id,
                    metadata={"agent_name": agent_name},
                )

            await update_observation_messages()
            return observation
        except Exception as e:
            logger.error("Error executing agent: %s", str(e))
            # tool call error event
            event = Event(
                type=EventType.TOOL_CALL_ERROR,
                payload=ToolCallErrorPayload(
                    tool_name="orchestrator",
                    error_message=str(e),
                ),
                agent_name="orchestrator",
            )
            if event_router:
                await event_router(session_id=session_id, event=event)
            return str(e)

    @track("agent_registry_tool")
    async def agent_registry_tool(self, mcp_tools: dict[str, Any]) -> str:
        """
        This function is used to create a tool that will return the agent registry
        """
        try:
            agent_registries = []
            for server_name, tools in mcp_tools.items():
                if server_name not in self.agents_registry:
                    logger.warning(f"No agent registry entry for {server_name}")
                    continue
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
                    "| Agent Name     | Description                         | Capabilities                     |",
                    "|----------------|-------------------------------------|----------------------------------|",
                    *[
                        f"| {entry['agent_name']} | {entry['agent_description']} | {', '.join(entry['capabilities'])} |\n\n"
                        for entry in agent_registries
                    ],
                ]
            )
        except Exception as e:
            logger.info(f"Agent registry error: {e}")
            return e

    @track("run")
    async def run(
        self,
        sessions: dict,
        query: str,
        add_message_to_history: Callable[[str, str, dict | None], Any],
        llm_connection: Callable,
        mcp_tools: dict[str, Any],
        message_history: Callable[[], Any],
        orchestrator_system_prompt: str,
        tool_call_timeout: int,
        max_steps: int,
        request_limit: int,
        total_tokens_limit: int,
        session_id: str,
        event_router: Callable[[str, Event], Any] = None,  # Event router callable
    ) -> str | None:
        """Execute ReAct loop with XML communication"""
        # Emit user message event
        event = Event(
            type=EventType.USER_MESSAGE,
            payload=UserMessagePayload(message=query),
            agent_name="orchestrator",
        )
        if event_router:
            await event_router(session_id=session_id, event=event)
        # Initialize messages with system prompt
        agent_registry_output = await self.agent_registry_tool(mcp_tools)
        updated_systm_prompt = (
            orchestrator_system_prompt
            + f"[AVAILABLE AGENTS REGISTRY]\n\n{agent_registry_output}"
        )
        self.orchestrator_messages = [
            {"role": "system", "content": updated_systm_prompt}
        ]

        # Add initial user message to message history
        await add_message_to_history(
            role="user",
            content=query,
            session_id=session_id,
            metadata={"agent_name": "orchestrator"},
        )
        await self.update_llm_working_memory(message_history, session_id)
        current_steps = 0
        while current_steps < self.max_steps:
            current_steps += 1
            if self._limits_enabled:
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
                # Emit error event
                if event_router:
                    await event_router(session_id=session_id, event=event)
                return error_message

            parsed_response = await self.extract_agent_action_or_answer(
                response=response, debug=self.debug
            )
            # check for final answer
            if parsed_response.answer is not None:
                # add the final answer to the message history and the messages that will be sent to LLM
                self.orchestrator_messages.append(
                    {
                        "role": "assistant",
                        "content": parsed_response.answer,
                    }
                )
                await add_message_to_history(
                    role="assistant",
                    content=parsed_response.answer,
                    session_id=session_id,
                    metadata={"agent_name": "orchestrator"},
                )
                # Emit final answer event
                event = Event(
                    type=EventType.FINAL_ANSWER,
                    payload=FinalAnswerPayload(message=parsed_response.answer),
                    agent_name="orchestrator",
                )
                if event_router:
                    await event_router(session_id=session_id, event=event)
                # reset the steps
                current_steps = 0
                return parsed_response.answer

            elif parsed_response.action is not None:
                # Parse the action data from the XML response
                action_data = json.loads(parsed_response.data)
                # Emit agent call event
                event = Event(
                    type=EventType.AGENT_MESSAGE,
                    payload=AgentMessagePayload(
                        message=f"Dispatching to agent: {action_data['agent_name']} with task: {action_data['task']}"
                    ),
                    agent_name="orchestrator",
                )
                if event_router:
                    await event_router(session_id=session_id, event=event)
                # Call the agent and emit observation event after
                observation = await self.act(
                    sessions=sessions,
                    agent_name=action_data["agent_name"],
                    task=action_data["task"],
                    add_message_to_history=add_message_to_history,
                    llm_connection=llm_connection,
                    mcp_tools=mcp_tools,
                    message_history=message_history,
                    max_steps=max_steps,
                    tool_call_timeout=tool_call_timeout,
                    total_tokens_limit=total_tokens_limit,
                    request_limit=request_limit,
                    session_id=session_id,
                    event_router=event_router,  # Pass event_router callable
                )
                # Ensure observation is a string for event payload
                if not isinstance(observation, str):
                    observation = str(observation)
                # Emit agent observation event
                event = Event(
                    type=EventType.TOOL_CALL_RESULT,
                    payload=ToolCallResultPayload(
                        tool_name=action_data["agent_name"],
                        tool_args={"task": action_data["task"]},
                        result=observation,
                        tool_call_id=None,
                    ),
                    agent_name="orchestrator",
                )
                if event_router:
                    await event_router(session_id=session_id, event=event)
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
                role="user",
                content=error_message,
                session_id=session_id,
                metadata={"agent_name": "orchestrator"},
            )
