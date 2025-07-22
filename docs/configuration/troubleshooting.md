# Troubleshooting

This guide covers common issues and their solutions when using MCPOmni Connect.

## Configuration Issues

### "Failed to connect to server: Session terminated"

This is the most common connection issue with several possible causes:

!!! failure "Session Terminated Error"
    **Error**: `Failed to connect to server 'server-name': Session terminated`

    **Possible Causes & Solutions**:

#### 1. Wrong Transport Type

```bash
Problem: Your server expects 'stdio' but you configured 'streamable_http'
```

**Solution**: Check your server's documentation for the correct transport type

```json title="✅ Correct stdio configuration"
{
    "filesystem": {
        "transport_type": "stdio",
        "command": "uvx",
        "args": ["mcp-server-filesystem", "/tmp"]
    }
}
```

#### 2. OAuth Configuration Mismatch

```bash
Problem: Your server doesn't support OAuth but you have "auth": {"method": "oauth"}
```

**Solution**: Remove the `auth` section and use headers instead:

```json title="✅ Use Bearer token instead of OAuth"
{
    "api-server": {
        "transport_type": "streamable_http",
        "url": "http://localhost:8080/mcp",
        "headers": {
            "Authorization": "Bearer your-token"
        }
    }
}
```

#### 3. Server Not Running

```bash
Problem: The MCP server at the specified URL is not running
```

**Solution**: Start your MCP server first, then connect with MCPOmni Connect

```bash
# Example: Start a local MCP server
uvx mcp-server-filesystem /tmp &

# Then start MCPOmni Connect
mcpomni_connect
```

#### 4. Wrong URL or Port

```bash
Problem: URL in config doesn't match where your server is running
```

**Solution**: Verify the server's actual address and port

```bash
# Check if server is listening
curl http://localhost:8080/health

# Or use netstat to see listening ports
netstat -tlnp | grep 8080
```

### "Started callback server on http://localhost:3000" - Is This Normal?

!!! info "OAuth Callback Server"
    **Yes, this is completely normal** when:
    - You have `"auth": {"method": "oauth"}` in any server configuration
    - The OAuth server handles authentication tokens automatically
    - You cannot and should not try to change this address

**If you don't want the OAuth server:**
- Remove `"auth": {"method": "oauth"}` from all server configurations
- Use alternative authentication methods like Bearer tokens

```json title="❌ Causes OAuth server to start"
{
    "server": {
        "auth": {"method": "oauth"},
        "url": "http://example.com/mcp"
    }
}
```

```json title="✅ No OAuth server needed"
{
    "server": {
        "url": "http://example.com/mcp",
        "headers": {
            "Authorization": "Bearer token"
        }
    }
}
```

## Authentication Issues

### Invalid API Key Errors

!!! failure "API Key Problems"
    **Error**: `Invalid API key` or `Authentication failed`

#### OpenAI API Key Issues

```bash
# Check your .env file
cat .env | grep LLM_API_KEY

# Verify key format (should start with sk-)
LLM_API_KEY=sk-your-key-here

# Test key directly
curl -H "Authorization: Bearer $LLM_API_KEY" \
     https://api.openai.com/v1/models
```

#### Anthropic API Key Issues

```bash
# Anthropic keys start with sk-ant-
LLM_API_KEY=sk-ant-your-key-here

# Test key
curl -H "x-api-key: $LLM_API_KEY" \
     https://api.anthropic.com/v1/messages
```

#### Environment Variable Not Loaded

```bash
# Check if environment variable is loaded
echo $LLM_API_KEY

# Restart MCPOmni Connect to reload .env
mcpomni_connect
```

### OAuth Authentication Failures

!!! failure "OAuth Issues"
    **Error**: `OAuth authentication failed`

**Solutions**:

1. **Port 3000 Already in Use**
   ```bash
   # Find what's using port 3000
   lsof -i :3000

   # Stop the conflicting service
   sudo kill -9 <pid>
   ```

