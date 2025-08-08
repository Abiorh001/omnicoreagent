# Configuration Guide

MCPOmni Connect uses **two separate configuration files** for different purposes. Understanding this separation is crucial for proper setup.

!!! info "Configuration Files Overview"
    - **`.env`** → Environment variables (API keys, Redis settings)
    - **`servers_config.json`** → Application settings (LLM config, MCP servers, agent settings)

## Configuration Files

### 1. `.env` File - Environment Variables

Contains sensitive information like API keys and optional settings:

```bash title=".env"
# Required: Your LLM provider API key
LLM_API_KEY=your_api_key_here

# Optional: Redis configuration (for persistent memory)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password  # if password protected

# Optional: Custom settings
DEBUG=false
LOG_LEVEL=INFO

# Optional: Vector DB selection
# Default is chroma-local. Options: chroma-local | chroma-remote | chroma-cloud | qdrant-remote
OMNI_MEMORY_PROVIDER=chroma-local

# If using chroma-remote
# CHROMA_HOST=localhost
# CHROMA_PORT=8000

# If using chroma-cloud
# CHROMA_TENANT=your_tenant_id
# CHROMA_DATABASE=your_database_name  
# CHROMA_API_KEY=your_api_key

# If using qdrant-remote
# QDRANT_HOST=localhost
# QDRANT_PORT=6333
```

!!! warning "Security"
    - Never commit your `.env` file to version control
    - Keep your API keys secure and rotate them regularly
    - Use environment-specific `.env` files for different deployments

### 2. `servers_config.json` - Application Configuration

Contains application settings, LLM configuration, and MCP server connections:

```json title="servers_config.json"
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
        "max_context_length": 30000,
        "top_p": 0.7
    },
    "mcpServers": {
        "your-server-name": {
            "transport_type": "stdio",
            "command": "uvx",
            "args": ["mcp-server-package"]
        }
    }
}
```

## Agent Configuration

Configure the behavior of MCPOmni Connect's agent system:

```json title="AgentConfig section"
{
    "AgentConfig": {
        "tool_call_timeout": 30,        // Tool execution timeout (seconds)
        "max_steps": 15,                // Maximum agent steps per task
        "request_limit": 1000,          // Maximum LLM requests per session
        "total_tokens_limit": 100000    // Maximum tokens per session
    }
}
```

### Agent Configuration Options

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| `tool_call_timeout` | Seconds before tool execution times out | 30 | 5-300 |
| `max_steps` | Maximum reasoning steps per task | 15 | 1-50 |
| `request_limit` | Maximum LLM API calls per session | 1000 | 10-10000 |
| `total_tokens_limit` | Maximum tokens consumed per session | 100000 | 1000-1000000 |

## LLM Configuration

Configure your AI model provider and settings:

```json title="LLM section"
{
    "LLM": {
        "provider": "openai",           // Provider name
        "model": "gpt-4o-mini",        // Model identifier
        "temperature": 0.5,             // Creativity level (0-1)
        "max_tokens": 5000,            // Max response length
        "max_context_length": 30000,   // Context window size
        "top_p": 0.7                   // Nucleus sampling
    }
}
```

### LLM Configuration Options

| Setting | Description | Typical Range |
|---------|-------------|---------------|
| `provider` | LLM provider (openai, anthropic, etc.) | See [LLM Providers](llm-providers.md) |
| `model` | Specific model name | Provider-specific |
| `temperature` | Response creativity/randomness | 0.0 (deterministic) - 1.0 (creative) |
| `max_tokens` | Maximum response length | 100 - 8000 |
| `max_context_length` | Context window size | Model-dependent |
| `top_p` | Nucleus sampling parameter | 0.1 - 1.0 |

## MCP Server Configuration

Configure connections to MCP servers using different transport types:

### Basic Structure

```json title="mcpServers section"
{
    "mcpServers": {
        "server-name": {
            "transport_type": "stdio|sse|streamable_http",
            // Additional configuration depends on transport type
        }
    }
}
```

### Configuration by Transport Type

=== "stdio"
    ```json
    {
        "filesystem": {
            "transport_type": "stdio",
            "command": "uvx",
            "args": ["mcp-server-filesystem", "/tmp"]
        }
    }
    ```

