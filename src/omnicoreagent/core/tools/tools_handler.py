import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any
from omnicoreagent.core.utils import logger


class BaseToolHandler(ABC):
    @abstractmethod
    async def validate_tool_call_request(
        self,
        tool_data: dict[str, Any],
        available_tools: dict[str, Any] | list[str],
    ) -> Any:
        pass

    @abstractmethod
    async def call(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        pass


class MCPToolHandler(BaseToolHandler):
    def __init__(
        self,
        sessions: dict,
        server_name: str = None,
        tool_data: str = None,
        mcp_tools: dict = None,
    ):
        self.sessions = sessions
        self.server_name = server_name

        # If server_name not passed in, infer it from tool_data
        if self.server_name is None and tool_data and mcp_tools:
            self.server_name = self._infer_server_name(tool_data, mcp_tools)

    def _infer_server_name(
        self, tool_data: str, mcp_tools: dict[str, Any]
    ) -> str | None:
        try:
            action = json.loads(tool_data)
            input_tool_name = action.get("tool", "").strip().lower()

            for server_name, tools in mcp_tools.items():
                for tool in tools:
                    if tool.name.lower() == input_tool_name:
                        return server_name
        except (json.JSONDecodeError, AttributeError, KeyError):
            pass
        return None

    async def validate_tool_call_request(
        self, tool_data: str, mcp_tools: dict[str, Any]
    ) -> dict:
        try:
            action = json.loads(tool_data)
            input_tool_name = action.get("tool", "").strip()
            tool_args = action.get("parameters")

            if not input_tool_name:
                return {
                    "error": "Invalid JSON format. Check the action format again.",
                    "action": False,
                    "tool_name": input_tool_name,
                    "tool_args": tool_args,
                }

            input_tool_name_lower = input_tool_name.lower()

            for server_name, tools in mcp_tools.items():
                for tool in tools:
                    if tool.name.lower() == input_tool_name_lower:
                        return {
                            "action": True,
                            "tool_name": tool.name,
                            "tool_args": tool_args,
                            "server_name": server_name,
                        }

            return {
                "action": False,
                "error": f"The tool named '{input_tool_name}' does not exist in the available tools.",
                "tool_name": input_tool_name,
                "tool_args": tool_args,
            }

        except json.JSONDecodeError as e:
            return {
                "error": f"Json decode error: Invalid JSON format: {e}",
                "action": False,
                "tool_name": "N/A",
                "tool_args": None,
            }

    async def call(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        session = self.sessions[self.server_name]["session"]
        return await session.call_tool(tool_name, tool_args)


class LocalToolHandler(BaseToolHandler):
    def __init__(self, local_tools: Any = None):
        """Initialize LocalToolHandler with LocalToolsIntegration instance"""
        self.local_tools = local_tools

    async def validate_tool_call_request(
        self,
        tool_data: str,
        local_tools: Any = None,  # Not used for local tools
    ) -> dict[str, Any]:
        try:
            action = json.loads(tool_data)
            tool_name = action.get("tool", "").strip()
            tool_args = action.get("parameters")

            if not tool_name or tool_args is None:
                return {
                    "error": "Missing 'tool' name or 'parameters' in the request.",
                    "action": False,
                    "tool_name": tool_name,
                    "tool_args": tool_args,
                }

            # Check if tool exists in local tools
            available_local_tools = local_tools.get_available_tools()
            tool_names = [tool["name"] for tool in available_local_tools]

            if tool_name in tool_names:
                return {
                    "action": True,
                    "tool_name": tool_name,
                    "tool_args": tool_args,
                }

            error_message = (
                f"The tool named '{tool_name}' does not exist in the current available tools. "
                "Please double-check the available tools before attempting another action.\n\n"
                "I will not retry the same tool name since it's not defined. "
                "If an alternative method or tool is available to fulfill the request, I'll try that now. "
                "Otherwise, I'll respond directly based on what I know."
            )
            return {
                "action": False,
                "error": error_message,
                "tool_name": tool_name,
                "tool_args": tool_args,
            }

        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON format",
                "action": False,
                "tool_name": "N/A",
                "tool_args": None,
            }

    async def call(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Execute a local tool using LocalToolsIntegration"""
        return await self.local_tools.execute_tool(tool_name, tool_args)


class ToolExecutor:
    def __init__(self, tool_handler: BaseToolHandler):
        self.tool_handler = tool_handler

    async def execute(
        self,
        agent_name: str,
        tool_name: str,
        tool_args: dict[str, Any],
        tool_call_id: str,
        add_message_to_history: Callable[[str, str, dict | None], Any],
        llm_connection: Callable,
        mcp_tools: dict,
        session_id: str = None,
        **kwargs,
    ) -> str:
        try:
            if tool_name.lower().strip() == "tools_retriever":
                tool_args["llm_connection"] = llm_connection
                tool_args["mcp_tools"] = mcp_tools
                tool_args["top_k"] = kwargs.get("top_k")
                tool_args["similarity_threshold"] = kwargs.get("similarity_threshold")
            result = await self.tool_handler.call(tool_name, tool_args)
            if tool_name.lower().strip() == "tools_retriever":
                del tool_args["llm_connection"]
                del tool_args["mcp_tools"]
                del tool_args["top_k"]
                del tool_args["similarity_threshold"]

            if isinstance(result, dict):
                # Handle structured dict responses (local tools)
                if result.get("status") == "success":
                    tool_result = result.get("data", result)
                    response = {"status": "success", "data": tool_result}
                elif result.get("status") == "error":
                    response = result  # Keep error as-is
                else:
                    # Dict without status field - treat as data
                    response = {"status": "success", "data": result}
            elif hasattr(result, "content"):
                # Handle MCP-style responses
                tool_content = result.content
                tool_result = (
                    tool_content[0].text
                    if isinstance(tool_content, list)
                    else tool_content
                )
                response = {"status": "success", "data": tool_result}
            else:
                # Handle raw responses (strings, numbers, etc.) - common for simple tools
                response = {"status": "success", "data": result}

            tool_content = response.get("data")
            # Only flag as error if tool_content is explicitly None (not empty string, list, etc.)
            # Empty results might be valid responses from tools
            if tool_content is None:
                response = {
                    "status": "error",
                    "message": (
                        f"Tool '{tool_name}' returned None/null result. This might indicate:\n"
                        f"1. Tool execution failed silently\n"
                        f"2. Tool doesn't support the provided parameters\n"
                        f"3. Network/connection issue (for MCP tools)\n"
                        f"Please verify tool parameters or try a different approach."
                    ),
                }
                tool_content = response["message"]

            await add_message_to_history(
                role="tool",
                content=tool_content,
                metadata={
                    "tool_call_id": tool_call_id,
                    "tool": tool_name,
                    "args": tool_args,
                    "agent_name": agent_name,
                },
                session_id=session_id,
            )

            return json.dumps(response)

        except Exception as e:
            error_response = {
                "status": "error",
                "message": (
                    f"Error: {str(e)}. Please try again or use a different approach. "
                    "If the issue persists, please provide a detailed description of the problem and "
                    "the current state of the conversation. And stop immediately, do not try again."
                ),
            }
            await add_message_to_history(
                role="tool",
                content=error_response["message"],
                metadata={
                    "tool_call_id": tool_call_id,
                    "tool": tool_name,
                    "args": tool_args,
                    "agent_name": agent_name,
                },
                session_id=session_id,
            )
            return json.dumps(error_response)