2. **Browser Not Opening**
   ```bash
   # Manual OAuth flow
   # Copy the authorization URL from the terminal
   # Open it manually in your browser
   ```

3. **Firewall Blocking Localhost**
   ```bash
   # Allow localhost connections
   sudo ufw allow from 127.0.0.1
   ```

## Server Configuration Issues

### JSON Syntax Errors

!!! failure "Configuration Parsing"
    **Error**: `JSON decode error` or `Invalid configuration`

**Common JSON Mistakes**:

```json title="❌ Common JSON errors"
{
    "LLM": {
        "provider": "openai",
        "model": "gpt-4o-mini"    // ❌ Trailing comma
    },
    "mcpServers": {
        "server": {
            "url": "http://example.com"    // ❌ Missing comma
            "timeout": 60
        }
    }
}
```

```json title="✅ Correct JSON"
{
    "LLM": {
        "provider": "openai",
        "model": "gpt-4o-mini"
    },
    "mcpServers": {
        "server": {
            "url": "http://example.com",
            "timeout": 60
        }
    }
}
```

**Validation Tools**:
```bash
# Validate JSON syntax
python -m json.tool servers_config.json

# Or use jq
jq . servers_config.json
```

### Missing Required Fields

!!! failure "Required Configuration"
    **Error**: `Missing required field`

**Check Required Fields**:

```json title="Minimum required configuration"
{
    "LLM": {
        "provider": "openai",        // ✅ Required
        "model": "gpt-4o-mini"      // ✅ Required
    },
    "mcpServers": {}                // ✅ Required (can be empty)
}
```

## Runtime Issues

### Tool Execution Failures

!!! failure "Tool Errors"
    **Error**: `Tool execution failed` or `Tool timeout`

#### Timeout Issues

```json title="Increase timeout in configuration"
{
    "AgentConfig": {
        "tool_call_timeout": 60    // Increase from default 30
    }
}
```

```bash
# Enable debug mode for detailed logs
/debug

# Check tool availability
/tools

# Test simple command first
/tools
```

#### Permission Denied

```bash
# Check file permissions
ls -la /path/to/file

# Ensure MCPOmni Connect has necessary permissions
chmod +r /path/to/file
```

### Memory Issues

!!! failure "Redis Connection"
    **Error**: `Could not connect to Redis`

**Solutions**:

1. **Redis Not Running**
   ```bash
   # Start Redis
   sudo systemctl start redis-server

   # Or with Docker
   docker run -d --name redis -p 6379:6379 redis:alpine
   ```

2. **Wrong Redis Configuration**
   ```bash title=".env"
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   # Add password if needed
   REDIS_PASSWORD=your-password
   ```

3. **Disable Redis Memory**
   ```bash
   # Turn off memory persistence
   /memory
   ```

### Rate Limiting

!!! failure "API Limits"
    **Error**: `Rate limit exceeded` or `Too many requests`

**Solutions**:

1. **Reduce Request Frequency**
   ```json
   {
       "AgentConfig": {
           "request_limit": 100,        // Lower limit
           "total_tokens_limit": 10000  // Lower token limit
       }
   }
   ```

2. **Switch to Different Provider**
   ```json
   {
       "LLM": {
           "provider": "groq",          // Often has higher limits
           "model": "llama-3.1-8b-instant"
       }
   }
   ```

3. **Check Current Usage**
   ```bash
   /api_stats
   ```

## Network Issues

### Connection Timeouts

!!! failure "Network Timeouts"
    **Error**: `Connection timeout` or `Request timeout`

**Solutions**:

1. **Increase Timeout Values**
   ```json
   {
       "server": {
           "transport_type": "streamable_http",
           "url": "http://slow-server.com/mcp",
           "timeout": 120,              // Increase timeout
           "sse_read_timeout": 300      // For SSE connections
       }
   }
   ```

