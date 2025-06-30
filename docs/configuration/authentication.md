# Authentication

MCPOmni Connect supports multiple authentication methods to securely connect to MCP servers. Choose the appropriate method based on your server's requirements.

## Authentication Methods Overview

| Method | Use Case | Security Level | Setup Complexity |
|--------|----------|----------------|------------------|
| **OAuth 2.0** | Enterprise APIs | High | Medium |
| **Bearer Token** | API services | Medium | Low |
| **Custom Headers** | Proprietary systems | Medium | Low |
| **No Auth** | Local/trusted servers | Low | None |

## OAuth 2.0 Authentication

OAuth 2.0 provides secure, token-based authentication with automatic token refresh.

### Configuration

```json
{
    "oauth-server": {
        "transport_type": "streamable_http",
        "auth": {
            "method": "oauth"
        },
        "url": "https://api.example.com/mcp"
    }
}
```

### OAuth Flow

1. **Automatic Server Start**: MCPOmni Connect starts callback server on `http://localhost:3000`
2. **Browser Authorization**: Opens browser for user authentication
3. **Token Exchange**: Receives authorization code and exchanges for access token
4. **Automatic Refresh**: Handles token refresh automatically

### OAuth Server Behavior

!!! info "OAuth Callback Server"
    - **Address**: `http://localhost:3000` (hardcoded)
    - **Automatic**: Starts only when OAuth is configured
    - **Security**: Uses PKCE (Proof Key for Code Exchange)
    - **Cleanup**: Stops when MCPOmni Connect exits

### Example Output

```bash
> mcpomni_connect
🖥️  Started callback server on http://localhost:3000
🔐 Opening browser for OAuth authentication...
✅ OAuth authentication successful
🚀 MCPOmni Connect - Universal Gateway to MCP Servers
Connected to 1 MCP server: oauth-server
```

## Bearer Token Authentication

Simple token-based authentication using HTTP headers.

### Configuration

```json
{
    "api-server": {
        "transport_type": "streamable_http",
        "url": "https://api.example.com/mcp",
        "headers": {
            "Authorization": "Bearer your-token-here"
        }
    }
}
```

### Token Types

=== "API Key"
    ```json
    {
        "headers": {
            "Authorization": "Bearer sk-1234567890abcdef"
        }
    }
    ```

=== "JWT Token"
    ```json
    {
        "headers": {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    }
    ```

=== "Custom Token"
    ```json
    {
        "headers": {
            "Authorization": "Bearer custom-token-format"
        }
    }
    ```

### Token Management

- **Rotation**: Manually update tokens when they expire
- **Storage**: Stored securely in configuration
- **Scope**: Ensure tokens have appropriate permissions

## Custom Headers Authentication

Flexible authentication using custom HTTP headers.

### Basic Custom Headers

```json
{
    "custom-server": {
        "transport_type": "streamable_http",
        "url": "https://internal.api.com/mcp",
        "headers": {
            "X-API-Key": "your-api-key",
            "X-Client-ID": "mcpomni-connect",
            "X-Service-Version": "v1"
        }
    }
}
```

### Advanced Authentication Schemes

=== "API Key + Secret"
    ```json
    {
        "headers": {
            "X-API-Key": "public-key-123",
            "X-API-Secret": "secret-key-456",
            "X-Timestamp": "2024-01-15T10:30:00Z"
        }
    }
    ```

=== "Custom Authorization"
    ```json
    {
        "headers": {
            "Authorization": "CustomScheme key=value, signature=abc123",
            "X-Request-ID": "unique-request-id"
        }
    }
    ```

=== "Certificate-Based"
    ```json
    {
        "headers": {
            "X-Client-Certificate": "cert-fingerprint",
            "X-Certificate-Subject": "CN=client.example.com"
        }
    }
    ```

## SSE Authentication

Server-Sent Events with authentication headers.

### Configuration

```json
{
    "sse-server": {
        "transport_type": "sse",
        "url": "https://stream.api.com/sse",
        "headers": {
            "Authorization": "Bearer sse-token-123",
            "X-Stream-Type": "mcp-events"
        },
        "sse_read_timeout": 120
    }
}
```

### SSE-Specific Considerations

- **Long-lived Connections**: Ensure tokens don't expire during connection
- **Reconnection**: Handle authentication on reconnect
- **Event Filtering**: Use headers to specify event types

