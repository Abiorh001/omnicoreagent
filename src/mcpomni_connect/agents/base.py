import asyncio
import json
import re
import uuid
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import Any
from mcpomni_connect.agents.token_usage import (
    Usage,
    UsageLimitExceeded,
    UsageLimits,
    session_stats,
    usage,
)
from mcpomni_connect.agents.tools.tools_handler import (
    LocalToolHandler,
    MCPToolHandler,
    ToolExecutor,
)
from mcpomni_connect.agents.types import (
    AgentState,
    Message,
    ParsedResponse,
    ToolCall,
    ToolCallMetadata,
    ToolCallResult,
    ToolError,
    ToolFunction,
)
from mcpomni_connect.utils import (
    RobustLoopDetector,
    handle_stuck_state,
    logger,
    show_tool_response,
)
from mcpomni_connect.events.base import (
    Event,
    EventType,
    ToolCallErrorPayload,
    ToolCallStartedPayload,
    ToolCallResultPayload,
    FinalAnswerPayload,
    AgentMessagePayload,
    UserMessagePayload,
)
from mcpomni_connect.memory_store.memory_management.memory_manager import (
    fire_and_forget_memory_processing,
    MemoryManagerFactory,
)
import traceback
from mcpomni_connect.memory_store.memory_management.shared_embedding import (
    is_vector_db_enabled,
)


