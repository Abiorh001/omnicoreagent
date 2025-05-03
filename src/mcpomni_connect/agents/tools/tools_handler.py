from abc import ABC, abstractmethod
import inspect
from typing import Any, Callable, Dict, Optional, List
import json


class BaseToolHandler(ABC):
    @abstractmethod
    async def validate_tool_call_request(
        self,
        tool_data: Dict[str, Any],
        available_tools: Dict[str, Any] | List[str],
    ) -> Any:
        pass

    @abstractmethod
    async def call(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        pass


class MCPToolHandler(BaseToolHandler):
    def __init__(
        self,
        sessions: dict,
        server_name: str = None,
        tool_data: str = None,
        available_tools: dict = None,
    ):
        self.sessions = sessions
        self.server_name = server_name

        # If server_name not passed in, infer it from tool_data
        if self.server_name is None and tool_data and available_tools:
            self.server_name = self._infer_server_name(tool_data, available_tools)

    def _infer_server_name(
        self, tool_data: str, available_tools: dict[str, Any]
    ) -> Optional[str]:
        try:
            action = json.loads(tool_data)
            tool_name = action.get("tool", "").lower()

            for server_name, tools in available_tools.items():
                tool_names = [tool.name.lower() for tool in tools]
                if tool_name in tool_names:
                    return server_name
        except (json.JSONDecodeError, AttributeError, KeyError):
            pass
        return None

    async def validate_tool_call_request(
        self, tool_data: Dict[str, Any], available_tools: Dict[str, Any]
    ) -> dict:
        try:
            action = json.loads(tool_data)
            tool_name = action["tool"].strip().lower() if "tool" in action else None
            tool_args = action["parameters"] if "parameters" in action else None
            # if tool_name is None or tool_args is None, return an error
            if tool_name is None or tool_args is None:
                return {
                    "error": "Invalid JSON format",
                    "action": False,
                }

            # Validate JSON structure and tool exists
            if "tool" in action and "parameters" in action:
                for (
                    server_name,
                    tools,
                ) in available_tools.items():
                    tool_names = [tool.name.lower() for tool in tools]
                    if tool_name in tool_names:
                        return {
                            "action": True,
                            "tool_name": tool_name,
                            "tool_args": tool_args,
                            "server_name": server_name,
                        }
            error_message = (
                f"The tool named {tool_name} does not exist in the current available tools. "
                "Please double-check the available tools before attempting another action.\n\n"
                "I will not retry the same tool name since it's not defined. "
                "If an alternative method or tool is available to fulfill the request, I’ll try that now. "
                "Otherwise, I’ll respond directly based on what I know."
            )
            return {
                "action": False,
                "error": error_message,
            }
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON format",
                "action": False,
            }

    async def call(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        session = self.sessions[self.server_name]["session"]
        return await session.call_tool(tool_name, tool_args)


class LocalToolHandler(BaseToolHandler):
    def __init__(self, tools_registry: Dict[str, Any]):
        self.tools_registry = tools_registry

    async def validate_tool_call_request(
        self,
        tool_data: Dict[str, Any],
        available_tools: Dict[str, Any],  # tool registry
    ) -> Dict[str, Any]:
        try:
            action = json.loads(tool_data)
            tool_name = action.get("tool", "").strip().lower()
            tool_args = action.get("parameters")

            if not tool_name or tool_args is None:
                return {
                    "error": "Missing 'tool' name or 'parameters' in the request.",
                    "action": False,
                }

            # Normalize available tool names
            available_tools_normalized = {
                name.lower(): func for name, func in available_tools.items()
            }

            if tool_name in available_tools_normalized:
                return {
                    "action": True,
                    "tool_name": tool_name,
                    "tool_args": tool_args,
                }
            error_message = (
                f"The tool named {tool_name} does not exist in the current available tools. "
                "Please double-check the available tools before attempting another action.\n\n"
                "I will not retry the same tool name since it's not defined. "
                "If an alternative method or tool is available to fulfill the request, I’ll try that now. "
                "Otherwise, I’ll respond directly based on what I know."
            )
            return {"action": False, "error": error_message}

        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON format",
                "action": False,
            }

    async def call(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        tool_name = tool_name.strip().lower()
        tool_args = tool_args or {}

        # Normalize keys in the registry to match lookup
        normalized_registry = {
            name.lower(): func for name, func in self.tool_registry.items()
        }
        tool_fn = normalized_registry.get(tool_name)

        if not tool_fn:
            raise ValueError(f"Tool '{tool_name}' not found in local registry.")

        if inspect.iscoroutinefunction(tool_fn):
            return await tool_fn(**tool_args)

        return tool_fn(**tool_args)


class ToolExecutor:
    def __init__(self, tool_handler: BaseToolHandler):
        self.tool_handler = tool_handler

    async def execute(
        self,
        agent_name: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        tool_call_id: str,
        add_message_to_history: Callable[[str, str, Optional[dict]], Any],
        chat_id: str = None,
    ) -> str:
        try:
            result = await self.tool_handler.call(tool_name, tool_args)

            if isinstance(result, dict):
                if result.get("status") == "success":
                    tool_result = result.get("data", result)
                    response = {"status": "success", "data": tool_result}
                else:
                    response = result
            elif hasattr(result, "content"):
                tool_content = result.content
                tool_result = (
                    tool_content[0].text
                    if isinstance(tool_content, list)
                    else tool_content
                )
                response = {"status": "success", "data": tool_result}
            else:
                response = {"status": "success", "data": result}

            tool_content = response.get("data")
            if tool_content in (None, "", [], {}, "[]", "{}"):
                response = {
                    "status": "error",
                    "message": (
                        "No results found from the tool. Please try again or use a different approach. "
                        "If the issue persists, please provide a detailed description of the problem and "
                        "the current state of the conversation. And stop immediately, do not try again."
                    ),
                }
                tool_content = response["message"]

            await add_message_to_history(
                agent_name=agent_name,
                role="tool",
                content=tool_content,
                metadata={
                    "tool_call_id": tool_call_id,
                    "tool": tool_name,
                    "args": tool_args,
                },
                chat_id=chat_id,
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
                agent_name=agent_name,
                role="tool",
                content=error_response["message"],
                metadata={
                    "tool_call_id": tool_call_id,
                    "tool": tool_name,
                    "args": tool_args,
                },
                chat_id=chat_id,
            )
            return json.dumps(error_response)
