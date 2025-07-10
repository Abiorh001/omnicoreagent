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
    LocalToolExecutor,
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
    strip_json_comments,
    show_tool_response,
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
        self.max_steps = max_steps
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

    async def extract_action_json(self, response: str) -> dict[str, Any]:
        """
        Extract a JSON-formatted action from a model response string.
        Returns a dictionary with the parsed content or an error structure.
        """
        try:
            action_start = response.find("Action:")
            if action_start == -1:
                return {
                    "error": "No 'Action:' section found in response",
                    "action": False,
                }

            action_text = response[action_start + len("Action:") :].strip()

            # Find start of JSON
            if "{" not in action_text:
                return {
                    "error": "No JSON object found after 'Action:'",
                    "action": False,
                }

            json_start = action_text.find("{")
            json_text = action_text[json_start:]

            # Track balanced braces
            open_braces = 0
            json_end_pos = 0

            for i, char in enumerate(json_text):
                if char == "{":
                    open_braces += 1
                elif char == "}":
                    open_braces -= 1
                    if open_braces == 0:
                        json_end_pos = i + 1
                        break

            if json_end_pos == 0:
                return {"error": "Unbalanced JSON braces", "action": False}

            json_str = json_text[:json_end_pos]

            # Clean up LLM quirks safely
            json_str = strip_json_comments(json_str)
            json_str = re.sub(r",\s*([\]}])", r"\1", json_str)

            logger.debug("Extracted JSON: %s", json_str)

            return {"action": True, "data": json_str}

        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", str(e))
            return {"error": f"Invalid JSON format: {str(e)}", "action": False}

        except Exception as e:
            logger.error("Error parsing response: %s", str(e))
            return {"error": str(e), "action": False}

    async def extract_action_or_answer(
        self,
        response: str,
        debug: bool = False,
    ) -> ParsedResponse:
        """Parse LLM response to extract a final answer or a tool action."""
        try:
            # Final answer present
            if "Final Answer:" in response or "Answer:" in response:
                if debug:
                    logger.info("Final answer detected in response: %s", response)

                parts = re.split(
                    r"(?:Final Answer:|Answer:)", response, flags=re.IGNORECASE
                )
                if len(parts) > 1:
                    return ParsedResponse(answer=parts[-1].strip())

            # Tool action present
            if "Action" in response:
                if debug:
                    logger.info("Tool action detected in response: %s", response)

                action_result = await self.extract_action_json(response=response)

                if action_result.get("action"):
                    return ParsedResponse(
                        action=action_result.get("action"),
                        data=action_result.get("data"),
                    )
                elif "error" in action_result:
                    return ParsedResponse(error=action_result["error"])
                else:
                    return ParsedResponse(
                        error="No valid action or answer found in response"
                    )

            # Fallback to raw response
            if debug:
                logger.info("Returning raw response as answer: %s", response)

            return ParsedResponse(answer=response.strip())

        except Exception as e:
            logger.error("Error parsing model response: %s", str(e))
            return ParsedResponse(error=str(e))

    async def update_llm_working_memory(
        self, message_history: Callable[[], Any], session_id: str
    ):
        """Update the LLM's working memory with the current message history"""
        short_term_memory_message_history = await message_history(
            agent_name=self.agent_name, session_id=session_id
        )
        if not short_term_memory_message_history:
            logger.warning(f"No message history found for agent: {self.agent_name}")
            return

        validated_messages = [
            Message.model_validate(msg) if isinstance(msg, dict) else msg
            for msg in short_term_memory_message_history
        ]

        for message in validated_messages:
            role = message.role
            metadata = message.metadata
            if role == "user":
                # Flush any pending assistant-tool-call + responses before new "user" message
                if self.assistant_with_tool_calls:
                    self.messages[self.agent_name].append(
                        self.assistant_with_tool_calls
                    )
                    self.messages[self.agent_name].extend(self.pending_tool_responses)
                    self.assistant_with_tool_calls = None
                    self.pending_tool_responses = []

                self.messages[self.agent_name].append(
                    Message(role="user", content=message.content)
                )

            elif role == "assistant":
                if metadata.has_tool_calls:
                    # If we already have a pending assistant with tool calls, flush it
                    if self.assistant_with_tool_calls:
                        self.messages[self.agent_name].append(
                            self.assistant_with_tool_calls
                        )
                        self.messages[self.agent_name].extend(
                            self.pending_tool_responses
                        )
                        self.pending_tool_responses = []

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
                else:
                    # Regular assistant message without tool calls
                    # First flush any pending tool calls
                    if self.assistant_with_tool_calls:
                        self.messages[self.agent_name].append(
                            self.assistant_with_tool_calls
                        )
                        self.messages[self.agent_name].extend(
                            self.pending_tool_responses
                        )
                        self.assistant_with_tool_calls = None
                        self.pending_tool_responses = []

                    self.messages[self.agent_name].append(
                        Message(role="assistant", content=message.content)
                    )

            elif role == "tool" and hasattr(metadata, "tool_call_id"):
                # Collect tool responses
                # Only add if we have a preceding assistant message with tool calls
                if self.assistant_with_tool_calls:
                    self.pending_tool_responses.append(
                        {
                            "role": "tool",
                            "content": message.content,
                            "tool_call_id": str(metadata.tool_call_id),
                        }
                    )

            elif role == "system":
                self.messages[self.agent_name].append(
                    Message(role="system", content=message.content)
                )

            else:
                logger.warning(f"Unknown message role encountered: {role}")

    async def resolve_tool_call_request(
        self,
        parsed_response: ParsedResponse,
        sessions: dict,
        available_tools: dict,
        local_tools: Any = None,  # LocalToolsIntegration instance
    ) -> ToolError | ToolCallResult:
        """
        Resolve tool call request for both MCP and local tools.
        
        Args:
            parsed_response: Parsed response from LLM
            sessions: MCP sessions dict
            available_tools: Combined available tools dict
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
            
            # Check if it's a local tool
            if local_tools:
                # Use LocalToolHandler to validate and execute local tools
                local_tool_handler = LocalToolHandler(local_tools)
                validation_result = await local_tool_handler.validate_tool_call_request(
                    tool_data=parsed_response.data,
                    available_tools={}  # Not used for local tools
                )
                
                if validation_result.get("action"):
                    # Create LocalToolExecutor for local tool execution
                    tool_executor = LocalToolExecutor(local_tools, tool_name)
                    return ToolCallResult(
                        tool_executor=tool_executor,
                        tool_name=validation_result.get("tool_name"),
                        tool_args=validation_result.get("tool_args"),
                    )
                else:
                    # Check if it's an MCP tool before returning error
                    pass
            
            # Check if it's an MCP tool
            if sessions and available_tools:
                # Find the tool in available MCP tools
                for server_name, tools in available_tools.items():
                    if server_name == "local_tools":
                        continue  # Skip local tools, already handled above
                    
                    for tool in tools:
                        if hasattr(tool, 'name') and tool.name.lower() == tool_name.lower():
                            # Use MCP tool handler
                            mcp_tool_handler = MCPToolHandler(
                                sessions=sessions,
                                tool_data=parsed_response.data,
                                available_tools=available_tools,
                            )
                            tool_executor = ToolExecutor(tool_handler=mcp_tool_handler)
                            tool_data = await mcp_tool_handler.validate_tool_call_request(
                                tool_data=parsed_response.data,
                                available_tools=available_tools,
                            )
                            
                            if not tool_data.get("action"):
                                return ToolError(
                                    observation=tool_data.get("error", "MCP tool validation failed"),
                                    tool_name=tool_name,
                                    tool_args=tool_args,
                                )
                            
                            return ToolCallResult(
                                tool_executor=tool_executor,
                                tool_name=tool_data.get("tool_name"),
                                tool_args=tool_data.get("tool_args"),
                            )
            
            # Tool not found - return error from local tool validation if available
            if local_tools:
                local_tool_handler = LocalToolHandler(local_tools)
                validation_result = await local_tool_handler.validate_tool_call_request(
                    tool_data=parsed_response.data,
                    available_tools={}
                )
                if not validation_result.get("action"):
                    return ToolError(
                        observation=validation_result.get("error", f"Tool '{tool_name}' not found"),
                        tool_name=tool_name,
                        tool_args=tool_args,
                    )
            
            # Fallback error
            return ToolError(
                observation=f"Tool '{tool_name}' not found in available tools",
                tool_name=tool_name,
                tool_args=tool_args,
            )
            
        except json.JSONDecodeError as e:
            return ToolError(
                observation=f"Invalid JSON in tool call: {str(e)}",
                tool_name="N/A",
                tool_args={},
            )
        except Exception as e:
            return ToolError(
                observation=f"Error resolving tool call: {str(e)}",
                tool_name="N/A",
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
        available_tools: dict = None,
        local_tools: Any = None,  # LocalToolsIntegration instance
        session_id: str = None,
    ):
        tool_call_result = await self.resolve_tool_call_request(
            parsed_response=parsed_response,
            available_tools=available_tools,
            sessions=sessions,
            local_tools=local_tools,
        )

        # Early exit on tool validation failure
        if isinstance(tool_call_result, ToolError):
            observation = tool_call_result.observation
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

            await add_message_to_history(
               
                role="assistant",
                content=response,
                metadata=tool_calls_metadata,
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

            except asyncio.TimeoutError:
                observation = (
                    "Tool call timed out. Please try again or use a different approach."
                )
                logger.warning(observation)
                await add_message_to_history(
                   
                    role="tool",
                    content=observation,
                    metadata={"tool_call_id": tool_call_id, "agent_name": self.agent_name},
                    session_id=session_id,
                )
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
                    metadata={"tool_call_id": tool_call_id, "agent_name": self.agent_name},
                    session_id=session_id,
                )

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
                f"Current approach is not working. Please:\n"
                f"1. Analyze why the previous attempts failed\n"
                f"2. Try a completely different tool or approach\n"
                f"3. If stuck, explain the issue to the user\n"
                f"4. Consider breaking down the task into smaller steps\n"
                f"5. Check if the tool parameters need adjustment\n"
                f"6. If the issue persists, stop immediately.\n"
            )
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
        self, available_tools: dict, agent_name: str = None
    ) -> str:
        tools_section = []
        try:
            if agent_name:
                tools = available_tools.get(agent_name, [])
            else:
                # Flatten all tools across agents (ignoring server/agent names)
                tools = [
                    tool
                    for tools_list in available_tools.values()
                    for tool in tools_list
                ]

            for tool in tools:
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
                            tool_md += (
                                f"| `{param_name}` | `{param_type}` | {param_desc} |\n"
                            )

                tools_section.append(tool_md)

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
        available_tools: dict = None,
        local_tools: Any = None,  # LocalToolsIntegration instance
        session_id: str = None,
    ) -> str | None:
        """Execute ReAct loop with JSON communication
        kwargs: if mcp is enbale then it will be sessions and availables_tools else it will be local_tools
        """
        # Initialize messages with system prompt
        tools_section = await self.get_tools_registry(
            available_tools, agent_name=self.agent_name
        )
        system_updated_prompt = (
            system_prompt + f"[AVAILABLE TOOLS REGISTRY]\n\n{tools_section}"
        )

        self.messages[self.agent_name] = [
            Message(role="system", content=system_updated_prompt)
        ]
        # Add initial user message to message history
        await add_message_to_history(
            role="user", content=query, session_id=session_id, metadata={"agent_name": self.agent_name}
        )
        # Initialize messages with current message history (only once at start)
        await self.update_llm_working_memory(
            message_history=message_history, session_id=session_id
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
            while self.state != AgentState.FINISHED and current_steps < self.max_steps:
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
                    self.messages[self.agent_name].append(
                        Message(
                            role="assistant",
                            content=parsed_response.answer,
                        )
                    )
                    await add_message_to_history(
                        role="assistant",
                        content=parsed_response.answer,
                        session_id=session_id,
                        metadata={"agent_name": self.agent_name},
                    )
                    # check if the system prompt has changed
                    if system_prompt != self.messages[self.agent_name][0].content:
                        # Reset system prompt and keep all messages
                        self.messages[self.agent_name] = await self.reset_system_prompt(
                            self.messages[self.agent_name], system_prompt
                        )
                    if debug:
                        logger.info(
                            f"Agent state changed from {self.state} to {AgentState.FINISHED}"
                        )
                    self.state = AgentState.FINISHED
                    # reset the steps
                    current_steps = 0
                    return parsed_response.answer

                elif parsed_response.action is not None:
                    # set the state to tool calling
                    if debug:
                        logger.info(
                            f"Agent state changed from {self.state} to {AgentState.TOOL_CALLING}"
                        )
                    self.state = AgentState.TOOL_CALLING

                    await self.act(
                        parsed_response=parsed_response,
                        response=response,
                        add_message_to_history=add_message_to_history,
                        system_prompt=system_prompt,
                        debug=debug,
                        sessions=sessions,
                        available_tools=available_tools,
                        local_tools=local_tools,
                        session_id=session_id,
                    )
                    continue
                # append the invalid response to the messages and the message history
                elif parsed_response.error is not None:
                    error_message = parsed_response.error
                else:
                    error_message = "Invalid response format. Please use the correct required format"

                self.messages[self.agent_name].append(
                    Message(role="user", content=error_message)
                )
                await add_message_to_history(
                    
                    role="user",
                    content=error_message,
                    session_id=session_id,
                    metadata={"agent_name": self.agent_name},
                )
                self.loop_detector.record_message(error_message, response)
                if self.loop_detector.is_looping():
                    logger.warning("Loop detected")
                    new_system_prompt = handle_stuck_state(
                        system_prompt, message_stuck_prompt=True
                    )
                    self.messages[self.agent_name] = await self.reset_system_prompt(
                        messages=self.messages[self.agent_name],
                        system_prompt=new_system_prompt,
                    )
                    loop_message = (
                        f"Observation:\n"
                        f"⚠️ Message loop detected: {self.loop_detector.get_loop_type()}\n"
                        f"The message stuck is: {error_message}\n"
                        f"Current approach is not working. Please:\n"
                        f"1. Analyze why the previous attempts failed\n"
                        f"2. Try a completely different tool or approach\n"
                        f"3. If the issue persists, please provide a detailed description of the problem and the current state of the conversation. and don't try again.\n"
                    )
                    self.messages[self.agent_name].append(
                        Message(role="user", content=loop_message)
                    )
                    if debug:
                        logger.info(
                            f"Agent state changed from {self.state} to {AgentState.STUCK}"
                        )
                    self.state = AgentState.STUCK
                    self.loop_detector.reset()

            # If we've reached max steps, return the last response
            if current_steps >= self.max_steps:
                return f"Maximum steps ({self.max_steps}) reached. Last response: {response}"

            return None
