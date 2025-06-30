# Transport Types

MCPOmni Connect supports multiple transport protocols to connect with MCP servers. Choose the right transport type based on your server's capabilities and requirements.

## Overview

| Transport Type | Use Case | Authentication | Performance |
|----------------|----------|----------------|-------------|
| `stdio` | Local processes | None | High |
| `sse` | HTTP with Server-Sent Events | Bearer/Headers | Medium |
| `streamable_http` | HTTP with optional OAuth | OAuth/Bearer/Headers | Medium |

## stdio Transport

**Best for**: Local MCP servers running as separate processes

### Configuration

```json
{
    "server-name": {
        "transport_type": "stdio",
        "command": "uvx",
        "args": ["mcp-server-package", "arg1", "arg2"]
    }
}
```

### Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `command` | Yes | Executable command | `"uvx"`, `"python"`, `"node"` |
| `args` | Yes | Command arguments | `["mcp-server-git", "/path/to/repo"]` |

### Examples

#### Python MCP Server
```json
{
    "python-server": {
        "transport_type": "stdio",
        "command": "python",
        "args": ["my_mcp_server.py", "--config", "config.json"]
    }
}
```

#### Node.js MCP Server
```json
{
    "node-server": {
        "transport_type": "stdio",
        "command": "node",
        "args": ["server.js", "--port", "3000"]
    }
}
```

#### UV Package
```json
{
    "filesystem": {
        "transport_type": "stdio",
        "command": "uvx",
        "args": ["mcp-server-filesystem", "/tmp"]
    }
}
```

### Characteristics

✅ **Advantages**:
- No network overhead
- Direct process communication
- No authentication needed
- Highest performance
- Simple setup

❌ **Limitations**:
- Local processes only
- No remote server support
- Process lifecycle tied to MCPOmni Connect

## sse Transport

**Best for**: HTTP-based MCP servers using Server-Sent Events for real-time communication

### Configuration

```json
{
    "server-name": {
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

### Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `url` | Yes | SSE endpoint URL | - |
| `headers` | No | HTTP headers | `{}` |
| `timeout` | No | Connection timeout (seconds) | `60` |
| `sse_read_timeout` | No | SSE read timeout (seconds) | `120` |

### Examples

#### Basic SSE Server
```json
{
    "sse-server": {
        "transport_type": "sse",
        "url": "http://localhost:4010/sse"
    }
}
```

#### SSE with Authentication
```json
{
    "secure-sse": {
        "transport_type": "sse",
        "url": "https://api.example.com/mcp/sse",
        "headers": {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "X-API-Version": "v1"
        },
        "timeout": 30,
        "sse_read_timeout": 180
    }
}
```

#### SSE with Custom Headers
```json
{
    "custom-sse": {
        "transport_type": "sse",
        "url": "http://internal.company.com/sse",
        "headers": {
            "X-Service-Key": "service-123",
            "X-Client-ID": "mcpomni-connect",
            "Content-Type": "application/json"
        }
    }
}
```

### Characteristics

✅ **Advantages**:
- Real-time bidirectional communication
- HTTP-based (firewall friendly)
- Supports authentication headers
- Good for streaming data
- Network resilient

❌ **Limitations**:
- Requires SSE-compatible server
- Network latency
- More complex than stdio

## streamable_http Transport

**Best for**: HTTP-based MCP servers with flexible authentication options

### Configuration Options

#### Without OAuth (Bearer Token)
```json
{
    "server-name": {
        "transport_type": "streamable_http",
        "url": "http://localhost:8080/mcp",
        "headers": {
            "Authorization": "Bearer your-token"
        },
        "timeout": 60
    }
}
```

#### With OAuth
```json
{
    "server-name": {
        "transport_type": "streamable_http",
        "auth": {
            "method": "oauth"
        },
        "url": "http://localhost:8080/mcp"
    }
}
```

### Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `url` | Yes | HTTP endpoint URL | - |
| `auth` | No | Authentication config | - |
| `headers` | No | HTTP headers | `{}` |
| `timeout` | No | Request timeout (seconds) | `60` |

### OAuth Configuration

When using OAuth, MCPOmni Connect automatically starts a callback server:

!!! info "OAuth Callback Server"
    - **Automatically starts** on `http://localhost:3000`
    - **Cannot be changed** (hardcoded for security)
    - **Only starts** when `"auth": {"method": "oauth"}` is configured
    - **Stops** when MCPOmni Connect shuts down

