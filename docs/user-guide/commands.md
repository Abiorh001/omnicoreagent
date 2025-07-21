# Commands Reference

MCPOmni Connect provides a comprehensive set of commands to control its behavior and interact with connected MCP servers.

## Command Types

MCPOmni Connect accepts two types of input:

### System Commands (start with `/`)
Control MCPOmni Connect's behavior and settings

### Natural Language Queries
Direct questions or requests processed by the AI

## System Commands

### Information Commands

#### `/tools`
List all available tools across connected MCP servers.

```bash
/tools
```

**Output Example:**
```
Available tools across 3 servers:

📁 filesystem server:
  - read_file: Read contents of a file
  - write_file: Write content to a file
  - list_directory: List directory contents

🗃️  database server:
  - query_database: Execute SQL queries
  - get_schema: Get database schema information

📧 notifications server:
  - send_email: Send email notifications
  - create_alert: Create system alerts
```

#### `/prompts`
Display all available prompts from connected servers.

```bash
/prompts
```

**Output Example:**
```
Available prompts:

🌤️  weather server:
  - weather: Get weather information for a location
    Args: location (required)

📊 analytics server:
  - generate_report: Create analytics report
    Args: dataset, metrics, date_range
```

#### `/resources`
List all available resources across servers.

```bash
/resources
```

#### `/api_stats`
Show current API usage statistics and limits.

```bash
/api_stats
```

**Output Example:**
```
📊 API Usage Statistics:
- Total Tokens Used: 15,247 / 100,000
- Total Requests: 45 / 1,000
- Session Duration: 23 minutes
- Average Tokens per Request: 339
```

#### `/help`
Display help information and available commands.

```bash
/help
```

#### `/status`
Show current system status and configuration.

```bash
/status
```

**Output Example:**
```
🚀 MCPOmni Connect Status:
- Mode: AUTONOMOUS
- Connected Servers: 3
- Memory: ENABLED (Redis)
- Debug: OFF
- Uptime: 1h 23m
```

### Mode Management

#### `/mode:chat`
Switch to interactive chat mode (requires approval for actions).

```bash
/mode:chat
```

**Response:**
```
Now operating in CHAT mode. I will ask for approval before executing tasks.
```

#### `/mode:auto`
Switch to autonomous mode (independent execution).

```bash
/mode:auto
```

**Response:**
```
Now operating in AUTONOMOUS mode. I will execute tasks independently.
```

#### `/mode:orchestrator`
Switch to orchestrator mode (complex multi-step coordination).

```bash
/mode:orchestrator
```

**Response:**
```
Now operating in ORCHESTRATOR mode. I will coordinate complex multi-step tasks.
```

### Server Management

#### `/refresh`
Refresh server capabilities and reconnect if needed.

```bash
/refresh
```

**Use Cases:**
- Server capabilities have changed
- Connection issues
- After server restart

#### `/add_servers:<config_file>`
Add new servers from a configuration file.

```bash
/add_servers:new_servers.json
```

**Example `new_servers.json`:**
```json
{
    "new-database": {
        "transport_type": "streamable_http",
        "url": "http://localhost:5432/mcp",
        "headers": {
            "Authorization": "Bearer db-token"
        }
    },
    "file-processor": {
        "transport_type": "stdio",
        "command": "uvx",
        "args": ["mcp-file-processor"]
    }
}
```

#### `/remove_server:<server_name>`
Remove a server by name.

```bash
/remove_server:old-database
```

**Response:**
```
✅ Server 'old-database' removed successfully.
Connected servers: 2 (filesystem, notifications)
```

#### `/connections`
Show detailed information about current server connections.

```bash
/connections
```

### Memory and History

#### `/memory`
Toggle Redis memory persistence on/off.

```bash
/memory
```

**Responses:**
```bash
# When enabling
Memory persistence is now ENABLED using Redis
Conversations will be saved and restored across sessions.

# When disabling
Memory persistence is now DISABLED
Conversations will not be saved to Redis.
```

#### `/save:<filename>`
Save current conversation to a file.

```bash
/save:project_discussion.json
```

**Response:**
```
✅ Conversation saved to project_discussion.json
```

#### `/load:<filename>`
Load a previous conversation from file.

```bash
/load:project_discussion.json
```

**Response:**
```
✅ Conversation loaded from project_discussion.json
Loaded 23 messages from previous session.
```

#### `/clear`
Clear current conversation history.

```bash
/clear
```

### Debugging and Diagnostics

#### `/debug`
Toggle debug mode for detailed logging.

```bash
/debug
```

**Responses:**
```bash
# When enabling
🐛 Debug mode ENABLED - Detailed logging active
You'll see verbose information about tool calls and server communication.

# When disabling
🐛 Debug mode DISABLED - Normal logging restored
```

#### `/history`
Show recent command history (in autonomous/orchestrator modes).

```bash
/history
```

## Prompt Execution Commands

### Basic Prompt Execution

#### `/prompt:<prompt_name>/<args>`
Execute a prompt with simple arguments.

```bash
/prompt:weather/location=tokyo
/prompt:file_search/pattern=*.py/directory=src
```

### Advanced Prompt Execution

#### JSON Format Arguments
For complex nested arguments:

