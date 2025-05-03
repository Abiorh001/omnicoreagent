import asyncio
import json
from pathlib import Path

from mcpomni_connect.cli import MCPClientCLI
from mcpomni_connect.client import Configuration, MCPClient
from mcpomni_connect.llm import LLMConnection
from mcpomni_connect.utils import logger
import os
from dotenv import load_dotenv


load_dotenv()

DEFAULT_CONFIG_NAME = "servers_config.json"


def check_config_exists():
    """Check if config file exists and provide guidance if missing"""
    config_path = Path.cwd() / DEFAULT_CONFIG_NAME

    if not config_path.exists():
        logger.warning(
            f"Configuration file '{DEFAULT_CONFIG_NAME}' not found. Creating default..."
        )
        logger.info(
            "Please ensure you update the configuration file with your MCP server configuration."
        )

        default_config = {
            "AgentConfig": {
                "tool_call_timeout": 30,
                "max_steps": 15,
                "request_limit": 1000,
                "total_tokens_limit": 100000,
            },
            "LLM": {
                "provider": "openrouter",
                "model": "qwen/qwq-32b:free",
                "temperature": 0.5,
                "max_tokens": 5000,
                "max_context_length": 30000,
                "top_p": 0,
            },
            "mcpServers": {
                "server_name": {
                    "type": "stdio",
                    "command": "mcp-server",
                    "args": [],
                    "env": {},
                }
            },
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)

        logger.info(f"Default configuration file created at {config_path}")

    return config_path


async def async_main():
    client = None

    try:
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            raise RuntimeError(
                "LLM_API_KEY environment variable is missing. Please set it in your environment or .env file."
            )
        config_path = check_config_exists()
        logger.debug(f"Configuration read in from {config_path}")
        config = Configuration()
        client = MCPClient(config)
        llm_connection = LLMConnection(config)
        cli = MCPClientCLI(client, llm_connection)

        await client.connect_to_servers()
        await cli.chat_loop()
    except KeyboardInterrupt:
        logger.info("Shutting down client...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        logger.info("Shutting down client...")
        if client:
            await client.cleanup()
        logger.info("Client shut down successfully")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
