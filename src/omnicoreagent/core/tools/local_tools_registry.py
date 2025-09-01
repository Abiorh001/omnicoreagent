import inspect
import asyncio
from collections.abc import Callable
from typing import Any, Dict, List


class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        inputSchema: dict[str, Any],
        function: Callable,
    ):
        self.name = name
        self.description = description
        self.inputSchema = inputSchema
        self.function = function
        self.is_async = asyncio.iscoroutinefunction(function)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema,
            "function": self.function,
        }

    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute the tool with extracted parameters"""
        # Extract parameters from the dict based on function signature
        sig = inspect.signature(self.function)
        func_params = {}

        for param_name, param in sig.parameters.items():
            if param_name in parameters:
                func_params[param_name] = parameters[param_name]
            elif param.default is not inspect.Parameter.empty:
                func_params[param_name] = param.default
            else:
                raise ValueError(f"Missing required parameter: {param_name}")

        # Execute the function
        if self.is_async:
            return await self.function(**func_params)
        else:
            return self.function(**func_params)

    def __repr__(self):
        return f"<Tool name={self.name} async={self.is_async}>"


class ToolRegistry:
    """Registry for local tools that can be executed by agents."""

    def __init__(self):
        self.tools = {}
        self.tool_descriptions = {}
        self.tool_schemas = {}

    def __str__(self):
        """Return a readable string representation of the ToolRegistry."""
        tool_count = len(self.tools)
        tool_names = list(self.tools.keys())
        return f"ToolRegistry({tool_count} tools: {', '.join(tool_names[:3])}{'...' if tool_count > 3 else ''})"

    def __repr__(self):
        """Return a detailed representation of the ToolRegistry."""
        return self.__str__()

    def register_tool(
        self,
        name: str | None = None,
        inputSchema: dict[str, Any] | None = None,
        description: str = "",
    ):
        def decorator(func: Callable):
            tool_name = name or func.__name__.lower()

            # Prefer explicit description, else docstring, else fallback
            final_description = description or (
                func.__doc__ or "No description provided."
            )

            # Prefer explicit schema, else infer from signature + docstring
            final_schema = inputSchema or self._infer_schema(func)

            tool = Tool(
                name=tool_name,
                description=final_description.strip(),
                inputSchema=final_schema,
                function=func,
            )
            self.tools[tool_name] = tool
            return func

        return decorator

    def get_tool(self, name: str) -> Tool | None:
        return self.tools.get(name.lower())

    def list_tools(self) -> list[Tool]:
        return list(self.tools.values())

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for OmniAgent"""
        tools = []
        for tool in self.list_tools():
            tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                    "type": "local",
                }
            )
        return tools

    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all tool schemas for MCP integration"""
        schemas = {}
        for tool in self.tools.values():
            schemas[tool.name] = {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }
        return schemas

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool by name with parameters"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        return await tool.execute(parameters)

    # def _infer_schema(self, func: Callable) -> dict[str, Any]:
    #     sig = inspect.signature(func)
    #     props = {}
    #     required = []

    #     for param_name, param in sig.parameters.items():
    #         # Skip 'self' parameter for methods
    #         if param_name == "self":
    #             continue

    #         param_type = (
    #             param.annotation
    #             if param.annotation is not inspect.Parameter.empty
    #             else str
    #         )

    #         props[param_name] = {"type": self._map_type(param_type)}

    #         # Add description if available from docstring
    #         if func.__doc__:
    #             # Simple docstring parsing for parameter descriptions
    #             doc_lines = func.__doc__.split("\n")
    #             for line in doc_lines:
    #                 if line.strip().startswith(f"{param_name}:"):
    #                     props[param_name]["description"] = line.split(":", 1)[1].strip()
    #                     break

    #         if param.default is inspect.Parameter.empty:
    #             required.append(param_name)

    #     return {
    #         "type": "object",
    #         "properties": props,
    #         "required": required,
    #         "additionalProperties": False,
    #     }

    def _infer_schema(self, func: Callable) -> dict[str, Any]:
        sig = inspect.signature(func)
        props = {}
        required = []

        # Extract docstring lines for parameter descriptions
        docstring = func.__doc__ or ""
        doc_lines = [line.strip() for line in docstring.split("\n") if ":" in line]

        param_docs = {}
        for line in doc_lines:
            parts = line.split(":", 1)
            if len(parts) == 2:
                param_docs[parts[0].strip()] = parts[1].strip()

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = (
                param.annotation
                if param.annotation is not inspect.Parameter.empty
                else str
            )
            schema = {"type": self._map_type(param_type)}

            # Attach description if found in docstring
            if param_name in param_docs:
                schema["description"] = param_docs[param_name]

            props[param_name] = schema

            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": props,
            "required": required,
            "additionalProperties": False,
        }

    def _map_type(self, typ: Any) -> str:
        type_map = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
            list: "array",
            dict: "object",
        }
        return type_map.get(typ, "string")
