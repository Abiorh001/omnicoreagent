# Installation

## Prerequisites

Before installing MCPOmni Connect, ensure you have the following:

!!! info "System Requirements"
    - **Python 3.10+** (Python 3.11+ recommended)
    - **LLM API key** from any supported provider
    - **UV package manager** (recommended) or pip
    - **Redis server** (optional, for persistent memory)

### Check Python Version

```bash
python --version
# Should show Python 3.10.0 or higher
```

### Install UV (Recommended)

UV is the fastest Python package manager and is recommended for MCPOmni Connect:

=== "macOS/Linux"
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"
    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

=== "Python pip"
    ```bash
    pip install uv
    ```

## Installation Methods

### Method 1: UV (Recommended)

```bash
uv add mcpomni-connect
```

### Method 2: pip

```bash
pip install mcpomni-connect
```

### Method 3: From Source

For development or latest features:

```bash
git clone https://github.com/Abiorh001/mcp_omni_connect.git
cd mcp_omni_connect
uv sync
```

## Verify Installation

After installation, verify MCPOmni Connect is correctly installed:

```bash
mcpomni_connect --version
```

You should see the version number displayed.

## Optional Dependencies

### Redis (For Persistent Memory)

MCPOmni Connect can use Redis for persistent conversation memory:

=== "Ubuntu/Debian"
    ```bash
    sudo apt update
    sudo apt install redis-server
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    ```

=== "macOS"
    ```bash
    brew install redis
    brew services start redis
    ```

=== "Windows"
    Download from [Redis Windows releases](https://github.com/microsoftarchive/redis/releases) or use WSL with Linux instructions.

=== "Docker"
    ```bash
    docker run -d --name redis -p 6379:6379 redis:alpine
    ```

### Verify Redis Connection

```bash
redis-cli ping
# Should respond with: PONG
```

## Next Steps

Once installation is complete:

1. **[Set up configuration](../configuration/configuration-guide.md)** - Create your `.env` and `servers_config.json` files
2. **[Follow the Quick Start guide](quick-start.md)** - Get your first MCP connection working
3. **[Explore operation modes](../user-guide/operation-modes.md)** - Learn about chat, autonomous, and orchestrator modes

## Troubleshooting Installation

### Common Issues

!!! failure "Python Version Error"
    **Error**: `MCPOmni Connect requires Python 3.10+`

    **Solution**: Upgrade your Python version:
    ```bash
    # Check available Python versions
    python3.10 --version  # or python3.11, python3.12

    # Use specific Python version with UV
    uv python install 3.11
    uv add mcpomni-connect
    ```

!!! failure "Permission Denied"
    **Error**: Permission denied during installation

    **Solution**: Use user installation:
    ```bash
    pip install --user mcpomni-connect
    ```

!!! failure "Command Not Found"
    **Error**: `mcpomni_connect: command not found`

    **Solution**: Add to PATH or use full path:
    ```bash
    # Check installation path
    pip show mcpomni-connect

    # Or run with python -m
    python -m mcpomni_connect
    ```

### Getting Help

If you encounter issues:

1. Check the [troubleshooting guide](../configuration/troubleshooting.md)
2. Search [existing issues](https://github.com/Abiorh001/mcp_omni_connect/issues)
3. Create a [new issue](https://github.com/Abiorh001/mcp_omni_connect/issues/new) with:
   - Your operating system
   - Python version
   - Installation method used
   - Complete error message

---

**Next**: [Quick Start Guide →](quick-start.md)