2. **Check Network Connectivity**
   ```bash
   # Test basic connectivity
   ping api.openai.com

   # Test HTTP connectivity
   curl -I https://api.openai.com

   # Test specific server
   curl -I http://your-server.com:8080
   ```

### Firewall Issues

!!! failure "Connection Blocked"
    **Error**: `Connection refused` or `Network unreachable`

**Solutions**:

1. **Check Firewall Rules**
   ```bash
   # Ubuntu/Debian
   sudo ufw status

   # Allow specific port
   sudo ufw allow 8080

   # Allow outbound HTTPS
   sudo ufw allow out 443
   ```

2. **Corporate Firewall**
   ```bash
   # Test with proxy if needed
   export https_proxy=http://proxy.company.com:8080
   mcpomni_connect
   ```

## Performance Issues

### Slow Response Times

!!! warning "Performance Problems"
    **Issue**: MCPOmni Connect is responding slowly

**Diagnosis**:

1. **Enable Debug Mode**
   ```bash
   /debug
   # Check where time is being spent
   ```

2. **Check API Stats**
   ```bash
   /api_stats
   # Look for high token usage or request counts
   ```

**Solutions**:

1. **Optimize Model Settings**
   ```json
   {
       "LLM": {
           "provider": "groq",              // Faster provider
           "model": "llama-3.1-8b-instant", // Faster model
           "max_tokens": 1000,              // Shorter responses
           "temperature": 0.1               // More focused
       }
   }
   ```

2. **Reduce Context Length**
   ```json
   {
       "LLM": {
           "max_context_length": 8000       // Smaller context
       }
   }
   ```

### High Token Usage

!!! warning "Token Consumption"
    **Issue**: Running out of tokens quickly

**Solutions**:

1. **Set Token Limits**
   ```json
   {
       "AgentConfig": {
           "total_tokens_limit": 50000,     // Lower limit
           "max_steps": 5                   // Fewer reasoning steps
       }
   }
   ```

2. **Use More Efficient Models**
   ```json
   {
       "LLM": {
           "provider": "openai",
           "model": "gpt-4o-mini"           // Most cost-effective
       }
   }
   ```

## Debugging Tools

### Built-in Debug Features

```bash
# Enable verbose logging
/debug

# Check system status
/status

# View current configuration
/connections

# Check API usage
/api_stats

# Refresh server connections
/refresh
```

### Log Analysis

```bash
# Check application logs
tail -f mcpomni_connect.log

# Filter for errors
grep ERROR mcpomni_connect.log

# Check specific server logs
grep "server-name" mcpomni_connect.log
```

### Environment Verification

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep mcpomni

# Verify environment variables
env | grep LLM_API_KEY

# Test configuration file
python -m json.tool servers_config.json
```

## Getting Help

### Before Asking for Help

1. **Enable Debug Mode**: `/debug`
2. **Check Logs**: Look for error messages
3. **Verify Configuration**: Validate JSON syntax
4. **Test Simple Cases**: Try basic operations first

### Information to Include

When reporting issues, include:

- **MCPOmni Connect version**: `mcpomni_connect --version`
- **Python version**: `python --version`
- **Operating system**: `uname -a` (Linux/Mac) or `ver` (Windows)
- **Configuration** (remove sensitive data):
  ```json
  {
      "LLM": {
          "provider": "openai",
          "model": "gpt-4o-mini"
      },
      "mcpServers": {
          "server": {
              "transport_type": "stdio",
              "command": "uvx",
              "args": ["mcp-server-filesystem"]
          }
      }
  }
  ```
- **Complete error message**
- **Steps to reproduce**

### Support Channels

- **GitHub Issues**: [Report bugs](https://github.com/Abiorh001/mcp_omni_connect/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/Abiorh001/mcp_omni_connect/discussions)
- **Email**: abiolaadedayo1993@gmail.com

---

**Next**: [User Guide →](../user-guide/basic-usage.md)
