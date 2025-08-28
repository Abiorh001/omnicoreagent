import json
from collections.abc import Callable
from typing import Any

from omnicoreagent.core.agents.token_usage import (
    Usage,
    UsageLimitExceeded,
    UsageLimits,
    session_stats,
    usage,
)
from omnicoreagent.core.agents.types import AgentConfig
from omnicoreagent.core.events.base import (
    Event,
    EventType,
    ToolCallStartedPayload,
    ToolCallResultPayload,
    AgentMessagePayload,
    UserMessagePayload,
    ToolCallErrorPayload,
)
from omnicoreagent.core.utils import logger, track


class ToolCallingAgent:
    def __init__(
        self,
        config: AgentConfig,
        debug: bool = False,
    ):
        self.request_limit = config.request_limit
        self.total_tokens_limit = config.total_tokens_limit
        self.agent_name = config.agent_name or "tool_calling_agent"

        self.debug = debug
        self.assistant_with_tool_calls = None
        self.pending_tool_responses = []
        self.messages = []
        self.usage_limits = UsageLimits(
            request_limit=self.request_limit, total_tokens_limit=self.total_tokens_limit
        )

    @track("update_llm_working_memory")
    async def update_llm_working_memory(
        self, message_history: Callable[[], Any], session_id: str
    ):
        """Process message history and update working memory for LLM."""
        # Get message history from Redis or other storage
        short_term_memory_message_history = await message_history(
            agent_name=self.agent_name, session_id=session_id
        )

        # Process message history in order
        for _, message in enumerate(short_term_memory_message_history):
            role = message["role"]
            if role == "user":
                # First flush any pending tool responses if needed
                if self.assistant_with_tool_calls and self.pending_tool_responses:
                    self.messages.append(self.assistant_with_tool_calls)
                    self.messages.extend(self.pending_tool_responses)
                    self.assistant_with_tool_calls = None
                    self.pending_tool_responses = []

                # Add user message to messages that will be sent to LLM
                self.messages.append({"role": "user", "content": message["content"]})

            elif role == "assistant":
                # Check if the assistant message has tool calls
                metadata = message.get("metadata", {})
                if metadata.get("has_tool_calls", False):
                    # If we already have a pending assistant with tool calls, flush it
                    if self.assistant_with_tool_calls:
                        self.messages.append(self.assistant_with_tool_calls)
                        self.messages.extend(self.pending_tool_responses)
                        self.pending_tool_responses = []

                    # Store this assistant message for later (until we collect all tool responses)
                    self.assistant_with_tool_calls = {
                        "role": "assistant",
                        "content": message["content"],
                        "tool_calls": metadata.get("tool_calls", []),
                    }
                else:
                    # Regular assistant message without tool calls
                    # First flush any pending tool calls
                    if self.assistant_with_tool_calls:
                        self.messages.append(self.assistant_with_tool_calls)
                        self.messages.extend(self.pending_tool_responses)
                        self.assistant_with_tool_calls = None
                        self.pending_tool_responses = []

                    # Add the regular assistant message to messages
                    self.messages.append(
                        {"role": "assistant", "content": message["content"]}
                    )

            elif role == "tool" and "tool_call_id" in message.get("metadata", {}):
                # Collect tool responses
                # Only add if we have a preceding assistant message with tool calls
                if self.assistant_with_tool_calls:
                    self.pending_tool_responses.append(
                        {
                            "role": "tool",
                            "content": message["content"],
                            "tool_call_id": message["metadata"]["tool_call_id"],
                        }
                    )

            elif role == "system":
                # Add system message to messages
                self.messages.append({"role": "system", "content": message["content"]})

        # Flush any remaining pending tool calls at the end
        if self.assistant_with_tool_calls:
            self.messages.append(self.assistant_with_tool_calls)
            self.messages.extend(self.pending_tool_responses)

    @track("list_available_tools")
    async def list_available_tools(self, available_tools: dict = None):
        """List available tools from all servers."""
        # List available tools
        available_tools_list = []
        all_available_tools = None
        if available_tools:
            for _, tools in available_tools.items():
                available_tools_list.extend(tools)

            all_available_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in available_tools_list
            ]

        return all_available_tools

    async def execute_tool_call(
        self,
        session_id: str,
        tool_name: str,
        tool_args: str | dict,
        tool_call: Any,
        add_message_to_history: Callable[..., Any],
        available_tools: dict[str, Any] = None,
        sessions: dict[str, Any] = None,
        event_router: Callable[[str, Event], Any] = None,
    ) -> dict:
        """Unified executor for MCP and local tool calls based on config"""

        if isinstance(tool_args, str):
            try:
                tool_args = json.loads(tool_args)
            except Exception:
                logger.error(f"Failed to parse tool_args for {tool_name}: {tool_args}")
                tool_args = {}

        # Emit tool call started event
        if event_router:
            event = Event(
                type=EventType.TOOL_CALL_STARTED,
                payload=ToolCallStartedPayload(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_call_id=tool_call.id,
                ),
                agent_name=self.agent_name,
            )
            await event_router(session_id=session_id, event=event)

        try:
            if available_tools:
                for server_name, tools in available_tools.items():
                    tool_names = [
                        tool.name if hasattr(tool, "name") else tool
                        for tool in tools
                        if hasattr(tool, "name") or isinstance(tool, str)
                    ]

                    if tool_name in tool_names:
                        result = await sessions[server_name]["session"].call_tool(
                            tool_name, tool_args
                        )
                        tool_content = (
                            result.content
                            if hasattr(result, "content")
                            else str(result)
                        )
                        break
                else:
                    raise Exception(f"Tool {tool_name} not found in any server")
            else:
                raise Exception("No available tools provided")

            # Normalize structured result if needed
            if (
                hasattr(tool_content, "__getitem__")
                and len(tool_content) > 0
                and hasattr(tool_content[0], "text")
            ):
                tool_content = tool_content[0].text

            self.messages.append(
                {
                    "role": "tool",
                    "content": str(tool_content),
                    "tool_call_id": tool_call.id,
                }
            )

            await add_message_to_history(
                role="tool",
                content=str(tool_content),
                metadata={
                    "tool_call_id": tool_call.id,
                    "tool": tool_name,
                    "args": tool_args,
                    "agent_name": self.agent_name,
                },
                session_id=session_id,
            )

            # Emit tool call result event
            if event_router:
                event = Event(
                    type=EventType.TOOL_CALL_RESULT,
                    payload=ToolCallResultPayload(
                        tool_name=tool_name,
                        tool_args=tool_args,
                        tool_call_id=tool_call.id,
                        result=str(tool_content),
                    ),
                    agent_name=self.agent_name,
                )
                await event_router(session_id=session_id, event=event)

            return {"result": str(tool_content)}

        except Exception as e:
            error_message = f"Error executing tool call {tool_name}: {e}"
            logger.error(error_message)

            self.messages.append(
                {
                    "role": "tool",
                    "content": error_message,
                    "tool_call_id": tool_call.id,
                }
            )

            await add_message_to_history(
                role="tool",
                content=error_message,
                metadata={
                    "tool_call_id": tool_call.id,
                    "tool": tool_name,
                    "args": tool_args,
                    "error": True,
                    "agent_name": self.agent_name,
                },
                session_id=session_id,
            )

            # Emit tool call error event
            if event_router:
                event = Event(
                    type=EventType.TOOL_CALL_ERROR,
                    payload=ToolCallErrorPayload(
                        tool_name=tool_name,
                        error_message=error_message,
                    ),
                    agent_name=self.agent_name,
                )
                await event_router(session_id=session_id, event=event)

            return {"error": error_message}

    async def run(
        self,
        query: str,
        session_id: str,
        system_prompt: str,
        llm_connection: Callable[[], Any],
        sessions: dict[str, Any],
        server_names: list[str],
        tools_list: list[dict[str, Any]],
        add_message_to_history: Callable[..., Any],
        message_history: Callable[[], Any],
        available_tools: dict[str, Any] = None,
        event_router: Callable[[str, Event], Any] = None,
    ):
        """Run the agent with the given query and return the response."""
        final_text = []
        available_tools = available_tools

        current_steps = 0
        # Initialize messages with system prompt
        self.messages = [{"role": "system", "content": system_prompt}]

        # Add user query to history
        await add_message_to_history(
            role="user",
            content=query,
            session_id=session_id,
            metadata={"agent_name": self.agent_name},
        )

        # Emit user message event
        if event_router:
            event = Event(
                type=EventType.USER_MESSAGE,
                payload=UserMessagePayload(message=query),
                agent_name=self.agent_name,
            )
            await event_router(session_id=session_id, event=event)

        # Update working memory with message history
        await self.update_llm_working_memory(
            message_history=message_history, session_id=session_id
        )

        # Get available tools
        all_available_tools = await self.list_available_tools(
            available_tools=available_tools,
        )

        try:
            # Initial LLM API call
            current_steps += 1
            self.usage_limits.check_before_request(usage=usage)
            response = await llm_connection.llm_call(
                messages=self.messages, tools=all_available_tools
            )
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
        except UsageLimitExceeded as e:
            error_message = f"Usage limit error: {e}"
            logger.error(error_message)
            return error_message
        except Exception as e:
            error_message = f"Error processing query: {e}"
            logger.error(error_message)
            return error_message
        # Process response and handle tool calls
        assistant_message = None
        if response:
            if hasattr(response, "choices"):
                assistant_message = response.choices[0].message
            elif hasattr(response, "message"):
                assistant_message = response.message
        else:
            return "Error processing query"
        initial_response = assistant_message.content or ""

        # Process tool calls
        if assistant_message.tool_calls:
            tool_calls_metadata = {
                "has_tool_calls": True,
                "tool_calls": assistant_message.tool_calls,
                "agent_name": self.agent_name,
            }

            if self.debug:
                logger.info(
                    f"Processing {len(assistant_message.tool_calls)} tool calls"
                )

            # If the initial response is empty, set it to the tool call name for context
            if not initial_response:
                if self.debug:
                    logger.info(
                        "Initial response is empty, setting it to the tool call name"
                    )
                tool_name = assistant_message.tool_calls[0].function.name
                initial_response = f"Tool called {tool_name}"

            # Append assistant message with tool calls
            self.messages.append(
                {
                    "role": "assistant",
                    "content": initial_response,
                    "tool_calls": assistant_message.tool_calls,
                }
            )

            # Add the assistant message to history with tool calls metadata
            await add_message_to_history(
                role="assistant",
                content=initial_response,
                metadata=tool_calls_metadata,
                session_id=session_id,
            )

            final_text.append(initial_response)

            # Process each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                execute_tool_result = await self.execute_tool_call(
                    session_id=session_id,
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_call=tool_call,
                    add_message_to_history=add_message_to_history,
                    available_tools=available_tools,
                    sessions=sessions,
                    event_router=event_router,
                )

                if "error" in execute_tool_result:
                    final_text.append(execute_tool_result["error"])

            # Get final response from LLM with tool results
            try:
                if self.debug:
                    logger.info("Getting final response from LLM with tool results")
                current_steps += 1
                second_response = await llm_connection.llm_call(
                    messages=self.messages,
                )
                if second_response:
                    # check if it has usage
                    if hasattr(second_response, "usage"):
                        request_usage = Usage(
                            requests=current_steps,
                            request_tokens=second_response.usage.prompt_tokens,
                            response_tokens=second_response.usage.completion_tokens,
                            total_tokens=second_response.usage.total_tokens,
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

                    if hasattr(second_response, "choices"):
                        final_assistant_message = second_response.choices[0].message
                    elif hasattr(second_response, "message"):
                        final_assistant_message = second_response.message
                response_content = final_assistant_message.content or ""

                await add_message_to_history(
                    role="assistant",
                    content=response_content,
                    session_id=session_id,
                    metadata={"agent_name": self.agent_name},
                )

                # Emit agent message event
                if event_router:
                    event = Event(
                        type=EventType.AGENT_MESSAGE,
                        payload=AgentMessagePayload(message=response_content),
                        agent_name=self.agent_name,
                    )
                    await event_router(session_id=session_id, event=event)

                final_text.append(response_content)
            except UsageLimitExceeded as e:
                error_message = f"Usage limit error: {e}"
                logger.error(error_message)
                return error_message
            except Exception as e:
                error_message = f"Error getting final response from LLM: {e}"
                logger.error(error_message)

                await add_message_to_history(
                    role="assistant",
                    content=error_message,
                    metadata={"error": True, "agent_name": self.agent_name},
                    session_id=session_id,
                )

                final_text.append(f"\n[Error getting final response from LLM: {e}]")
        else:
            # If no tool calls, add the assistant response directly
            await add_message_to_history(
                role="assistant",
                content=initial_response,
                session_id=session_id,
                metadata={"agent_name": self.agent_name},
            )

            # Emit agent message event
            if event_router:
                event = Event(
                    type=EventType.AGENT_MESSAGE,
                    payload=AgentMessagePayload(message=initial_response),
                    agent_name=self.agent_name,
                )
                await event_router(session_id=session_id, event=event)

            final_text.append(initial_response)
        current_steps = 0
        return "\n".join(final_text)
