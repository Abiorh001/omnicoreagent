# tools_registry = {

# }
# async def add(parameters: dict):
#     """add two numbers together
#     args:
#     a: int
#     b: int
#     return:
#     a+b

#     """
#     a = parameters["a"]
#     b = parameters["b"]
#     return a + b


# add_schema = {
#     "type": "object",
#     "properties": {
#         "a": {"type": "number"},
#         "b": {"type": "number"}
#     },
#     "required": ["a", "b"],
#     "additionalProperties": False
# }
# add_description = "adds two numbers provided in the 'parameters' dictionary. Expects 'a' and 'b' as numeric values and returns their sum."


# def register_tool(name: str, function: Callable, description: str, inputSchema: Dict[str, Any]) -> None:
#     """Register a new tool with JSON schema"""
#     # Add to the tools dictionary with name as key and function/schema as values
#     tools_registry[name.lower()] = {"function": function, "inputSchema": inputSchema, "description": description}


#     return tools_registry[name.lower()]

# register_tool(
#     name="add",
#     function=add,
#     description=add_description,
#     inputSchema=add_schema,
# )
# TODO still working on this
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry

tool_registry = ToolRegistry()


@tool_registry.register(
    name="add",
    inputSchema={
        "type": "object",
        "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
        "required": ["a", "b"],
        "additionalProperties": False,
    },
    description="Adds two numbers.",
)
async def add(parameters: dict):
    """add two numbers together
    args:
    a: int
    b: int
    return:
    a+b

    """
    a = parameters["a"]
    b = parameters["b"]
    return a + b


for tool in tool_registry.list_tools():
    print(tool.name, tool.description)
