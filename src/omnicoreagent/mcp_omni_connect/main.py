import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from decouple import config as decouple_config

from omnicoreagent.mcp_omni_connect.cli import MCPClientCLI
from omnicoreagent.mcp_omni_connect.client import Configuration, MCPClient
from omnicoreagent.core.utils import logger

load_dotenv()

DEFAULT_CONFIG_NAME = "servers_config.json"


def validate_config(config_path: Path):
    """Validate that the config file has valid server configurations"""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        # Check if mcpServers section exists and has content
        if "mcpServers" not in config:
            logger.error("❌ Configuration missing 'mcpServers' section")
            logger.info(
                "💡 Please add your MCP server configurations to the 'mcpServers' section."
            )
            return False

        servers = config["mcpServers"]
        if not servers:
            logger.error("❌ Configuration has empty 'mcpServers' section")
            logger.info(
                "💡 Please add your MCP server configurations to the 'mcpServers' section."
            )
            return False

        # Check for example/template servers
        example_servers = ["server_name1", "server_name2", "server_name3"]
        if all(server in servers for server in example_servers):
            logger.error("❌ Configuration still contains template servers")
            logger.info(
                "💡 Please replace the example servers with your actual MCP server configurations."
            )
            return False

        # Check LLM section for template values
        if "LLM" not in config:
            logger.error("❌ Configuration missing 'LLM' section")
            logger.info("💡 Please add your LLM configuration to the 'LLM' section.")
            return False

        llm_config = config["LLM"]
        template_llm_values = ["provider_name", "model_name"]

        if llm_config.get("provider") in template_llm_values:
            logger.error("❌ Configuration still contains template LLM provider")
            logger.info(
                "💡 Please replace 'provider_name' with your actual LLM provider (e.g., 'openai', 'anthropic', 'openrouter')."
            )
            return False

        if llm_config.get("model") in template_llm_values:
            logger.error("❌ Configuration still contains template LLM model")
            logger.info(
                "💡 Please replace 'model_name' with your actual model name (e.g., 'gpt-4', 'claude-3-sonnet')."
            )
            return False

        logger.info(f"✅ Configuration validated: {len(servers)} server(s) configured")
        return True

    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON in configuration file")
        return False
    except Exception as e:
        logger.error(f"❌ Error validating configuration: {e}")
        return False


def check_config_exists():
    """Check if config file exists and provide guidance if missing"""
    config_path = Path.cwd() / DEFAULT_CONFIG_NAME

    if not config_path.exists():
        logger.warning(
            f"Configuration file '{DEFAULT_CONFIG_NAME}' not found. Creating default template..."
        )
        logger.info(
            "Please update the configuration file with your actual MCP server configuration."
        )

        default_config = {
            "AgentConfig": {
                "tool_call_timeout": 30,
                "max_steps": 15,
                "request_limit": 0,
                "total_tokens_limit": 0,
                "memory_results_limit": 5,
                "memory_similarity_threshold": 0.5,
            },
            "LLM": {
                "provider": "provider_namer",
                "model": "model_name",
                "temperature": 0.5,
                "max_tokens": 5000,
                "max_context_length": 30000,
                "top_p": 0,
            },
            "mcpServers": {
                "server_name1": {
                    "transport_type": "stdio",
                    "command": "mcp-server",
                    "args": [],
                    "env": {},
                },
                "server_name2": {
                    "transport_type": "sse",
                    "url": "https://example.com/sse",
                    "headers": {},
                    "timeout": 60,
                    "sse_read_timeout": 120,
                },
                "server_name3": {
                    "transport_type": "streamable_http",
                    "url": "https://example.com/mcp",
                    "headers": {},
                    "timeout": 60,
                    "sse_read_timeout": 120,
                },
            },
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)

        logger.info(f"Default configuration template created at {config_path}")
        logger.info(
            "⚠️  Please update the configuration with your actual MCP servers and restart the application."
        )
        logger.info(
            "💡 Example: Update the 'mcpServers' section with your real server configurations."
        )

        # Exit gracefully instead of continuing with invalid config
        import sys

        sys.exit(1)

    return config_path


async def async_main():
    client = None

    try:
        api_key = decouple_config("LLM_API_KEY", default=None)
        if not api_key:
            raise RuntimeError(
                "LLM_API_KEY environment variable is missing. Please set it in your environment or .env file."
            )

        config_path = check_config_exists()

        # Validate the configuration before proceeding
        if not validate_config(config_path):
            logger.error(
                "❌ Configuration validation failed. Please fix the issues above and restart."
            )
            return

        logger.debug(f"Configuration read in from {config_path}")
        config = Configuration()
        client = MCPClient(config, config_filename=str(config_path))
        # Use the LLMConnection from MCPClient to avoid duplication
        llm_connection = client.llm_connection
        if llm_connection is None:
            logger.error(
                "LLM configuration is required but not available. Please check your LLM configuration in servers_config.json"
            )
            return

        cli = MCPClientCLI(client, llm_connection)
        await client.connect_to_servers()
        # load the mcp tools to knowledge base if its enabled
        await cli.async_init()

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