=== "sse"
    ```json
    {
        "sse-server": {
            "transport_type": "sse",
            "url": "http://localhost:3000/sse",
            "headers": {
                "Authorization": "Bearer your-token"
            },
            "timeout": 60,
            "sse_read_timeout": 120
        }
    }
    ```

=== "streamable_http"
    ```json
    {
        "http-server": {
            "transport_type": "streamable_http",
            "url": "http://localhost:3000/mcp",
            "headers": {
                "Authorization": "Bearer your-token"
            },
            "timeout": 60
        }
    }
    ```

## Complete Configuration Examples

### Minimal Setup

```json title="Minimal servers_config.json"
{
    "LLM": {
        "provider": "openai",
        "model": "gpt-4o-mini"
    },
    "mcpServers": {}
}
```

### Production Setup

```json title="Production servers_config.json"
{
    "AgentConfig": {
        "tool_call_timeout": 60,
        "max_steps": 25,
        "request_limit": 5000,
        "total_tokens_limit": 500000
    },
    "LLM": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3,
        "max_tokens": 4000,
        "max_context_length": 100000,
        "top_p": 0.8
    },
    "mcpServers": {
        "database": {
            "transport_type": "streamable_http",
            "url": "https://db-api.company.com/mcp",
            "headers": {
                "Authorization": "Bearer prod-token-xyz"
            },
            "timeout": 120
        },
        "filesystem": {
            "transport_type": "stdio",
            "command": "uvx",
            "args": ["mcp-server-filesystem", "/data"]
        },
        "notifications": {
            "transport_type": "sse",
            "url": "https://notify.company.com/sse",
            "headers": {
                "Authorization": "Bearer notify-token-abc"
            },
            "sse_read_timeout": 300
        }
    }
}
```

### Development Setup

```json title="Development servers_config.json"
{
    "AgentConfig": {
        "tool_call_timeout": 10,
        "max_steps": 5,
        "request_limit": 100,
        "total_tokens_limit": 10000
    },
    "LLM": {
        "provider": "ollama",
        "model": "llama3.1:8b",
        "temperature": 0.7,
        "max_tokens": 2000,
        "ollama_host": "http://localhost:11434"
    },
    "mcpServers": {
        "local-tools": {
            "transport_type": "stdio",
            "command": "python",
            "args": ["local_mcp_server.py"]
        }
    }
}
```

## Environment-Specific Configuration

### Using Multiple Configuration Files

You can use different configuration files for different environments:

```bash
# Development
mcpomni_connect --config dev.servers_config.json

# Production
mcpomni_connect --config prod.servers_config.json

# Testing
mcpomni_connect --config test.servers_config.json
```

### Environment Variables in Configuration

Reference environment variables in your JSON configuration:

```json
{
    "LLM": {
        "provider": "openai",
        "model": "${MODEL_NAME:-gpt-4o-mini}",
        "temperature": "${TEMPERATURE:-0.5}"
    }
}
```

## Validation and Testing

### Validate Configuration

```bash
# Test configuration without starting full application
mcpomni_connect --validate-config

# Test specific configuration file
mcpomni_connect --config custom.json --validate-config
```

### Debug Configuration Issues

```bash
# Start with debug mode for detailed logging
mcpomni_connect --debug

# Or enable debug in your session
/debug
```

## Best Practices

!!! tip "Configuration Best Practices"
    1. **Start Simple**: Begin with minimal configuration and add complexity gradually
    2. **Use Version Control**: Track your `servers_config.json` in git (but not `.env`)
    3. **Environment Separation**: Use different configs for dev/test/prod
    4. **Regular Backups**: Keep backups of working configurations
    5. **Document Changes**: Comment complex configurations for team members

!!! warning "Common Mistakes"
    - Mixing up `.env` and `servers_config.json` purposes
    - Hardcoding sensitive data in `servers_config.json`
    - Using incorrect transport types for your servers
    - Setting unrealistic timeout values
    - Forgetting to restart after configuration changes

---

**Next Steps**:
- [Transport Types →](transport-types.md)
- [Authentication →](authentication.md)
- [LLM Providers →](llm-providers.md)
