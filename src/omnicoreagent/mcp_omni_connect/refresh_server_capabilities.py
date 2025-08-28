from collections.abc import Callable
from typing import Any

from omnicoreagent.core.constants import AGENTS_REGISTRY
from omnicoreagent.core.utils import logger


async def generate_react_agent_role_prompt_func(
    available_tools: dict[str, Any],
    server_name: str,
    llm_connection: Callable,
    generate_react_agent_role_prompt: Callable,
) -> str:
    """Generate the react agent role prompt"""
    react_agent_role_prompt = generate_react_agent_role_prompt(
        available_tools=available_tools,
        server_name=server_name,
    )
    messages = [
        {"role": "system", "content": react_agent_role_prompt},
        {"role": "user", "content": "Generate the agent role prompt"},
    ]
    response = await llm_connection.llm_call(messages)
    if response:
        if hasattr(response, "choices"):
            response = response.choices[0].message.content.strip()
        elif hasattr(response, "message"):
            response = response.message.content.strip()
        return response
    else:
        return ""


async def refresh_capabilities(
    sessions: dict[str, Any],
    server_names: list[str],
    available_tools: dict[str, Any],
    available_resources: dict[str, Any],
    available_prompts: dict[str, Any],
    debug: bool,
    llm_connection: Callable,
    generate_react_agent_role_prompt: Callable,
    server_name: str = None,
) -> None:
    """Refresh the capabilities of the server and update system prompt"""
    for server_name in server_names:
        if not sessions.get(server_name, {}).get("connected", False):
            raise ValueError(f"Not connected to server: {server_name}")

        session = sessions[server_name].get("session")
        if not session:
            logger.warning(f"No session found for server: {server_name}")
            continue

        # List all tools
        try:
            tools_response = await session.list_tools()
            available_tools[server_name] = (
                tools_response.tools if tools_response else []
            )
        except Exception as e:
            logger.info(f"{server_name} does not support tools: {e}")
            available_tools[server_name] = []

        # List all resources
        try:
            resources_response = await session.list_resources()
            available_resources[server_name] = (
                resources_response.resources if resources_response else []
            )
        except Exception as e:
            logger.info(f"{server_name} does not support resources: {e}")
            available_resources[server_name] = []

        # List all prompts
        try:
            prompts_response = await session.list_prompts()
            available_prompts[server_name] = (
                prompts_response.prompts if prompts_response else []
            )
        except Exception as e:
            logger.info(f"{server_name} does not support prompts: {e}")
            available_prompts[server_name] = []
    # Generate the react agent role prompt
    if server_name:
        react_agent_role_prompt = await generate_react_agent_role_prompt_func(
            available_tools=available_tools,
            server_name=server_name,
            llm_connection=llm_connection,
            generate_react_agent_role_prompt=generate_react_agent_role_prompt,
        )
        AGENTS_REGISTRY[server_name] = react_agent_role_prompt
    else:
        for _server_name in server_names:
            react_agent_role_prompt = await generate_react_agent_role_prompt_func(
                available_tools=available_tools,
                server_name=_server_name,
                llm_connection=llm_connection,
                generate_react_agent_role_prompt=generate_react_agent_role_prompt,
            )
            AGENTS_REGISTRY[_server_name] = react_agent_role_prompt
    if debug:
        logger.info(f"Agents Registry: {AGENTS_REGISTRY}")
    if debug:
        logger.info(f"Refreshed capabilities for {server_names}")

        for category, data in {
            "Tools": available_tools,
            "Resources": available_resources,
            "Prompts": available_prompts,
        }.items():
            logger.info(f"Available {category.lower()} by server:")
            for server_name, items in data.items():
                logger.info(f"  {server_name}:")
                for item in items:
                    logger.info(f"    - {item.name}")

    if debug:
        logger.info("Updated system prompt with new capabilities")