class BaseReactAgent:
    """Autonomous agent implementing the ReAct paradigm for task solving through iterative reasoning and tool usage."""

    def __init__(
        self,
        agent_name: str,
        max_steps: int,
        tool_call_timeout: int,
        request_limit: int,
        total_tokens_limit: int,
    ):
        self.agent_name = agent_name
        # Enforce minimum 5 steps to allow proper tool usage and reasoning
        self.max_steps = max(max_steps, 5)
        if max_steps < 5:
            logger.warning(
                f"Agent {agent_name}: max_steps increased from {max_steps} to 5 (minimum required for tool usage)"
            )
        self.tool_call_timeout = tool_call_timeout
        self.request_limit = request_limit
        self.total_tokens_limit = total_tokens_limit

        self.messages: dict[str, list[Message]] = {}
        self.state = AgentState.IDLE

        self.loop_detector = RobustLoopDetector()
        self.assistant_with_tool_calls = None
        self.pending_tool_responses = []
        self.usage_limits = UsageLimits(
            request_limit=self.request_limit, total_tokens_limit=self.total_tokens_limit
        )

    async def get_long_episodic_memory(self, query: str, session_id: str):
        """Get long-term and episodic memory for a given query and session ID using optimized single query"""
        try:
            # Check if vector database is enabled

            if not is_vector_db_enabled():
                return [], []

            # Create both memory managers
            episodic_manager, long_term_manager = (
                MemoryManagerFactory.create_both_memory_managers(session_id=session_id)
            )

            # Query both memory types
            episodic_results = await episodic_manager.query_memory(
                query, n_results=3, distance_threshold=0.4
            )

            long_term_results = await long_term_manager.query_memory(
                query, n_results=3, distance_threshold=0.4
            )

            return long_term_results, episodic_results
        except Exception as e:
            logger.error(f"❌ Failed to retrieve memory for session {session_id}: {e}")
            logger.error(f"📋 Full traceback: {traceback.format_exc()}")
            return (
                "No relevant long-term memory found",
                "No relevant episodic memory found",
            )

    async def extract_action_or_answer(
        self,
        response: str,
        debug: bool = False,
    ) -> ParsedResponse:
        """Parse LLM response to extract a final answer or a tool action using XML format only."""
        try:
            # Check for XML-style tool call format first
            if "<tool_call>" in response and "</tool_call>" in response:
                if debug:
                    logger.info(
                        "XML tool call format detected in response: %s", response
                    )
                try:
                    # Extract single tool call
                    tool_call_match = re.search(
                        r"<tool_call>(.*?)</tool_call>", response, re.DOTALL
                    )
                    if not tool_call_match:
                        return ParsedResponse(error="No valid <tool_call> block found")

                    block = tool_call_match.group(1)

                    name_match = re.search(
                        r"<tool_name>(.*?)</tool_name>", block, re.DOTALL
                    )
                    args_match = re.search(
                        r"<parameters>(.*?)</parameters>", block, re.DOTALL
                    )

                    if name_match and args_match:
                        tool_name = name_match.group(1).strip()
                        args_str = args_match.group(1).strip()

                        try:
                            # Handle both JSON format and XML parameter format
                            if args_str.startswith("{") and args_str.endswith("}"):
                                # JSON format
                                args = json.loads(args_str)
                            else:
                                # XML parameter format - extract key-value pairs
                                args = {}
                                param_matches = re.findall(
                                    r"<(\w+)>(.*?)</\1>", args_str, re.DOTALL
                                )
                                for key, value in param_matches:
                                    args[key] = value.strip()

                            tool_call = {"tool": tool_name, "parameters": args}
                        except json.JSONDecodeError as e:
                            return ParsedResponse(
                                error=f"Invalid JSON in args: {str(e)}"
                            )
                    else:
                        return ParsedResponse(
                            error="Invalid tool call format - missing tool name or parameters"
                        )

                    # Create JSON format for compatibility with existing code
                    action_json = json.dumps(tool_call)

                    return ParsedResponse(action=True, data=action_json)

                except Exception as e:
                    logger.error("Error parsing XML tool call: %s", str(e))
                    return ParsedResponse(
                        error=f"Error parsing XML tool call: {str(e)}"
                    )

            # Check for XML final answer format
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

            # If no XML format detected, treat as conversational response
            if debug:
                logger.info(
                    "No XML format detected, treating as conversational response: %s",
                    response,
                )

            # Check if response contains any XML tags at all
            if "<" in response and ">" in response:
                # Has some XML but not the required format - return error
                return ParsedResponse(
                    error="Response contains XML tags but not in the required format. You MUST use <thought> and <final_answer> tags for all responses."
                )

            # No XML at all - return error
            return ParsedResponse(
                error="Response must use XML format. You MUST wrap your response in <thought> and <final_answer> tags. Example: <thought>Your reasoning here</thought><final_answer>Your answer here</final_answer>"
            )

        except Exception as e:
            logger.error("Error parsing model response: %s", str(e))
            return ParsedResponse(error=str(e))

    async def update_llm_working_memory(
        self,
        message_history: Callable[[], Any],
        session_id: str,
        llm_connection: Callable,
    ):
        """Update the LLM's working memory with the current message history and process memory asynchronously"""

        short_term_memory_message_history = await message_history(
            agent_name=self.agent_name, session_id=session_id
        )
        if not short_term_memory_message_history:
            return

        validated_messages = [
            Message.model_validate(msg) if isinstance(msg, dict) else msg
            for msg in short_term_memory_message_history
        ]

        try:
            # Create long-term and episodic memory processor (background task)
            fire_and_forget_memory_processing(
                session_id, validated_messages, llm_connection
            )
        except ImportError as e:
            logger.warning(f"⚠️ Memory processing not available: {e}")
        except Exception as e:
            logger.error(f"❌ Error in memory processing: {e}")
            logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        for message in validated_messages:
            role = message.role
            metadata = message.metadata
            if role == "user":
                # Flush any pending assistant-tool-call + responses before new "user" message
                self._try_flush_pending()
                self.messages[self.agent_name].append(
                    Message(role="user", content=message.content)
                )

            elif role == "assistant":
                if metadata.has_tool_calls:
                    # If we already have a pending assistant with tool calls, try to flush it
                    self._try_flush_pending()
                    # Store this assistant message for later (until we collect all tool responses)
                    self.assistant_with_tool_calls = {
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": (
                            [tc.model_dump() for tc in metadata.tool_calls]
                            if metadata.tool_calls
                            else []
                        ),
                    }
                    self.pending_tool_responses = []
                else:
                    # Regular assistant message without tool calls
                    # First flush any pending tool calls
                    self._try_flush_pending()
                    self.messages[self.agent_name].append(
                        Message(role="assistant", content=message.content)
                    )

            elif role == "tool":
                self.pending_tool_responses.append(
                    {
                        "role": "tool",
                        "content": message.content,
                        "tool_call_id": metadata.tool_call_id,
                    }
                )
                # After adding, try to flush if all responses are present
                self._try_flush_pending()

            elif role == "system":
                self._try_flush_pending()
                self.messages[self.agent_name].append(
                    Message(role="system", content=message.content)
                )

            else:
                logger.warning(f"⚠️ Unknown message role encountered: {role}")

    def _try_flush_pending(self):
        if self.assistant_with_tool_calls:
            expected_tool_calls = {
                tc["id"] for tc in self.assistant_with_tool_calls.get("tool_calls", [])
            }
            actual_tool_calls = {
                resp["tool_call_id"] for resp in self.pending_tool_responses
            }
            missing = expected_tool_calls - actual_tool_calls
            if not missing:
                self.messages[self.agent_name].append(self.assistant_with_tool_calls)
                self.messages[self.agent_name].extend(self.pending_tool_responses)
                self.assistant_with_tool_calls = None
                self.pending_tool_responses = []

    async def resolve_tool_call_request(
        self,
        parsed_response: ParsedResponse,
        sessions: dict,
        mcp_tools: dict,
        local_tools: Any = None,  # LocalToolsIntegration instance
    ) -> ToolError | ToolCallResult:
        """
        Resolve tool call request for both MCP and local tools.

        Args:
            parsed_response: Parsed response from LLM
            sessions: MCP sessions dict
            mcp_tools: MCP tools dict
            local_tools: LocalToolsIntegration instance for local tool execution
        """
        try:
            action = json.loads(parsed_response.data)
            tool_name = action.get("tool", "").strip()
            tool_args = action.get("parameters", {})

            if not tool_name:
                return ToolError(
                    observation="No tool name provided in the request",
                    tool_name="N/A",
                    tool_args=tool_args,
                )

            # First, check if tool exists in MCP tools
            mcp_tool_found = False
            if mcp_tools:
                for server_name, tools in mcp_tools.items():
                    for tool in tools:
                        if tool.name.lower() == tool_name.lower():
                            # MCP tool found
                            mcp_tool_handler = MCPToolHandler(
                                sessions=sessions,
                                tool_data=parsed_response.data,
                                mcp_tools=mcp_tools,
                            )
                            tool_executor = ToolExecutor(tool_handler=mcp_tool_handler)
                            tool_data = (
                                await mcp_tool_handler.validate_tool_call_request(
                                    tool_data=parsed_response.data,
                                    mcp_tools=mcp_tools,
                                )
                            )
                            mcp_tool_found = True
                            break
                    if mcp_tool_found:
                        break

            # If not found in MCP tools, check local tools
            if not mcp_tool_found and local_tools:
                local_tool_handler = LocalToolHandler(local_tools=local_tools)
                tool_executor = ToolExecutor(tool_handler=local_tool_handler)
                tool_data = await local_tool_handler.validate_tool_call_request(
                    tool_data=parsed_response.data,
                    local_tools=local_tools,
                )
            elif not mcp_tool_found:
                # Tool not found in either MCP or local tools
                return ToolError(
                    observation=f"The tool named '{tool_name}' does not exist in the available tools.",
                    tool_name=tool_name,
                    tool_args=tool_args,
                )

            if not tool_data.get("action"):
                return ToolError(
                    observation=tool_data.get("error", "Tool validation failed"),
                    tool_name=tool_name,
                    tool_args=tool_args,
                )

            return ToolCallResult(
                tool_executor=tool_executor,
                tool_name=tool_data.get("tool_name"),
                tool_args=tool_data.get("tool_args"),
            )
        except Exception as e:
            logger.error(f"Error resolving tool call request: {e}")
            return ToolError(
                observation=f"Error resolving tool call request: {e}",
                tool_name="unknown",
                tool_args={},
            )

    async def act(
        self,
        parsed_response: ParsedResponse,
        response: str,
        add_message_to_history: Callable[[str, str, dict | None], Any],
        system_prompt: str,
        debug: bool = False,
        sessions: dict = None,
        mcp_tools: dict = None,
        local_tools: Any = None,  # LocalToolsIntegration instance
        session_id: str = None,
        event_router: Callable[[str, Event], Any] = None,  # Event router callable
    ):
        tool_call_result = await self.resolve_tool_call_request(
            parsed_response=parsed_response,
            mcp_tools=mcp_tools,
            sessions=sessions,
            local_tools=local_tools,
        )

        # Early exit on tool validation failure
        if isinstance(tool_call_result, ToolError):
            observation = tool_call_result.observation
            event = Event(
                type=EventType.TOOL_CALL_ERROR,
                payload=ToolCallErrorPayload(
                    tool_name=tool_call_result.tool_name,
                    error_message=observation,
                ),
                agent_name=self.agent_name,
            )
            if event_router:
                await event_router(session_id=session_id, event=event)

        else:
            # Create proper tool call metadata
            tool_call_id = str(uuid.uuid4())
            tool_calls_metadata = ToolCallMetadata(
                agent_name=self.agent_name,
                has_tool_calls=True,
                tool_call_id=tool_call_id,
                tool_calls=[
                    ToolCall(
                        id=tool_call_id,
                        function=ToolFunction(
                            name=tool_call_result.tool_name,
                            arguments=json.dumps(tool_call_result.tool_args),
                        ),
                    )
                ],
            )
            # Add tool call started event
            event = Event(
                type=EventType.TOOL_CALL_STARTED,
                payload=ToolCallStartedPayload(
                    tool_name=tool_call_result.tool_name,
                    tool_args=tool_call_result.tool_args,
                    tool_call_id=tool_call_id,
                ),
                agent_name=self.agent_name,
            )
            if event_router:
                await event_router(session_id=session_id, event=event)
            await add_message_to_history(
                role="assistant",
                content=response,
                metadata=tool_calls_metadata.model_dump(),
                session_id=session_id,
            )

            try:
                async with asyncio.timeout(self.tool_call_timeout):
                    observation = await tool_call_result.tool_executor.execute(
                        agent_name=self.agent_name,
                        tool_args=tool_call_result.tool_args,
                        tool_name=tool_call_result.tool_name,
                        tool_call_id=tool_call_id,
                        add_message_to_history=add_message_to_history,
                        session_id=session_id,
                    )
                    try:
                        parsed = json.loads(observation)
                    except json.JSONDecodeError:
                        parsed = {
                            "status": "error",
                            "message": "Invalid JSON returned by tool. Please try again or use a different approach. If the issue persists, stop immediately.",
                        }

                    if parsed.get("status") == "error":
                        observation = f"Error: {parsed['message']}"
                    else:
                        observation = str(parsed["data"])
                # Handle tool call result event
                event = Event(
                    type=EventType.TOOL_CALL_RESULT,
                    payload=ToolCallResultPayload(
                        tool_name=tool_call_result.tool_name,
                        tool_args=tool_call_result.tool_args,
                        result=observation,
                        tool_call_id=tool_call_id,
                    ),
                    agent_name=self.agent_name,
                )
                if event_router:
                    await event_router(session_id=session_id, event=event)

            except asyncio.TimeoutError:
                observation = (
                    "Tool call timed out. Please try again or use a different approach."
                )
                logger.warning(observation)
                await add_message_to_history(
                    role="tool",
                    content=observation,
                    metadata={
                        "tool_call_id": tool_call_id,
                        "agent_name": self.agent_name,
                    },
                    session_id=session_id,
                )
                # handle tool call timeout event
                event = Event(
                    type=EventType.TOOL_CALL_ERROR,
                    payload=ToolCallErrorPayload(
                        tool_name=tool_call_result.tool_name,
                        error_message=observation,
                    ),
                    agent_name=self.agent_name,
                )
                if event_router:
                    await event_router(session_id=session_id, event=event)
                self.messages[self.agent_name].append(
                    Message(
                        role="user",
                        content=f"Observation:\n{observation}",
                    )
                )
            except Exception as e:
                observation = f"Error executing tool: {str(e)}"
                logger.error(observation)
                await add_message_to_history(
                    role="tool",
                    content=observation,
                    metadata={
                        "tool_call_id": tool_call_id,
                        "agent_name": self.agent_name,
                    },
                    session_id=session_id,
                )
                # handle tool call error event
                event = Event(
                    type=EventType.TOOL_CALL_ERROR,
                    payload=ToolCallErrorPayload(
                        tool_name=tool_call_result.tool_name,
                        error_message=observation,
                    ),
                    agent_name=self.agent_name,
                )
                if event_router:
                    await event_router(session_id=session_id, event=event)
                self.messages[self.agent_name].append(
                    Message(
                        role="user",
                        content=f"Observation:\n{observation}",
                    )
                )
            # Loop detection
            self.loop_detector.record_tool_call(
                str(tool_call_result.tool_name),
                str(tool_call_result.tool_args),
                str(observation),
            )
        if debug:
            show_tool_response(
                agent_name=self.agent_name,
                tool_name=tool_call_result.tool_name,
                tool_args=tool_call_result.tool_args,
                observation=observation,
            )
        # Final observation handling
        self.messages[self.agent_name].append(
            Message(
                role="user",
                content=f"OBSERVATION(RESULT FROM {tool_call_result.tool_name} TOOL CALL): \n{observation}",
            )
        )
        await add_message_to_history(
            role="user",
            content=f"OBSERVATION(RESULT FROM {tool_call_result.tool_name} TOOL CALL): \n{observation}",
            session_id=session_id,
            metadata={"agent_name": self.agent_name},
        )
        if debug:
            logger.info(
                f"Agent state changed from {self.state} to {AgentState.OBSERVING}"
            )
        self.state = AgentState.OBSERVING

        if self.loop_detector.is_looping():
            loop_type = self.loop_detector.get_loop_type()
            logger.warning(f"Tool call loop detected: {loop_type}")
            new_system_prompt = handle_stuck_state(system_prompt)
            self.messages[self.agent_name] = await self.reset_system_prompt(
                messages=self.messages[self.agent_name], system_prompt=new_system_prompt
            )
            loop_message = (
                f"Observation:\n"
                f"⚠️ Tool call loop detected: {loop_type}\n\n"
                f"Current approach is not working. You MUST now provide a final answer to the user.\n"
                f"Please:\n"
                f"1. Stop trying the same approach\n"
                f"2. Provide your best response to the user based on what you know\n"
                f"3. Use <final_answer>Your response here</final_answer> format\n"
                f"4. Be helpful and explain any limitations if needed\n"
                f"5. Do NOT continue with more tool calls\n"
                f"\nYou MUST respond with <final_answer> tags now.\n"
            )
            # handle loop detection event
            event = Event(
                type=EventType.TOOL_CALL_ERROR,
                payload=ToolCallErrorPayload(
                    tool_name=tool_call_result.tool_name,
                    error_message=loop_message,
                ),
                agent_name=self.agent_name,
            )
            if event_router:
                await event_router(session_id=session_id, event=event)
            self.messages[self.agent_name].append(
                Message(role="user", content=loop_message)
            )
            if debug:
                logger.info(
                    f"Agent state changed from {self.state} to {AgentState.STUCK}"
                )
            self.state = AgentState.STUCK
            self.loop_detector.reset()

    async def reset_system_prompt(self, messages: list, system_prompt: str):
        # Reset system prompt and keep all messages

        old_messages = messages[1:]
        messages = [Message(role="system", content=system_prompt)]
        messages.extend(old_messages)
        return messages

    @asynccontextmanager
    async def agent_state_context(self, new_state: AgentState):
        """Context manager to change the agent state"""
        if not isinstance(new_state, AgentState):
            raise ValueError(f"Invalid agent state: {new_state}")
        previous_state = self.state
        self.state = new_state
        try:
            yield
        except Exception as e:
            self.state = AgentState.ERROR
            logger.error(f"Error in agent state context: {e}")
            raise
        finally:
            self.state = previous_state

    async def get_tools_registry(
        self, mcp_tools: dict = None, local_tools: Any = None
    ) -> str:
        tools_section = []
        try:
            # Process MCP tools
            if mcp_tools:
                for server_name, tools in mcp_tools.items():
                    if not tools:
                        continue

                    # Add server header
                    tools_section.append(f"## {server_name.upper()} TOOLS (MCP)")

                    # Handle MCP Tool objects
                    for tool in tools:
                        if hasattr(tool, "name"):  # MCP Tool object
                            tool_name = str(tool.name)
                            tool_description = str(tool.description)

                            tool_md = f"### `{tool_name}`\n{tool_description}"

                            if hasattr(tool, "inputSchema") and tool.inputSchema:
                                params = tool.inputSchema.get("properties", {})
                                if params:
                                    tool_md += "\n\n**Parameters:**\n"
                                    tool_md += "| Name | Type | Description |\n"
                                    tool_md += "|------|------|-------------|\n"
                                    for param_name, param_info in params.items():
                                        param_desc = param_info.get(
                                            "description", "**No description**"
                                        )
                                        param_type = param_info.get("type", "any")
                                        tool_md += f"| `{param_name}` | `{param_type}` | {param_desc} |\n"

                            tools_section.append(tool_md)

            # Process local tools
            if local_tools:
                local_tools_list = local_tools.get_available_tools()
                if local_tools_list:
                    tools_section.append("## LOCAL TOOLS")

                    # Handle local tool dictionaries
                    for tool in local_tools_list:
                        if isinstance(tool, dict):
                            tool_name = tool.get("name", "Unknown")
                            tool_description = tool.get("description", "No description")

                            tool_md = f"### `{tool_name}`\n{tool_description}"

                            input_schema = tool.get("inputSchema", {})
                            if input_schema:
                                params = input_schema.get("properties", {})
                                if params:
                                    tool_md += "\n\n**Parameters:**\n"
                                    tool_md += "| Name | Type | Description |\n"
                                    tool_md += "|------|------|-------------|\n"
                                    for param_name, param_info in params.items():
                                        param_desc = param_info.get(
                                            "description", "**No description**"
                                        )
                                        param_type = param_info.get("type", "any")
                                        tool_md += f"| `{param_name}` | `{param_type}` | {param_desc} |\n"

                            tools_section.append(tool_md)

            if not tools_section:
                return "No tools available"

        except Exception as e:
            logger.error(f"Error getting tools registry: {e}")
            return "No tools registry available"

        return "\n\n".join(tools_section)

    async def run(
        self,
        system_prompt: str,
        query: str,
        llm_connection: Callable,
        add_message_to_history: Callable[[str, str, dict | None], Any],
        message_history: Callable[[], Any],
        debug: bool = False,
        sessions: dict = None,
        mcp_tools: dict = None,
        local_tools: Any = None,  # LocalToolsIntegration instance
        session_id: str = None,
        event_router: Callable[[str, Event], Any] = None,  # Event router callable
    ) -> str | None:
        """Execute ReAct loop with JSON communication
        kwargs: if mcp is enbale then it will be sessions and availables_tools else it will be local_tools
        """
        # handle start of agent run
        event = Event(
            type=EventType.USER_MESSAGE,
            payload=UserMessagePayload(
                message=query,
            ),
            agent_name=self.agent_name,
        )
        if event_router:
            await event_router(session_id=session_id, event=event)

        # Initialize messages with system prompt
        tools_section = await self.get_tools_registry(
            mcp_tools=mcp_tools, local_tools=local_tools
        )
        long_term_memory, episodic_memory = await self.get_long_episodic_memory(
            query=query, session_id=session_id
        )
        #  append the tools section if needed
        system_prompt += f"\n[AVAILABLE TOOLS REGISTRY]\n\n{tools_section}"
        # now update the system prompt with the long term and episodic memory using the XML-based template
        system_updated_prompt = (
            system_prompt
            + f"\n[LONG TERM MEMORY]\n\n{long_term_memory}\n\n[EPISODIC MEMORY]\n\n{episodic_memory}"
        )

        self.messages[self.agent_name] = [
            Message(role="system", content=system_updated_prompt)
        ]
        # Add initial user message to message history
        await add_message_to_history(
            role="user",
            content=query,
            session_id=session_id,
            metadata={"agent_name": self.agent_name},
        )
        # Initialize messages with current message history (only once at start)
        await self.update_llm_working_memory(
            message_history=message_history,
            session_id=session_id,
            llm_connection=llm_connection,
        )
        # check if the agent is in a valid state to run
        if self.state not in [
            AgentState.IDLE,
            AgentState.STUCK,
            AgentState.ERROR,
        ]:
            raise RuntimeError(f"Agent is not in a valid state to run: {self.state}")

        # set the agent state to running
        async with self.agent_state_context(AgentState.RUNNING):
            current_steps = 0
            last_valid_response = None  # Track last valid response
            while (
                self.state not in [AgentState.FINISHED, AgentState.STUCK]
                and current_steps < self.max_steps
            ):
                if debug:
                    logger.info(
                        f"Sending {len(self.messages[self.agent_name])} messages to LLM"
                    )
                current_steps += 1
                self.usage_limits.check_before_request(usage=usage)

                try:
                    response = await llm_connection.llm_call(
                        self.messages[self.agent_name]
                    )
                    if response:
                        # handle agent response event
                        event = Event(
                            type=EventType.AGENT_MESSAGE,
                            payload=AgentMessagePayload(
                                message=str(response),
                            ),
                            agent_name=self.agent_name,
                        )
                        if event_router:
                            await event_router(session_id=session_id, event=event)
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
                            if debug:
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
                    response=response, debug=debug
                )
                if debug:
                    logger.info(f"current steps: {current_steps}")
                # check for final answer
                if parsed_response.answer is not None:
                    last_valid_response = (
                        parsed_response.answer
                    )  # Store last valid response
                    self.messages[self.agent_name].append(
                        Message(
                            role="assistant",
                            content=parsed_response.answer,
                        )
                    )
                    # handle final answer event
                    event = Event(
                        type=EventType.FINAL_ANSWER,
                        payload=FinalAnswerPayload(
                            message=str(parsed_response.answer),
                        ),
                        agent_name=self.agent_name,
                    )
                    if event_router:
                        await event_router(session_id=session_id, event=event)
                    await add_message_to_history(
                        role="assistant",
                        content=parsed_response.answer,
                        session_id=session_id,
                        metadata={"agent_name": self.agent_name},
                    )
                    self.state = AgentState.FINISHED
                    return parsed_response.answer
                # check for action
                if parsed_response.action is not None:
                    # Add the action to the message history
                    self.messages[self.agent_name].append(
                        Message(
                            role="assistant",
                            content=parsed_response.data,
                        )
                    )
                    await add_message_to_history(
                        role="assistant",
                        content=parsed_response.data,
                        session_id=session_id,
                        metadata={"agent_name": self.agent_name},
                    )

                    # Execute the action
                    await self.act(
                        parsed_response=parsed_response,
                        response=response,
                        add_message_to_history=add_message_to_history,
                        system_prompt=system_prompt,
                        debug=debug,
                        sessions=sessions,
                        mcp_tools=mcp_tools,
                        local_tools=local_tools,
                        session_id=session_id,
                        event_router=event_router,  # Pass event_router callable
                    )

                # check for stuck state
                if current_steps >= self.max_steps:
                    self.state = AgentState.STUCK
                    if last_valid_response:
                        # Prepend max steps context for judge evaluation
                        max_steps_context = f"[SYSTEM_CONTEXT: MAX_STEPS_REACHED - Agent hit {self.max_steps} step limit]\n\n"
                        return max_steps_context + last_valid_response
                    else:
                        return f"[SYSTEM_CONTEXT: MAX_STEPS_REACHED - Agent hit {self.max_steps} step limit without valid response]"

        # If we exit the loop due to STUCK state, return last valid response with context
        if self.state == AgentState.STUCK and last_valid_response:
            # Prepend loop detection context for judge evaluation
            loop_context = (
                f"[SYSTEM_CONTEXT: LOOP_DETECTED - Agent stuck in tool call loop]\n\n"
            )
            return loop_context + last_valid_response

        return None
