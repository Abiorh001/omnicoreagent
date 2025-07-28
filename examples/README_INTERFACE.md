# OmniAgent Unified Interface

A comprehensive interface for the OmniAgent that supports both CLI and Web modes, showcasing all features and capabilities.

## 🚀 Quick Start

### CLI Mode (Default)
```bash
# Run in CLI mode
python run_omni_agent.py

# Or explicitly specify CLI mode
python run_omni_agent.py --mode cli
```

### Web Mode
```bash
# Run in Web mode
python run_omni_agent.py --mode web

# Then open your browser to: http://localhost:5000
```

## 📋 Features

### 🤖 Agent Capabilities
- **Mathematical Tools**: Calculate area, perimeter, analyze numbers
- **Text Processing**: Format text, word count, case conversion
- **System Information**: Get OS info, platform details, current time
- **Data Analysis**: Statistical analysis of number lists
- **File System**: List directories, browse files
- **Memory Management**: Persistent conversation history
- **Event Streaming**: Real-time event monitoring
- **Session Management**: Multiple concurrent sessions

### 💻 CLI Mode Features
- **Interactive Chat**: Real-time conversation with the agent
- **Command System**: Built-in commands for various operations
- **Memory Management**: View, clear, save, and load conversation history
- **Tool Information**: List and explore available tools
- **Backend Switching**: Switch between different memory and event backends
- **Session Management**: Automatic session ID generation

### 🌐 Web Mode Features
- **Modern UI**: Beautiful, responsive web interface
- **Real-time Chat**: WebSocket-based real-time messaging
- **Feature Panels**: Sidebar with tools, history, and configuration
- **Session Management**: Web-based session handling
- **Tool Integration**: Visual tool listing and usage
- **History Viewing**: Browse conversation history
- **Configuration**: Switch backends and view agent info

## 🎯 Available Commands (CLI Mode)

| Command | Description |
|---------|-------------|
| `/help` | Show help and available commands |
| `/memory` | Show memory store information |
| `/events` | Show event store information |
| `/tools` | List all available tools |
| `/history` | Show conversation history |
| `/clear` | Clear conversation history |
| `/save <file>` | Save conversation to file |
| `/load <file>` | Load conversation from file |
| `/switch <backend>` | Switch memory/event backends |
| `/quit` | Exit the interface |

## 🔧 Available Tools

### Mathematical Tools
- **calculate_area**: Calculate rectangle area
- **calculate_perimeter**: Calculate rectangle perimeter

### Text Processing Tools
- **format_text**: Format text in different styles (uppercase, lowercase, title, reverse)
- **word_count**: Count words in text

### System Tools
- **system_info**: Get system information (OS, architecture, Python version, time)

### Data Analysis Tools
- **analyze_numbers**: Analyze lists of numbers (count, sum, average, min, max)

### File System Tools
- **list_directory**: List directory contents

## 📊 Example Usage

### CLI Mode Example
```bash
$ python run_omni_agent.py

🤖 OMNIGENT UNIFIED INTERFACE - CLI MODE
================================================================================
Available Commands:
  /help              - Show this help
  /memory            - Show memory information
  /events            - Show event information
  /tools             - List available tools
  /history           - Show conversation history
  /clear             - Clear conversation history
  /save <file>       - Save conversation to file
  /load <file>       - Load conversation from file
  /switch <backend>  - Switch memory/event backends
  /quit              - Exit the interface
  <message>          - Send message to agent
================================================================================

💬 Start chatting with the agent! (Type /help for commands)

👤 You: Calculate the area of a rectangle with length 10 and width 5
🤖 Processing: Calculate the area of a rectangle with length 10 and width 5
✅ Response: I'll calculate the area of a rectangle with length 10 and width 5 for you.

Using the calculate_area tool:
Area of rectangle (10 x 5): 50 square units

The area of the rectangle is 50 square units.

👤 You: /tools
🔧 Available Tools:
  • calculate_area: Calculate the area of a rectangle.
  • calculate_perimeter: Calculate the perimeter of a rectangle.
  • format_text: Format text in different styles.
  • word_count: Count words in text.
  • system_info: Get basic system information.
  • analyze_numbers: Analyze a list of numbers.
  • list_directory: List contents of a directory.
```