### Examples

#### Basic HTTP Server
```json
{
    "http-server": {
        "transport_type": "streamable_http",
        "url": "http://localhost:8080/mcp"
    }
}
```

#### HTTP with Bearer Token
```json
{
    "api-server": {
        "transport_type": "streamable_http",
        "url": "https://api.example.com/mcp",
        "headers": {
            "Authorization": "Bearer sk-1234567890abcdef",
            "User-Agent": "MCPOmni-Connect/1.0"
        },
        "timeout": 120
    }
}
```

#### HTTP with OAuth
```json
{
    "oauth-server": {
        "transport_type": "streamable_http",
        "auth": {
            "method": "oauth"
        },
        "url": "https://secure-api.example.com/mcp",
        "timeout": 90
    }
}
```

#### HTTP with Custom Authentication
```json
{
    "custom-auth": {
        "transport_type": "streamable_http",
        "url": "http://internal.api/mcp",
        "headers": {
            "X-API-Key": "your-api-key",
            "X-Client-Certificate": "cert-fingerprint",
            "Authorization": "Custom-Scheme token-data"
        }
    }
}
```

### Characteristics

✅ **Advantages**:
- Most flexible authentication
- HTTP-based (standard protocol)
- Supports OAuth and custom auth
- Good for enterprise APIs
- RESTful communication

❌ **Limitations**:
- Network latency
- Requires HTTP-compatible server
- More configuration complexity

## Choosing the Right Transport

### Decision Matrix

```mermaid
flowchart TD
    A[Choose Transport Type] --> B{Local or Remote?}
    B -->|Local| C[Use stdio]
    B -->|Remote| D{Authentication Required?}
    D -->|No| E[Use streamable_http]
    D -->|Yes| F{OAuth or Token?}
    F -->|OAuth| G[Use streamable_http with auth]
    F -->|Token/Headers| H{Real-time Streaming?}
    H -->|Yes| I[Use sse]
    H -->|No| J[Use streamable_http with headers]
```

### Recommendations

| Scenario | Recommended Transport | Reason |
|----------|----------------------|---------|
| Local development | `stdio` | Fastest, simplest setup |
| Enterprise API | `streamable_http` + OAuth | Secure, standardized |
| Real-time notifications | `sse` | Built for streaming |
| Simple remote API | `streamable_http` + Bearer | Balance of features and simplicity |
| Microservices | `streamable_http` | HTTP-native, scalable |

## Common Issues and Solutions

### stdio Issues

!!! failure "Command Not Found"
    **Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'uvx'`
    
    **Solution**: Install the required command or use full path:
    ```json
    {
        "command": "/usr/local/bin/uvx"
        // or
        "command": "python3"
    }
    ```

### SSE Issues

!!! failure "SSE Connection Failed"
    **Error**: `Failed to connect to SSE endpoint`
    
    **Solutions**:
    1. Verify the URL is correct
    2. Check if server supports SSE
    3. Ensure proper headers are set
    4. Increase timeout values

### HTTP Issues

!!! failure "OAuth Server Already Running"
    **Error**: `Address already in use: localhost:3000`
    
    **Solutions**:
    1. Stop other processes using port 3000
    2. Only one OAuth server runs at a time
    3. Remove OAuth config if not needed

## Performance Considerations

### Latency Comparison

| Transport | Local Latency | Remote Latency | Throughput |
|-----------|---------------|----------------|------------|
| `stdio` | ~1ms | N/A | Very High |
| `sse` | ~5-10ms | ~50-200ms | High |
| `streamable_http` | ~5-10ms | ~50-200ms | Medium-High |

### Optimization Tips

1. **Use stdio for local servers** when possible
2. **Tune timeout values** based on your network
3. **Minimize headers** to reduce overhead
4. **Use connection pooling** for multiple HTTP calls
5. **Consider geographic proximity** for remote servers

---

**Next**: [Authentication →](authentication.md) 