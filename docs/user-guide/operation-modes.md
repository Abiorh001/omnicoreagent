# Operation Modes

MCPOmni Connect offers three distinct operation modes, each designed for different levels of automation and user involvement.

## Mode Overview

| Mode | Description | User Involvement | Best For |
|------|-------------|------------------|----------|
| **Chat** | Interactive with approval | High | Learning, careful operations |
| **Autonomous** | Independent execution | Low | Well-defined tasks |
| **Orchestrator** | Multi-agent coordination | Minimal | Complex workflows |

## Chat Mode (Default)

**Interactive mode** where the AI asks for permission before executing any tools.

### Characteristics

- ✅ **User Control**: Every tool execution requires explicit approval
- ✅ **Educational**: Shows reasoning process step-by-step
- ✅ **Safe**: No unexpected actions
- ✅ **Transparent**: Clear explanation of what each tool does

### How It Works

```bash
> Can you list the files in the current directory?

I'll help you list the files in the current directory using the filesystem tools.

🔧 Tool: list_directory
📁 Path: .
📋 Purpose: List all files and directories in the current location
❓ Execute this tool? (y/n): y

[Tool executes after user approval]

Found 5 items:
- README.md (file)
- src/ (directory)
- docs/ (directory)
- pyproject.toml (file)
- .gitignore (file)
```

### When to Use Chat Mode

- **Learning**: Understanding how MCPOmni Connect works
- **Sensitive Operations**: Working with important files or systems
- **Exploration**: Discovering what tools are available
- **Debugging**: Step-by-step problem diagnosis

### Switching to Chat Mode

```bash
/mode:chat
Now operating in CHAT mode. I will ask for approval before executing tasks.
```

## Autonomous Mode

**Independent execution** where the AI operates using ReAct (Reasoning + Acting) methodology.

### Characteristics

- 🤖 **Independent**: No approval required for tool execution
- 🧠 **Reasoning**: Shows thought process before each action
- 🔄 **Iterative**: Adapts based on results
- 📊 **Goal-Oriented**: Focuses on completing the requested task
- ⚡ **Efficient**: Faster execution without approval delays

### How It Works

```bash
> /mode:auto
Now operating in AUTONOMOUS mode. I will execute tasks independently.

> Create a backup of all configuration files

🤖 Executing autonomous task: Create backup of configuration files

💭 Thought: I need to find all configuration files, create a backup directory, and copy them safely.

🔧 Action: list_directory(path=".", pattern="*.{json,yaml,yml,conf}")
📊 Observation: Found 3 configuration files: servers_config.json, docker-compose.yaml, .env

💭 Thought: I'll create a timestamped backup directory and copy the files.

🔧 Action: create_directory(path="backup_2024-01-15_14-30")
📊 Observation: Backup directory created successfully.

🔧 Action: copy_files(source=["servers_config.json", "docker-compose.yaml"], destination="backup_2024-01-15_14-30/")
📊 Observation: 2 files copied successfully (excluding .env for security).

✅ Task Complete: Configuration backup created in backup_2024-01-15_14-30/
```

### When to Use Autonomous Mode

- **Routine Tasks**: Regular maintenance or data processing
- **Well-Defined Operations**: Clear objectives with known steps
- **Batch Processing**: Multiple similar operations
- **Time-Sensitive Tasks**: When speed is important

### Switching to Autonomous Mode

```bash
/mode:auto
Now operating in AUTONOMOUS mode. I will execute tasks independently.
```

## Orchestrator Mode

**Advanced coordination** for complex, multi-step workflows across multiple systems.

### Characteristics

- 🎯 **Strategic Planning**: Breaks complex tasks into coordinated subtasks
- 🤝 **Multi-Agent**: Coordinates multiple specialized agents
- ⚡ **Parallel Execution**: Runs independent tasks simultaneously
- 📈 **Scalable**: Handles enterprise-level workflows
- 🔄 **Adaptive**: Adjusts strategy based on real-time results

### How It Works