## No Authentication

For local or trusted servers that don't require authentication.

### Configuration

```json
{
    "local-server": {
        "transport_type": "stdio",
        "command": "uvx",
        "args": ["mcp-server-filesystem", "/tmp"]
    }
}
```

```json
{
    "public-server": {
        "transport_type": "streamable_http",
        "url": "http://localhost:8080/mcp"
    }
}
```

## Environment Variables for Secrets

Store sensitive authentication data in environment variables.

### .env File

```bash title=".env"
# API Keys
OPENAI_API_KEY=sk-1234567890abcdef
DATABASE_API_KEY=db-token-xyz789
NOTIFICATION_SECRET=notify-secret-abc

# OAuth Credentials
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-client-secret

# Custom Authentication
CUSTOM_API_KEY=custom-key-123
CUSTOM_SECRET=custom-secret-456
```

### Reference in Configuration

```json
{
    "api-server": {
        "transport_type": "streamable_http",
        "url": "https://api.example.com/mcp",
        "headers": {
            "Authorization": "Bearer ${OPENAI_API_KEY}",
            "X-Custom-Key": "${CUSTOM_API_KEY}"
        }
    }
}
```

## Security Best Practices

### Token Security

!!! warning "Token Management"
    - **Never commit tokens** to version control
    - **Use environment variables** for sensitive data
    - **Rotate tokens regularly** according to your security policy
    - **Use minimal permissions** for each token
    - **Monitor token usage** for suspicious activity

### Network Security

- **Use HTTPS** for all remote connections
- **Validate certificates** in production
- **Use VPN/private networks** when possible
- **Implement rate limiting** to prevent abuse

### Configuration Security

```json title="✅ Secure Configuration"
{
    "server": {
        "transport_type": "streamable_http",
        "url": "https://secure-api.example.com/mcp",
        "headers": {
            "Authorization": "Bearer ${API_TOKEN}"
        },
        "timeout": 30
    }
}
```

```json title="❌ Insecure Configuration"
{
    "server": {
        "transport_type": "streamable_http",
        "url": "http://api.example.com/mcp",
        "headers": {
            "Authorization": "Bearer hardcoded-token-123"
        }
    }
}
```

## Troubleshooting Authentication

### Common Issues

!!! failure "OAuth Server Error"
    **Error**: `Failed to start OAuth callback server`
    
    **Solutions**:
    - Check if port 3000 is available
    - Stop other applications using port 3000
    - Ensure firewall allows localhost connections

!!! failure "Invalid Token"
    **Error**: `401 Unauthorized`
    
    **Solutions**:
    - Verify token is correct and not expired
    - Check token has required permissions
    - Ensure token format matches server expectations

!!! failure "Missing Headers"
    **Error**: `Authentication headers missing`
    
    **Solutions**:
    - Verify all required headers are configured
    - Check header names match server requirements
    - Ensure environment variables are loaded

### Debug Authentication

```bash
# Enable debug mode for detailed auth logging
/debug

# Check current server connections
/connections

# Refresh server capabilities (re-authenticates)
/refresh
```

### Testing Authentication

```bash
# Test with curl before configuring
curl -H "Authorization: Bearer your-token" \
     -H "Content-Type: application/json" \
     https://api.example.com/mcp/health

# Test OAuth flow manually
# Visit the OAuth authorization URL in browser
```

## Authentication Examples by Provider

### GitHub API

```json
{
    "github": {
        "transport_type": "streamable_http",
        "url": "https://api.github.com/mcp",
        "headers": {
            "Authorization": "Bearer ${GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MCPOmni-Connect"
        }
    }
}
```

### AWS Services

```json
{
    "aws-service": {
        "transport_type": "streamable_http",
        "url": "https://service.us-east-1.amazonaws.com/mcp",
        "headers": {
            "Authorization": "AWS4-HMAC-SHA256 ${AWS_SIGNATURE}",
            "X-Amz-Date": "${TIMESTAMP}",
            "X-Amz-Security-Token": "${AWS_SESSION_TOKEN}"
        }
    }
}
```

### Google Cloud

```json
{
    "gcp-service": {
        "transport_type": "streamable_http",
        "url": "https://service.googleapis.com/mcp",
        "headers": {
            "Authorization": "Bearer ${GCP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
    }
}
```

---

**Next**: [Troubleshooting →](troubleshooting.md) 