import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from omnicoreagent.core.agents.tool_calling_agent import ToolCallingAgent
from omnicoreagent.core.agents.types import AgentConfig


@pytest.fixture
def agent_config():
    return AgentConfig(
        agent_name="TestAgent",
        mcp_enabled=True,
        request_limit=10,
        total_tokens_limit=1000,
        tool_call_timeout=60,
        max_steps=10,
    )


@pytest.fixture
def agent(agent_config):
    return ToolCallingAgent(config=agent_config, debug=True)


@pytest.mark.asyncio
async def test_update_llm_working_memory_user_and_assistant(agent):
    message_history = AsyncMock(
        return_value=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!", "metadata": {}},
        ]
    )
    await agent.update_llm_working_memory(message_history, "chat1")
    assert agent.messages == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]


@pytest.mark.asyncio
async def test_update_llm_working_memory_with_tool_calls(agent):
    message_history = AsyncMock(
        return_value=[
            {"role": "user", "content": "Run a tool"},
            {
                "role": "assistant",
                "content": "Calling tool",
                "metadata": {
                    "has_tool_calls": True,
                    "tool_calls": [{"name": "example_tool"}],
                },
            },
            {
                "role": "tool",
                "content": "tool output",
                "metadata": {"tool_call_id": "123"},
            },
        ]
    )
    await agent.update_llm_working_memory(message_history, "chat1")
    assert agent.messages == [
        {"role": "user", "content": "Run a tool"},
        {
            "role": "assistant",
            "content": "Calling tool",
            "tool_calls": [{"name": "example_tool"}],
        },
        {"role": "tool", "content": "tool output", "tool_call_id": "123"},
    ]


@pytest.mark.asyncio
async def test_list_available_tools_with_mcp(agent):
    tool_mock = MagicMock()
    tool_mock.name = "do_something"
    tool_mock.description = "desc"
    tool_mock.inputSchema = {"type": "object"}

    result = await agent.list_available_tools(
        available_tools={"server1": [tool_mock]}, tools_registry=None
    )

    assert result == [
        {
            "type": "function",
            "function": {
                "name": "do_something",
                "description": "desc",
                "parameters": {"type": "object"},
            },
        }
    ]


@pytest.mark.asyncio
async def test_list_available_tools_with_registry():
    agent_config = AgentConfig(
        agent_name="LocalOnly",
        mcp_enabled=False,
        request_limit=10,
        total_tokens_limit=1000,
        tool_call_timeout=60,
        max_steps=10,
    )
    agent = ToolCallingAgent(config=agent_config)

    registry = {
        "sum_numbers": {
            "description": "Add two numbers",
            "inputSchema": {"a": "int", "b": "int"},
        }
    }

    result = await agent.list_available_tools(
        available_tools=None, tools_registry=registry
    )

    assert result == [
        {
            "type": "function",
            "function": {
                "name": "sum_numbers",
                "description": "Add two numbers",
                "parameters": {"a": "int", "b": "int"},
            },
        }
    ]


@pytest.mark.asyncio
async def test_execute_tool_call_mcp(agent):
    tool = MagicMock()
    tool.name = "add"
    available_tools = {"server1": [tool]}
    sessions = {"server1": {"session": AsyncMock()}}
    sessions["server1"]["session"].call_tool.return_value = {"result": 3}

    tool_call = MagicMock()
    tool_call.id = "test-tool-call-id"

    result = await agent.execute_tool_call(
        chat_id="chat1",
        tool_name="add",
        tool_args=json.dumps({"a": 1, "b": 2}),
        tool_call=tool_call,
        add_message_to_history=AsyncMock(),
        available_tools=available_tools,
        tools_registry=None,
        sessions=sessions,
    )

    assert "result" in result or result is not None


@pytest.mark.asyncio
async def test_execute_tool_call_raises_when_both_sources_provided(agent):
    with pytest.raises(ValueError):
        await agent.execute_tool_call(
            chat_id="chat1",
            tool_name="tool",
            tool_args={},
            tool_call={},
            add_message_to_history=AsyncMock(),
            available_tools={"server": []},
            tools_registry={"tool": {}},
            sessions={},
        )


@pytest.mark.asyncio
async def test_execute_tool_call_raises_when_no_sources(agent):
    with pytest.raises(ValueError):
        await agent.execute_tool_call(
            chat_id="chat1",
            tool_name="tool",
            tool_args={},
            tool_call={},
            add_message_to_history=AsyncMock(),
            available_tools=None,
            tools_registry=None,
            sessions={},
        )


@pytest.mark.asyncio
async def test_execute_tool_call_with_invalid_json(agent):
    available_tools = {"server1": ["tool_name"]}
    sessions = {"server1": {"session": AsyncMock()}}
    sessions["server1"]["session"].call_tool.return_value = {"result": "ok"}

    # Mock tool_call to have an 'id' attribute
    tool_call = MagicMock()
    tool_call.id = "test-tool-call-id"

    result = await agent.execute_tool_call(
        chat_id="chat1",
        tool_name="tool_name",
        tool_args="{invalid_json}",
        tool_call=tool_call,
        add_message_to_history=AsyncMock(),
        available_tools=available_tools,
        tools_registry=None,
        sessions=sessions,
    )

    assert "result" in result or result is not None
