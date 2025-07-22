# Memory Management

MCPOmni Connect provides flexible memory management through Redis persistence and file-based conversation history, allowing you to maintain context across sessions and save important conversations.

## Memory Types

| Type | Storage | Persistence | Use Case |
|------|---------|-------------|----------|
| **Session Memory** | RAM | Current session only | Active conversation |
| **Redis Memory** | Redis Database | Across sessions | Long-term context |
| **File History** | JSON Files | Manual save/load | Conversation backups |

## Redis-Powered Persistence

### Overview

Redis memory provides automatic conversation persistence across MCPOmni Connect sessions, maintaining context and conversation history even after restarts.

### Setup Redis

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

=== "Docker"
    ```bash
    docker run -d --name redis -p 6379:6379 redis:alpine
    ```

=== "Windows"
    Download from [Redis Windows releases](https://github.com/microsoftarchive/redis/releases) or use WSL.

### Configuration

Configure Redis connection in your `.env` file:

```bash title=".env"
# Redis Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password  # if password protected
```

### Using Redis Memory

#### Enable/Disable Memory Persistence

```bash
# Toggle memory persistence
/memory
```

**When Enabling:**
```
✅ Memory persistence is now ENABLED using Redis
Conversations will be saved and restored across sessions.
Connected to Redis at localhost:6379 (DB: 0)
```

**When Disabling:**
```
❌ Memory persistence is now DISABLED
Conversations will not be saved to Redis.
Session memory will be cleared on restart.
```

#### Check Memory Status

```bash
/status
```

**Output:**
```
🚀 MCPOmni Connect Status:
- Mode: CHAT
- Connected Servers: 3
- Memory: ENABLED (Redis localhost:6379)
- Debug: OFF
- Session Duration: 45 minutes
```

### How Redis Memory Works

1. **Automatic Saving**: Conversations automatically saved to Redis
2. **Context Preservation**: Maintains conversation context across restarts
3. **Session Restoration**: Previous conversations loaded on startup
4. **Intelligent Pruning**: Old conversations automatically cleaned up

### Example Session with Redis

```bash
# Session 1
> /memory
Memory persistence is now ENABLED using Redis

> Hello, I'm working on a Python project
AI: Hello! I'd be happy to help with your Python project. What specific
    aspect are you working on?

> I need to analyze some CSV files
AI: Great! I can help you analyze CSV files. Do you have the files ready?

# Exit MCPOmni Connect

# Session 2 (later)
> mcpomni_connect
🚀 MCPOmni Connect - Universal Gateway to MCP Servers
📚 Restored conversation from Redis (5 messages)

> What were we discussing?
AI: We were discussing your Python project, specifically analyzing CSV files.
    You mentioned you needed help with CSV analysis. Are you ready to continue?
```

## File-Based Chat History

### Overview

File-based history allows manual saving and loading of specific conversations, useful for:

- **Project Documentation**: Save conversations related to specific projects
- **Backup**: Create backups of important discussions
- **Sharing**: Share conversation history with team members
- **Templates**: Save common workflows as templates

### Saving Conversations

#### Manual Save

```bash
/save:filename.json
```

**Examples:**
```bash
# Save with descriptive names
/save:database_migration_discussion.json
/save:bug_investigation_2024-01-15.json
/save:deployment_workflow.json

# Save with timestamps
/save:session_$(date +%Y%m%d_%H%M).json
```

**Response:**
```
✅ Conversation saved to database_migration_discussion.json
Saved 15 messages (3,247 tokens)
File location: ./database_migration_discussion.json
```

### Loading Conversations

#### Manual Load

```bash
/load:filename.json
```

**Examples:**
```bash
# Load specific conversation
/load:database_migration_discussion.json

# Load recent session
/load:session_20240115_1430.json
```

**Response:**
```
✅ Conversation loaded from database_migration_discussion.json
Loaded 15 messages from previous session
Context restored: Database migration planning
```

### File Format

Conversation files are saved in JSON format:

```json title="example_conversation.json"
{
    "metadata": {
        "version": "1.0",
        "created_at": "2024-01-15T14:30:00Z",
        "mcpomni_version": "0.3.0",
        "total_messages": 15,
        "total_tokens": 3247,
        "session_duration": "45 minutes"
    },
    "configuration": {
        "llm_provider": "openai",
        "llm_model": "gpt-4o-mini",
        "connected_servers": ["filesystem", "database", "notifications"]
    },
    "conversation": [
        {
            "timestamp": "2024-01-15T14:30:15Z",
            "role": "user",
            "content": "Help me analyze the database schema",
            "command": null
        },
        {
            "timestamp": "2024-01-15T14:30:20Z",
            "role": "assistant",
            "content": "I'll help you analyze the database schema...",
            "tools_used": ["query_database"],
            "tokens": 156
        }
    ]
}
```

## Memory Management Commands

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/memory` | Toggle Redis persistence | `/memory` |
| `/save:file` | Save to file | `/save:project.json` |
| `/load:file` | Load from file | `/load:project.json` |
| `/clear` | Clear current memory | `/clear` |
| `/history` | Show recent history | `/history` |

### Advanced Commands

#### `/history`
Show recent conversation history:

```bash
/history
```

**Output:**
```
📚 Recent Conversation History:
[14:30] User: Help me analyze the database schema
[14:31] AI: I'll analyze the schema using database tools...
[14:32] User: /tools
[14:32] AI: Available tools: query_database, get_schema...
[14:35] User: Show me the users table structure
[14:36] AI: Here's the users table structure...
```

#### `/clear`
Clear current conversation memory:

```bash
/clear
```

**Response:**
```
🧹 Conversation history cleared
- Session memory: cleared
- Redis memory: preserved (use /memory to disable)
- File history: preserved
```

## Memory Configuration

### Redis Configuration Options

```bash title=".env"
# Basic Redis setup
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Advanced Redis setup
REDIS_PASSWORD=secure_password
REDIS_SSL=true
REDIS_MAX_CONNECTIONS=10
REDIS_TIMEOUT=30

# Memory management
REDIS_TTL=604800          # 7 days in seconds
REDIS_MAX_MESSAGES=1000   # Max messages per conversation
```

### Memory Limits

Configure memory limits in `servers_config.json`:

```json
{
    "AgentConfig": {
        "memory_settings": {
            "max_conversation_length": 1000,    // Max messages
            "max_context_tokens": 50000,        // Max tokens in context
            "auto_prune_threshold": 0.8,        // Prune when 80% full
            "redis_ttl_days": 7                 // Redis expiration
        }
    }
}
```

## Memory Usage Patterns

### Project-Based Memory

Organize conversations by project:

```bash
# Start project
/load:project_alpha_setup.json

# Work on project
[... development conversation ...]

# Save progress
/save:project_alpha_progress_$(date +%m%d).json

# End session
/save:project_alpha_final.json
```

### Daily Workflow Memory

```bash
# Morning: Load yesterday's context
/load:daily_work_$(date -d yesterday +%Y%m%d).json

# Work throughout day with Redis persistence
/memory  # Ensure Redis is enabled

# Evening: Save daily summary
/save:daily_work_$(date +%Y%m%d).json
```

### Team Collaboration Memory

```bash
# Save conversation for team review
/save:team_review_database_design.json

# Team member loads and continues
/load:team_review_database_design.json
# Continue conversation with context
```

## Memory Best Practices

### When to Use Each Type

!!! tip "Memory Type Selection"
    - **Session Memory**: Default for temporary work
    - **Redis Memory**: Long-running projects, development work
    - **File History**: Important conversations, team sharing, backups

### Optimization Tips

1. **Regular Cleanup**
   ```bash
   # Clear old conversations periodically
   /clear

   # Save important parts before clearing
   /save:important_findings.json
   ```

2. **Strategic Saving**
   ```bash
   # Save at natural breakpoints
   /save:analysis_complete.json    # After major analysis
   /save:before_deployment.json    # Before risky operations
   /save:meeting_notes.json        # After team discussions
   ```

3. **Context Management**
   ```bash
   # Load relevant context
   /load:project_context.json

   # Add new information
   [... conversation ...]

   # Save updated context
   /save:project_context_updated.json
   ```

## Troubleshooting Memory

### Redis Connection Issues

!!! failure "Redis Connection Failed"
    **Error**: `Could not connect to Redis`

    **Solutions**:
    ```bash
    # Check Redis status
    redis-cli ping

    # Start Redis if needed
    sudo systemctl start redis-server

    # Check configuration
    cat .env | grep REDIS

    # Test connection manually
    redis-cli -h localhost -p 6379
    ```

### File Loading Issues

!!! failure "File Not Found"
    **Error**: `Could not load conversation file`

    **Solutions**:
    ```bash
    # Check file exists
    ls -la *.json

    # Use full path
    /load:/full/path/to/conversation.json

    # Check file permissions
    chmod 644 conversation.json
    ```

### Memory Performance Issues

!!! failure "Slow Memory Operations"
    **Issue**: Memory operations taking too long

    **Solutions**:
    ```bash
    # Check Redis memory usage
    redis-cli info memory

    # Clear old conversations
    /clear

    # Reduce context size
    # Edit AgentConfig.memory_settings
    ```

## Advanced Memory Features

### Memory Analytics

```bash
# Check memory usage
/memory stats
```

**Output:**
```
📊 Memory Usage Statistics:
- Redis Memory: 15.2 MB
- Active Conversations: 3
- Total Messages: 1,247
- Average Message Size: 89 tokens
- Oldest Conversation: 5 days ago
- Memory Efficiency: 92%
```

### Automatic Memory Management

MCPOmni Connect automatically:

1. **Prunes Old Messages**: Removes messages beyond token limits
2. **Compresses Context**: Summarizes old conversations
3. **Cleans Expired Data**: Removes data past TTL
4. **Optimizes Storage**: Compacts conversation data

### Memory Integration with Modes

Different operation modes use memory differently:

| Mode | Memory Usage | Context Retention |
|------|-------------|-------------------|
| **Chat** | Full history | High |
| **Autonomous** | Task-focused | Medium |
| **Orchestrator** | Strategic context | Variable |

---

**Next**: [Prompt Management →](prompt-management.md)
