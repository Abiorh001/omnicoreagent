# Quick Start

This guide will get you up and running with MCPOmni Connect in under 5 minutes.

## Step 1: Basic Configuration

Create the two required configuration files:

### Create `.env` file

```bash
# Create .env file with your LLM API key
echo "LLM_API_KEY=your_api_key_here" > .env
```

!!! tip "Supported API Keys"
    You can use API keys from OpenAI, Anthropic, Google, Groq, or any other [supported LLM provider](../configuration/llm-providers.md).

### Create `servers_config.json`

```bash
cat > servers_config.json << 'EOF'
{
    "AgentConfig": {
        "tool_call_timeout": 30,
        "max_steps": 15,
        "request_limit": 1000,
        "total_tokens_limit": 100000
    },
    "LLM": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.5,
        "max_tokens": 5000,
        "top_p": 0.7
    },
    "mcpServers": {}
}
EOF
```

## Step 2: Start MCPOmni Connect

```bash
mcpomni_connect
```

You should see the MCPOmni Connect CLI start up:

```
🚀 MCPOmni Connect - Universal Gateway to MCP Servers
Connected to 0 MCP servers
Mode: CHAT (type /mode:auto for autonomous mode)

> 
```

## Step 3: Test Basic Functionality

Try these commands to verify everything is working:

### Check Available Commands
```bash
/help
```

### Test LLM Connection
```bash
Hello! Can you tell me about yourself?
```

The AI should respond, confirming your LLM configuration is working.

## Step 4: Add Your First MCP Server

Let's add a simple MCP server to demonstrate connectivity:

### Option A: File System Server (Local)

Edit your `servers_config.json` to add a file system server:

```json
{
    "AgentConfig": {
        "tool_call_timeout": 30,
        "max_steps": 15,
        "request_limit": 1000,
        "total_tokens_limit": 100000
    },
    "LLM": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.5,
        "max_tokens": 5000,
        "top_p": 0.7
    },
    "mcpServers": {
        "filesystem": {
            "transport_type": "stdio",
            "command": "uvx",
            "args": ["mcp-server-filesystem", "/tmp"]
        }
    }
}
```

### Option B: Remote HTTP Server

```json
{
    "mcpServers": {
        "remote-server": {
            "transport_type": "streamable_http",
            "url": "http://your-server.com:8080/mcp",
            "headers": {
                "Authorization": "Bearer your-token"
            },
            "timeout": 60
        }
    }
}
```

### Restart and Test

```bash
# Restart MCPOmni Connect
mcpomni_connect
```

Now check available tools:
```bash
/tools
```

You should see tools from your connected MCP server!

## Step 5: Try Different Operation Modes

### Chat Mode (Default)
```bash
Can you list the files in the current directory?
```
*The AI will ask for approval before executing tools*

### Autonomous Mode
```bash
/mode:auto
Can you analyze the files in the current directory and create a summary?
```
*The AI will execute tasks independently*

### Switch Back to Chat Mode
```bash
/mode:chat
```

## Common First Tasks

### Explore Available Capabilities
```bash
/tools      # List all available tools
/prompts    # Show available prompts
/resources  # Display available resources
```

### Memory Management
```bash
/memory     # Toggle Redis memory persistence
```

### Debug Mode
```bash
/debug      # Enable detailed logging for troubleshooting
```

## Next Steps

Now that you have MCPOmni Connect running:

1. **[Configure additional LLM providers](../configuration/llm-providers.md)** - Try different AI models
2. **[Add more MCP servers](../configuration/configuration-guide.md)** - Connect to databases, APIs, and tools
3. **[Explore advanced features](../features/agent-system.md)** - Learn about ReAct agents and orchestration
4. **[Set up authentication](../configuration/authentication.md)** - Configure OAuth and secure connections

## Troubleshooting Quick Start

!!! failure "Connection Failed"
    If you see "Failed to connect to server":
    
    1. Check your `servers_config.json` syntax
    2. Verify the MCP server is actually running
    3. See the [troubleshooting guide](../configuration/troubleshooting.md)

!!! failure "API Key Error"
    If you see "Invalid API key":
    
    1. Verify your `.env` file contains the correct key
    2. Check you're using the right provider in `servers_config.json`
    3. Ensure the API key has proper permissions

!!! failure "Command Not Found"
    If `mcpomni_connect` command isn't found:
    
    1. Try `python -m mcpomni_connect`
    2. Check your PATH includes the installation directory
    3. Reinstall with `pip install --user mcpomni-connect`

!!! tip "Getting Help"
    - Join our [GitHub Discussions](https://github.com/Abiorh001/mcp_omni_connect/discussions)
    - Check [existing issues](https://github.com/Abiorh001/mcp_omni_connect/issues)
    - Read the [full configuration guide](../configuration/configuration-guide.md)

---

**Congratulations!** 🎉 You now have MCPOmni Connect running. Ready to explore more advanced features?

**Next**: [Configuration Guide →](../configuration/configuration-guide.md) 