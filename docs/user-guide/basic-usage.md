# Basic Usage

This guide covers the everyday usage patterns and commands for MCPOmni Connect.

## Starting MCPOmni Connect

```bash
# Start with default configuration
mcpomni_connect

# Start with custom config file
mcpomni_connect --config custom.servers_config.json

# Start with debug mode enabled
mcpomni_connect --debug
```

## Understanding the Interface

When you start MCPOmni Connect, you'll see:

```
🚀 MCPOmni Connect - Universal Gateway to MCP Servers
Connected to 3 MCP servers: filesystem, database, notifications
Mode: CHAT (type /mode:auto for autonomous mode)

>
```

### Interface Elements

- **Connection Status**: Shows how many MCP servers are connected
- **Current Mode**: CHAT (interactive) or AUTO (autonomous)
- **Prompt**: `>` indicates MCPOmni Connect is ready for input

## Command Types

MCPOmni Connect accepts two types of input:

### 1. System Commands (start with `/`)

System commands control MCPOmni Connect's behavior:

```bash
/tools              # List available tools
/help              # Show help information
/mode:auto         # Switch to autonomous mode
/debug             # Toggle debug mode
```

### 2. Natural Language Queries

Direct questions or requests to the AI:

```bash
List the files in the current directory
What tools are available for database operations?
Can you help me analyze this log file?
```

## Essential Commands

### Information Commands

```bash
# Show all available tools across servers
/tools

# List available prompts
/prompts

# Display available resources
/resources

# Show current API usage statistics
/api_stats

# Get help information
/help
```

### Mode Management

```bash
# Switch to autonomous mode (AI acts independently)
/mode:auto

# Switch to interactive chat mode (requires approval)
/mode:chat

# Check current mode
/status
```

### Server Management

```bash
# Refresh server capabilities
/refresh

# Add new servers from config file
/add_servers:path/to/new_config.json

# Remove a server
/remove_server:server_name
```

### Memory and History

```bash
# Toggle Redis memory persistence
/memory

# Save current conversation to file
/save:conversation.json

# Load previous conversation
/load:conversation.json
```

### Debugging

```bash
# Toggle debug mode for detailed logging
/debug

# Show detailed connection information
/connections
```

## Working with Tools

### Discovering Tools

```bash
# List all available tools
/tools
```

Example output:
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

### Using Tools in Chat Mode

In chat mode, the AI will ask for permission before executing tools:

```bash
> Can you read the contents of config.json?

I'll help you read the contents of config.json. Let me use the file reading tool.

🔧 Tool: read_file
📁 File: config.json
❓ Execute this tool? (y/n): y

[Tool executes and shows results]
```

### Using Tools in Autonomous Mode

In autonomous mode, tools execute automatically:

```bash
> /mode:auto
Now operating in AUTONOMOUS mode.

> Analyze all log files and create a summary report

🤖 Executing autonomous task...
🔧 Using tool: list_directory → found 5 log files
🔧 Using tool: read_file → analyzing error.log
🔧 Using tool: read_file → analyzing access.log
...
📊 Summary report created successfully
```

## Working with Prompts

### Discovering Prompts

```bash
# List all available prompts
/prompts
```

### Executing Prompts

Prompts are pre-defined templates with specific parameters:

```bash
# Basic prompt execution
/prompt:weather/location=tokyo

# Multiple parameters
/prompt:travel-planner/from=london/to=paris/date=2024-03-25

# JSON format for complex arguments
/prompt:analyze-data/{
    "dataset": "sales_2024",
    "metrics": ["revenue", "growth"],
    "filters": {
        "region": "europe",
        "period": "q1"
    }
}
```

## Working with Resources

### Discovering Resources

```bash
# List all available resources
/resources
```

### Accessing Resources

```bash
# Access a specific resource
/resource:file:///path/to/document.pdf
/resource:http://example.com/api/data
/resource:database://connection/table
```

## Common Usage Patterns

### File Operations

```bash
# Read and analyze files
Can you read config.json and explain the settings?

# Batch file operations
Please read all .log files and find any error patterns

# File creation
Create a new README.md file with project documentation
```

### Data Analysis

```bash
# Database queries
Show me the top 10 customers by revenue this month

# Log analysis
Analyze the error logs and categorize the issues

# Report generation
Create a summary report of yesterday's user activity
```

### System Management

```bash
# Server monitoring
Check the status of all connected services

# Configuration management
Compare the current config with the backup version

# Deployment tasks
Deploy the latest changes to the staging environment
```

## Conversation Flow

### Interactive Session Example

```bash
> /tools
[Shows available tools]

> Can you help me find all Python files in this project?

I'll help you find Python files. Let me list the directory contents
and look for .py files.

🔧 Tool: list_directory
📁 Path: .
❓ Execute this tool? (y/n): y

Found the following Python files:
- src/main.py
- tests/test_main.py
- scripts/deploy.py

Would you like me to analyze any of these files?

> Yes, please analyze the main.py file

🔧 Tool: read_file
📁 File: src/main.py
❓ Execute this tool? (y/n): y

[File analysis results]
```

### Autonomous Session Example

```bash
> /mode:auto

> Create a backup of all configuration files

🤖 Planning autonomous task: Create backup of configuration files

Step 1: 🔧 list_directory → scanning for config files
Step 2: 🔧 read_file → reading config.json
Step 3: 🔧 read_file → reading settings.yml
Step 4: 🔧 write_file → creating backup/config_backup_2024-01-15.tar.gz

✅ Task completed: Created backup containing 5 configuration files
```

## Memory Management

### Using Redis Memory

```bash
# Enable persistent memory
/memory
Memory persistence is now ENABLED using Redis

# Your conversations will be saved and restored
> Hello, I'm working on a Python project
[AI responds and remembers this context]

# Later session
> What were we working on last time?
[AI recalls: "You were working on a Python project..."]
```

### File-Based History

```bash
# Save current conversation
/save:project_discussion.json
Conversation saved to project_discussion.json

# Load previous conversation
/load:project_discussion.json
Conversation loaded from project_discussion.json
```

## Best Practices

### Effective Communication

!!! tip "Clear Instructions"
    - Be specific about what you want
    - Mention relevant file paths or parameters
    - Ask follow-up questions for clarification

```bash
# ✅ Good
Read the config.json file and explain the database settings

# ❌ Vague
Tell me about the config
```

### Mode Selection

!!! tip "Choose the Right Mode"
    - **Chat Mode**: When you want control and oversight
    - **Autonomous Mode**: For well-defined tasks you trust the AI to complete

### Error Handling

!!! tip "When Things Go Wrong"
    1. Enable debug mode: `/debug`
    2. Check server status: `/connections`
    3. Verify configuration: `/refresh`
    4. Restart with clean state if needed

## Troubleshooting Common Issues

### Tool Not Found

```bash
> Use the database tool to query users

❌ Error: No database tools found

Solutions:
1. Check if database server is connected: /tools
2. Verify server config: /connections
3. Add the server: /add_servers:db_config.json
```

### Permission Denied

```bash
> Read the sensitive file

❌ Error: Permission denied

Solutions:
1. Check file permissions
2. Run with appropriate user privileges
3. Verify server has access to the file path
```

### Connection Lost

```bash
❌ Error: Connection to server 'database' lost

Solutions:
1. Check if the server is still running
2. Refresh connections: /refresh
3. Restart MCPOmni Connect
4. Verify network connectivity
```

---

**Next**: [Operation Modes →](operation-modes.md)