### Web Mode Example
1. Start the web interface: `python run_omni_agent.py --mode web`
2. Open browser to `http://localhost:5000`
3. Use the modern web interface with:
   - Real-time chat
   - Tool panel showing available tools
   - History panel showing conversation history
   - Configuration panel for backend switching

## 🛠️ Installation Requirements

### Basic Requirements
```bash
pip install -r requirements.txt
```

### Web Mode Requirements
```bash
pip install flask flask-socketio
```

## 🔄 Backend Switching

### Memory Backends
- `in_memory`: Fast in-memory storage (default)
- `redis`: Redis-based persistent storage
- `database`: Database-based persistent storage (SQLite/PostgreSQL)

### Event Backends
- `in_memory`: In-memory event storage (default)
- `redis_stream`: Redis Streams for event streaming

### Switching Backends
```bash
# CLI Mode
/switch memory:redis
/switch event:redis_stream

# Web Mode
Use the Configuration panel in the sidebar
```

## 📁 File Structure

```
examples/
├── omni_agent_interface.py      # Main interface implementation
├── templates/
│   └── omni_agent_interface.html # Web interface template
├── README_INTERFACE.md          # This file
└── run_omni_agent.py           # Simple runner script
```

## 🎨 Customization

### Adding New Tools
1. Modify the `create_comprehensive_tool_registry()` function in `omni_agent_interface.py`
2. Add new tool functions with the `@tool_registry.register_tool()` decorator
3. Restart the interface

### Customizing the Web Interface
1. Modify `templates/omni_agent_interface.html`
2. Update styles, add new features, or modify the layout
3. Restart the web interface

### Customizing the CLI Interface
1. Modify the `OmniAgentInterface` class in `omni_agent_interface.py`
2. Add new commands in the `handle_cli_command()` method
3. Restart the interface

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure you're in the correct directory
cd /path/to/mcp_omni_connect

# Install dependencies
pip install -r requirements.txt
```

**Web Mode Not Working**
```bash
# Install Flask dependencies
pip install flask flask-socketio

# Check if port 5000 is available
# Try a different port if needed
```

**Memory/Event Backend Errors**
```bash
# Check if Redis is running (if using Redis backend)
redis-server

# Check database connection (if using database backend)
# Ensure SQLite file is writable or PostgreSQL is accessible
```

## 🚀 Advanced Usage

### Environment Variables
```bash
export OPENAI_API_KEY="your-api-key"
export DATABASE_URL="postgresql://user:pass@localhost/db"
export REDIS_URL="redis://localhost:6379"
```

### Custom Configuration
```python
# Modify the agent configuration in omni_agent_interface.py
agent_config = {
    "max_steps": 20,  # Increase for complex tasks
    "tool_call_timeout": 120,  # Increase timeout
    "request_limit": 2000,  # Increase request limit
    "memory_config": {"mode": "token_budget", "value": 15000},
}
```

### Integration with Other Systems
The interface can be easily integrated with other systems by:
1. Importing the `OmniAgentInterface` class
2. Using the agent programmatically
3. Extending the interface with custom features

## 📈 Performance Tips

1. **Use appropriate backends**: In-memory for development, Redis/Database for production
2. **Monitor memory usage**: Clear history periodically in long sessions
3. **Optimize tool calls**: Use specific tools rather than complex multi-step requests
4. **Session management**: Use different sessions for different contexts

## 🤝 Contributing

To add new features to the interface:

1. **New Tools**: Add to `create_comprehensive_tool_registry()`
2. **New Commands**: Add to `handle_cli_command()` method
3. **Web Features**: Modify the HTML template and JavaScript
4. **Backend Support**: Add new memory/event store implementations

## 📄 License

This interface is part of the OmniAgent project and follows the same license terms. 