```bash
/prompt:analytics_report/{
    "dataset": "sales_2024",
    "metrics": ["revenue", "growth", "conversion"],
    "filters": {
        "region": "north_america",
        "period": "Q1",
        "product_category": "software"
    },
    "output_format": "pdf"
}
```

#### Multiple Arguments
```bash
/prompt:database_query/table=users/columns=name,email,created_at/limit=100
```

### Prompt Examples by Type

=== "Simple Parameters"
    ```bash
    /prompt:weather/location=london
    /prompt:translate/text=hello/target_lang=spanish
    /prompt:file_info/path=/etc/hosts
    ```

=== "Multiple Parameters"
    ```bash
    /prompt:search/query=python/type=files/directory=src
    /prompt:backup/source=/data/files/destination=/backup/target
    /prompt:deploy/env=staging/version=1.2.3/notify=true
    ```

=== "Complex JSON"
    ```bash
    /prompt:complex_analysis/{
        "input": {
            "data_source": "database",
            "query": "SELECT * FROM orders WHERE date > '2024-01-01'",
            "format": "json"
        },
        "processing": {
            "aggregate_by": ["month", "product"],
            "metrics": ["sum", "average", "count"],
            "filters": {
                "status": "completed",
                "amount": {"min": 100, "max": 10000}
            }
        },
        "output": {
            "format": "chart",
            "type": "bar",
            "save_to": "reports/monthly_sales.png"
        }
    }
    ```

## Resource Access Commands

#### `/resource:<uri>`
Access and analyze a specific resource.

```bash
/resource:file:///path/to/document.pdf
/resource:http://example.com/api/data
/resource:database://connection/table_name
```

**Examples:**
```bash
# File resources
/resource:file:///home/user/report.pdf
/resource:file://./config.json

# HTTP resources
/resource:http://api.github.com/repos/owner/repo
/resource:https://example.com/data.csv

# Database resources
/resource:database://localhost:5432/mydb/users
```

## Command Combinations and Workflows

### Typical Workflow Commands

```bash
# 1. Check available capabilities
/tools
/prompts
/resources

# 2. Switch to appropriate mode
/mode:auto

# 3. Execute tasks
Process all log files and create a summary report

# 4. Check progress and usage
/api_stats
/debug

# 5. Save work
/save:log_analysis_session.json
```

### Debugging Workflow

```bash
# 1. Enable debug mode
/debug

# 2. Check connections
/connections
/status

# 3. Refresh if needed
/refresh

# 4. Test simple operation
/tools

# 5. Try basic prompt
/prompt:simple_test/input=hello
```

### Server Management Workflow

```bash
# 1. Check current servers
/status

# 2. Add new servers
/add_servers:additional_servers.json

# 3. Verify connections
/connections
/refresh

# 4. Test new capabilities
/tools
/prompts

# 5. Remove old servers if needed
/remove_server:old_server_name
```

## Command Parameters and Options

### Global Parameters

Most commands support these modifiers:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--verbose` | Detailed output | `/tools --verbose` |
| `--json` | JSON format output | `/status --json` |
| `--help` | Command-specific help | `/prompt --help` |

### Mode-Specific Behavior

Commands behave differently based on current mode:

| Command | Chat Mode | Auto Mode | Orchestrator Mode |
|---------|-----------|-----------|-------------------|
| `/tools` | Shows tools + asks what to use | Shows tools | Shows tools + suggests workflows |
| Natural queries | Asks approval for each step | Executes independently | Plans and coordinates |
| `/debug` | Shows user-friendly info | Shows execution details | Shows coordination details |

## Error Handling

### Common Command Errors

!!! failure "Command Not Found"
    **Error**: `/unknown_command`

    **Response**: `Unknown command. Type /help for available commands.`

!!! failure "Invalid Arguments"
    **Error**: `/prompt:weather/invalid=args`

    **Response**: `Invalid arguments for prompt 'weather'. Expected: location`

!!! failure "Server Not Connected"
    **Error**: `/prompt:server_prompt/args=value`

    **Response**: `Server not found. Use /connections to see available servers.`

### Recovery Commands

```bash
# Reset to known good state
/mode:chat
/refresh
/clear

# Check system health
/status
/connections
/debug
```

## Advanced Command Usage

### Chaining Commands

```bash
# Multiple commands in sequence
/mode:auto && /debug && /tools
```

### Conditional Execution

```bash
# Execute based on conditions
/status | grep "CONNECTED" && /tools
```

### Scripting with Commands

```bash
# Save to script file
echo "/mode:auto" > automation.txt
echo "Process all CSV files in ./data/" >> automation.txt
echo "/save:csv_processing_results.json" >> automation.txt

# Execute script (future feature)
/script:automation.txt
```

## Tips and Best Practices

### Efficient Command Usage

!!! tip "Command Efficiency"
    1. **Use shortcuts**: `/t` instead of `/tools` (if available)
    2. **Group related commands**: Check status before major operations
    3. **Save frequently**: Use `/save:` for important sessions
    4. **Monitor usage**: Regular `/api_stats` checks
    5. **Debug when needed**: Enable `/debug` for troubleshooting

### Common Patterns

```bash
# Daily workflow start
/status && /refresh && /tools

# Before major operation
/mode:chat && /debug

# After complex task
/api_stats && /save:session_$(date +%Y%m%d).json

# Troubleshooting
/debug && /connections && /refresh
```

---

**Next**: [Memory Management →](memory-management.md)
