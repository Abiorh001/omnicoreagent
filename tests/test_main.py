import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from omnicoreagent.mcp_omni_connect.main import async_main, check_config_exists


@pytest.fixture
def mock_config_path(tmp_path):
    """Create a temporary config path"""
    return tmp_path / "servers_config.json"


def test_check_config_exists_new(mock_config_path):
    """Test creating a new config file when it doesn't exist"""
    with patch("mcpomni_connect.main.Path.cwd", return_value=mock_config_path.parent):
        config_path = check_config_exists()

        assert config_path == mock_config_path
        assert config_path.exists()

        # Verify default config contents
        with open(config_path) as f:
            config = json.load(f)
            assert "LLM" in config
            assert "mcpServers" in config
            assert config["LLM"]["model"] == "qwen/qwq-32b:free"
            assert config["LLM"]["temperature"] == 0.5
            assert config["LLM"]["max_tokens"] == 5000
            assert config["LLM"]["top_p"] == 0
            assert "server_name1" in config["mcpServers"]


def test_check_config_exists_existing(mock_config_path):
    """Test when config file already exists"""
    # Create existing config with custom values
    existing_config = {
        "LLM": {
            "model": "qwen/qwq-32b:free",
            "temperature": 0.8,
            "max_tokens": 1000,
            "top_p": 0.1,
            "max_input_tokens": 1000,
            "provider": "openrouter",
        },
        "mcpServers": {
            "custom_server": {
                "transport_type": "stdio",
                "command": "custom-command",
                "args": ["arg1", "arg2"],
                "env": {"KEY": "value"},
            }
        },
    }
    with open(mock_config_path, "w") as f:
        json.dump(existing_config, f)

    with patch("mcpomni_connect.main.Path.cwd", return_value=mock_config_path.parent):
        config_path = check_config_exists()

        assert config_path == mock_config_path
        assert config_path.exists()

        # Verify existing config was not modified
        with open(config_path) as f:
            config = json.load(f)
            assert config == existing_config


@pytest.mark.asyncio
async def test_async_main_success():
    """Test successful async_main execution"""
    mock_config = Mock()
    mock_client = AsyncMock()  # Use AsyncMock for async methods
    mock_llm_connection = Mock()
    mock_cli = Mock()

    with (
        patch("mcpomni_connect.main.check_config_exists") as mock_check_config,
        patch("mcpomni_connect.main.Configuration", return_value=mock_config),
        patch("mcpomni_connect.main.MCPClient", return_value=mock_client),
        patch(
            "mcpomni_connect.main.LLMConnection",
            return_value=mock_llm_connection,
        ),
        patch("mcpomni_connect.main.MCPClientCLI", return_value=mock_cli),
    ):
        await async_main()

        mock_check_config.assert_called_once()
        mock_client.connect_to_servers.assert_called_once()
        mock_cli.chat_loop.assert_called_once()
        mock_client.cleanup.assert_called_once()  # Ensure cleanup is called


@pytest.mark.asyncio
async def test_async_main_keyboard_interrupt():
    """Test async_main handling of KeyboardInterrupt"""
    mock_config = Mock()
    mock_client = AsyncMock()  # Use AsyncMock
    mock_llm_connection = Mock()
    mock_cli = Mock()
    mock_cli.chat_loop.side_effect = KeyboardInterrupt()

    with (
        patch("mcpomni_connect.main.check_config_exists") as mock_check_config,
        patch("mcpomni_connect.main.Configuration", return_value=mock_config),
        patch("mcpomni_connect.main.MCPClient", return_value=mock_client),
        patch(
            "mcpomni_connect.main.LLMConnection",
            return_value=mock_llm_connection,
        ),
        patch("mcpomni_connect.main.MCPClientCLI", return_value=mock_cli),
    ):
        await async_main()

        mock_check_config.assert_called_once()
        mock_client.connect_to_servers.assert_called_once()
        mock_cli.chat_loop.assert_called_once()
        mock_client.cleanup.assert_called_once()


@pytest.mark.asyncio
async def test_async_main_error():
    """Test async_main handling of general exceptions"""
    mock_config = Mock()
    mock_client = AsyncMock()  # Use AsyncMock
    mock_llm_connection = Mock()
    mock_cli = Mock()
    mock_cli.chat_loop.side_effect = Exception("Test error")

    with (
        patch("mcpomni_connect.main.check_config_exists") as mock_check_config,
        patch("mcpomni_connect.main.Configuration", return_value=mock_config),
        patch("mcpomni_connect.main.MCPClient", return_value=mock_client),
        patch(
            "mcpomni_connect.main.LLMConnection",
            return_value=mock_llm_connection,
        ),
        patch("mcpomni_connect.main.MCPClientCLI", return_value=mock_cli),
    ):
        await async_main()

        mock_check_config.assert_called_once()
        mock_client.connect_to_servers.assert_called_once()
        mock_cli.chat_loop.assert_called_once()
        mock_client.cleanup.assert_called_once()


@pytest.mark.OpenAIIntegration
def test_main():
    """Test main function"""
    from omnicoreagent.mcp_omni_connect.main import main

    with patch(
        "mcpomni_connect.main.async_main", new_callable=AsyncMock
    ) as mock_async_main:
        main()
        mock_async_main.assert_called_once()