```bash
> /mode:orchestrator
Now operating in ORCHESTRATOR mode. I will coordinate complex multi-step tasks.

> Deploy the application, update documentation, and notify the team

🎯 Orchestrator: Planning deployment workflow

📋 Strategic Plan:
Phase 1: Pre-deployment Checks (Parallel)
├─ Agent A: Run test suite
├─ Agent B: Verify database connectivity
└─ Agent C: Check deployment target status

Phase 2: Deployment (Sequential)
├─ Agent D: Build application
├─ Agent E: Deploy to staging
└─ Agent F: Run smoke tests

Phase 3: Documentation & Notification (Parallel)
├─ Agent G: Update deployment docs
├─ Agent H: Generate release notes
└─ Agent I: Send team notifications

🚀 Executing Phase 1: Pre-deployment Checks...

🤖 Agent A: Running pytest test suite... ✅ 47/47 tests passed
🤖 Agent B: Database connection verified ✅
🤖 Agent C: Staging environment ready ✅

Phase 1 Complete (2.1 minutes)

🚀 Executing Phase 2: Deployment...
[Sequential execution continues...]

✅ Workflow Complete (8.3 minutes total):
- Application deployed successfully
- Documentation updated
- Team notified via Slack
```

### When to Use Orchestrator Mode

- **Complex Deployments**: Multi-step deployment workflows
- **Data Migration**: Moving data between systems
- **Business Processes**: Automated business workflows
- **Integration Tasks**: Coordinating multiple systems

### Switching to Orchestrator Mode

```bash
/mode:orchestrator
Now operating in ORCHESTRATOR mode. I will coordinate complex multi-step tasks.
```

## Mode Comparison

### Execution Speed

| Mode | Speed | Reason |
|------|-------|--------|
| **Chat** | Slowest | Waits for user approval |
| **Autonomous** | Fast | No approval delays |
| **Orchestrator** | Variable | Depends on task complexity |

### Safety Level

| Mode | Safety | Control |
|------|--------|---------|
| **Chat** | Highest | Full user control |
| **Autonomous** | Medium | Configurable limits |
| **Orchestrator** | Medium | Strategic oversight |

### Use Case Examples

=== "Chat Mode"
    - Learning MCPOmni Connect
    - Exploring new MCP servers
    - Debugging configuration issues
    - Working with sensitive data
    - Educational demonstrations

=== "Autonomous Mode"
    - File organization
    - Data analysis reports
    - System health checks
    - Log file analysis
    - Backup operations

=== "Orchestrator Mode"
    - Application deployments
    - Database migrations
    - Multi-system integrations
    - Business process automation
    - Complex reporting workflows

## Configuration

Control mode behavior through `AgentConfig`:

```json
{
    "AgentConfig": {
        "tool_call_timeout": 30,        // Tool execution timeout
        "max_steps": 15,                // Max steps per task (Auto/Orchestrator)
        "request_limit": 1000,          // API request limit
        "total_tokens_limit": 100000    // Token usage limit
    }
}
```

### Mode-Specific Settings

| Setting | Chat | Auto | Orchestrator |
|---------|------|------|--------------|
| `tool_call_timeout` | ✅ | ✅ | ✅ |
| `max_steps` | ❌ | ✅ | ✅ |
| `request_limit` | ✅ | ✅ | ✅ |
| `total_tokens_limit` | ✅ | ✅ | ✅ |

## Safety Features

### Built-in Safeguards

- **Timeout Protection**: Prevents infinite loops
- **Step Limits**: Controls reasoning cycles
- **Resource Limits**: Manages API usage
- **Emergency Stop**: Ctrl+C to interrupt

### Best Practices

!!! tip "Safe Mode Usage"
    1. **Start with Chat Mode** when learning
    2. **Test in Autonomous** with simple tasks first
    3. **Use Orchestrator** for well-understood complex workflows
    4. **Set Conservative Limits** in production
    5. **Monitor Resource Usage** with `/api_stats`

## Troubleshooting Modes

### Mode Not Switching

```bash
# Check current mode
/status

# Force mode switch
/mode:chat
/mode:auto
/mode:orchestrator
```

### Autonomous Mode Stuck

```bash
# Check current progress
/debug

# Stop execution
Ctrl+C

# Switch back to chat mode
/mode:chat
```

### Resource Limits Reached

```bash
# Check usage
/api_stats

# Adjust limits in servers_config.json
{
    "AgentConfig": {
        "total_tokens_limit": 200000,  // Increase limit
        "max_steps": 25               // Allow more steps
    }
}
```

## Advanced Usage

### Mode-Specific Commands

```bash
# Check current mode and status
/status

# View execution history (Autonomous/Orchestrator)
/history

# Monitor resource usage
/api_stats

# Enable detailed logging
/debug
```

### Combining Modes

You can switch between modes within a session:

```bash
# Start with exploration in chat mode
/mode:chat
What tools are available?

# Switch to autonomous for execution
/mode:auto
Process all the log files and create a summary

# Back to chat for review
/mode:chat
Can you explain what you found in the logs?
```

---

**Next**: [Commands →](commands.md)
