# 🚀 MCPOmni Connect - Universal Gateway to MCP Servers

[![PyPI Downloads](https://static.pepy.tech/badge/mcpomni-connect)](https://pepy.tech/projects/mcpomni-connect)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/Abiorh001/mcp_omni_connect/actions)
[![PyPI version](https://badge.fury.io/py/mcpomni-connect.svg)](https://badge.fury.io/py/mcpomni-connect)
[![Last Commit](https://img.shields.io/github/last-commit/Abiorh001/mcp_omni_connect)](https://github.com/Abiorh001/mcp_omni_connect/commits/main)
[![Open Issues](https://img.shields.io/github/issues/Abiorh001/mcp_omni_connect)](https://github.com/Abiorh001/mcp_omni_connect/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/Abiorh001/mcp_omni_connect)](https://github.com/Abiorh001/mcp_omni_connect/pulls)

MCPOmni Connect is a powerful, intelligent AI agent system and universal command-line interface (CLI) that goes beyond being just a gateway to the Model Context Protocol (MCP) ecosystem. It acts as an autonomous agent through its **ReAct Agent Mode** and **Orchestrator Mode**, capable of independent reasoning, decision-making, and complex task execution. It seamlessly integrates multiple MCP servers, AI models, and various transport protocols into a unified, intelligent interface that can operate autonomously or interactively.

> 🚀 **New User?** Start with the [⚙️ Configuration Guide](#%EF%B8%8F-configuration-guide) to understand the difference between config files, transport types, and OAuth behavior. Then check out the [🧪 Testing](#-testing) section to get started quickly.

## ✨ Key Features

### 🤖 Intelligent Agent System

- **ReAct Agent Mode**
  - Autonomous task execution with reasoning and action cycles
  - Independent decision-making without human intervention
  - Advanced problem-solving through iterative reasoning
  - Self-guided tool selection and execution
  - Complex task decomposition and handling
- **Orchestrator Agent Mode**
  - Strategic multi-step task planning and execution
  - Intelligent coordination across multiple MCP servers
  - Dynamic agent delegation and communication
  - Parallel task execution when possible
  - Sophisticated workflow management with real-time progress monitoring
- **Interactive Chat Mode**
  - Human-in-the-loop task execution with approval workflows
  - Step-by-step guidance and explanations
  - Educational mode for understanding AI decision processes

### 🔌 Universal Connectivity

- **Multi-Protocol Support**
  - Native support for stdio transport
  - Server-Sent Events (SSE) for real-time communication
  - Streamable HTTP for efficient data streaming
  - Docker container integration
  - NPX package execution
  - Extensible transport layer for future protocols
- **Authentication Support**
  - OAuth 2.0 authentication flow
  - Bearer token authentication
  - Custom header support
  - Secure credential management
- **Agentic Operation Modes**
  - Seamless switching between chat, autonomous, and orchestrator modes
  - Context-aware mode selection based on task complexity
  - Persistent state management across mode transitions

### 🧠 AI-Powered Intelligence

- **Unified LLM Integration with LiteLLM**
  - Single unified interface for all AI providers
  - Support for 100+ models across providers including:
    - OpenAI (GPT-4, GPT-3.5, etc.)
    - Anthropic (Claude 3.5 Sonnet, Claude 3 Haiku, etc.)
    - Google (Gemini Pro, Gemini Flash, etc.)
    - Groq (Llama, Mixtral, Gemma, etc.)
    - DeepSeek (DeepSeek-V3, DeepSeek-Coder, etc.)
    - Azure OpenAI
    - OpenRouter (access to 200+ models)
    - Ollama (local models)
  - Simplified configuration and reduced complexity
  - Dynamic system prompts based on available capabilities
  - Intelligent context management
  - Automatic tool selection and chaining
  - Universal model support through custom ReAct Agent
    - Handles models without native function calling
    - Dynamic function execution based on user requests
    - Intelligent tool orchestration

### 🔒 Security & Privacy

- **Explicit User Control**
  - All tool executions require explicit user approval in chat mode
  - Clear explanation of tool actions before execution
  - Transparent disclosure of data access and usage
- **Data Protection**
  - Strict data access controls
  - Server-specific data isolation
  - No unauthorized data exposure
- **Privacy-First Approach**
  - Minimal data collection
  - User data remains on specified servers
  - No cross-server data sharing without consent
- **Secure Communication**
  - Encrypted transport protocols
  - Secure API key management
  - Environment variable protection

### 💾 Memory Management

- **Redis-Powered Persistence**
  - Long-term conversation memory storage
  - Session persistence across restarts
  - Configurable memory retention
  - Easy memory toggle with commands
- **Chat History File Storage**
  - Save complete chat conversations to files
  - Load previous conversations from saved files
  - Continue conversations from where you left off
  - Persistent chat history across sessions
  - File-based backup and restoration of conversations
- **Intelligent Context Management**
  - Automatic context pruning
  - Relevant information retrieval
  - Memory-aware responses
  - Cross-session context maintenance

### 💬 Prompt Management

- **Advanced Prompt Handling**
  - Dynamic prompt discovery across servers
  - Flexible argument parsing (JSON and key-value formats)
  - Cross-server prompt coordination
  - Intelligent prompt validation
  - Context-aware prompt execution
  - Real-time prompt responses
  - Support for complex nested arguments
  - Automatic type conversion and validation
- **Client-Side Sampling Support**
  - Dynamic sampling configuration from client
  - Flexible LLM response generation
  - Customizable sampling parameters
  - Real-time sampling adjustments

### 🛠️ Tool Orchestration

- **Dynamic Tool Discovery & Management**
  - Automatic tool capability detection
  - Cross-server tool coordination
  - Intelligent tool selection based on context
  - Real-time tool availability updates

### 📦 Resource Management

- **Universal Resource Access**
  - Cross-server resource discovery
  - Unified resource addressing
  - Automatic resource type detection
  - Smart content summarization

### 🔄 Server Management

- **Advanced Server Handling**
  - Multiple simultaneous server connections
  - Automatic server health monitoring
  - Graceful connection management
  - Dynamic capability updates
  - Flexible authentication methods
  - Runtime server configuration updates

## 🏗️ Architecture

### Core Components

```
MCPOmni Connect
├── Transport Layer
│   ├── Stdio Transport
│   ├── SSE Transport
│   └── Docker Integration
├── Session Management
│   ├── Multi-Server Orchestration
│   └── Connection Lifecycle Management
├── Tool Management
│   ├── Dynamic Tool Discovery
│   ├── Cross-Server Tool Routing
│   └── Tool Execution Engine
└── AI Integration
    ├── LLM Processing
    ├── Context Management
    └── Response Generation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- LLM API key
- UV package manager (recommended)
- Redis server (optional, for persistent memory)

### Install using package manager

#### with uv recommended

```bash
uv add mcpomni-connect
```

#### using pip

```bash
pip install mcpomni-connect
```

### Configuration

```bash
# Set up environment variables
echo "LLM_API_KEY=your_key_here" > .env
# Optional: Configure Redis connection
echo "REDIS_HOST=localhost" >> .env
echo "REDIS_PORT=6379" >> .env
echo "REDIS_DB=0" >> .env"
# Configure your servers in servers_config.json
```

## ⚙️ Configuration Guide

### Configuration Files Overview

MCPOmni Connect uses **two separate configuration files** for different purposes:

#### 1. `.env` File - Environment Variables

Contains sensitive information like API keys and optional settings:

```bash
# Required: Your LLM provider API key
LLM_API_KEY=your_api_key_here

# Optional: Redis configuration (for persistent memory)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

#### 2. `servers_config.json` - Server & Agent Configuration

Contains application settings, LLM configuration, and MCP server connections:

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
    "your-server-name": {
      "transport_type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-package"]
    }
  }
}
```

### 🚦 Transport Types & Authentication

MCPOmni Connect supports multiple ways to connect to MCP servers:

#### 1. **stdio** - Direct Process Communication

**Use when**: Connecting to local MCP servers that run as separate processes

```json
{
  "server-name": {
    "transport_type": "stdio",
    "command": "uvx",
    "args": ["mcp-server-package"]
  }
}
```

- **No authentication needed**
- **No OAuth server started**
- Most common for local development

#### 2. **sse** - Server-Sent Events

**Use when**: Connecting to HTTP-based MCP servers using Server-Sent Events

```json
{
  "server-name": {
    "transport_type": "sse",
    "url": "http://your-server.com:4010/sse",
    "headers": {
      "Authorization": "Bearer your-token"
    },
    "timeout": 60,
    "sse_read_timeout": 120
  }
}
```

- **Uses Bearer token or custom headers**
- **No OAuth server started**

#### 3. **streamable_http** - HTTP with Optional OAuth

**Use when**: Connecting to HTTP-based MCP servers with or without OAuth

**Without OAuth (Bearer Token):**

```json
{
  "server-name": {
    "transport_type": "streamable_http",
    "url": "http://your-server.com:4010/mcp",
    "headers": {
      "Authorization": "Bearer your-token"
    },
    "timeout": 60
  }
}
```

- **Uses Bearer token or custom headers**
- **No OAuth server started**

**With OAuth:**

```json
{
  "server-name": {
    "transport_type": "streamable_http",
    "auth": {
      "method": "oauth"
    },
    "url": "http://your-server.com:4010/mcp"
  }
}
```

- **OAuth callback server automatically starts on `http://localhost:3000`**
- **This is hardcoded and cannot be changed**
- **Required for OAuth flow to work properly**

### 🔐 OAuth Server Behavior

**Important**: When using OAuth authentication, MCPOmni Connect automatically starts an OAuth callback server.

#### What You'll See:

```
🖥️  Started callback server on http://localhost:3000
```

#### Key Points:

- **This is normal behavior** - not an error
- **The address `http://localhost:3000` is hardcoded** and cannot be changed
- **The server only starts when** you have `"auth": {"method": "oauth"}` in your config
- **The server stops** when the application shuts down
- **Only used for OAuth token handling** - no other purpose

#### When OAuth is NOT Used:

- Remove the entire `"auth"` section from your server configuration
- Use `"headers"` with `"Authorization": "Bearer token"` instead
- No OAuth server will start

### 🛠️ Troubleshooting Common Issues

#### "Failed to connect to server: Session terminated"

**Possible Causes & Solutions:**

1. **Wrong Transport Type**

   ```
   Problem: Your server expects 'stdio' but you configured 'streamable_http'
   Solution: Check your server's documentation for the correct transport type
   ```

2. **OAuth Configuration Mismatch**

   ```
   Problem: Your server doesn't support OAuth but you have "auth": {"method": "oauth"}
   Solution: Remove the "auth" section entirely and use headers instead:

   "headers": {
       "Authorization": "Bearer your-token"
   }
   ```

3. **Server Not Running**

   ```
   Problem: The MCP server at the specified URL is not running
   Solution: Start your MCP server first, then connect with MCPOmni Connect
   ```

4. **Wrong URL or Port**
   ```
   Problem: URL in config doesn't match where your server is running
   Solution: Verify the server's actual address and port
   ```

#### "Started callback server on http://localhost:3000" - Is This Normal?

**Yes, this is completely normal** when:

- You have `"auth": {"method": "oauth"}` in any server configuration
- The OAuth server handles authentication tokens automatically
- You cannot and should not try to change this address

**If you don't want the OAuth server:**

- Remove `"auth": {"method": "oauth"}` from all server configurations
- Use alternative authentication methods like Bearer tokens

### 📋 Configuration Examples by Use Case

#### Local Development (stdio)

```json
{
  "mcpServers": {
    "local-tools": {
      "transport_type": "stdio",
      "command": "uvx",
      "args": ["mcp-server-tools"]
    }
  }
}
```

#### Remote Server with Token

```json
{
  "mcpServers": {
    "remote-api": {
      "transport_type": "streamable_http",
      "url": "http://api.example.com:8080/mcp",
      "headers": {
        "Authorization": "Bearer abc123token"
      }
    }
  }
}
```

#### Remote Server with OAuth

```json
{
  "mcpServers": {
    "oauth-server": {
      "transport_type": "streamable_http",
      "auth": {
        "method": "oauth"
      },
      "url": "http://oauth-server.com:8080/mcp"
    }
  }
}
```

### Start CLI

```bash
# start the cli running the command ensure your api key is exported or create .env
mcpomni_connect
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_specific_file.py -v

# Run tests with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
```

### Development Quick Start

1. **Installation**

   ```bash
   # Clone the repository
   git clone https://github.com/Abiorh001/mcp_omni_connect.git
   cd mcp_omni_connect

   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate

   # Install dependencies
   uv sync
   ```

2. **Configuration**

   ```bash
   # Set up environment variables
   echo "LLM_API_KEY=your_key_here" > .env

   # Configure your servers in servers_config.json
   ```

3. ** Start Client**
   ```bash
   # Start the client
   uv run run.py
   # or
   python run.py
   ```

## 🧑‍💻 Examples

### Basic CLI Example

You can run the basic CLI example to interact with MCPOmni Connect directly from the terminal.

**Using [uv](https://github.com/astral-sh/uv) (recommended):**

```bash
uv run examples/basic.py
```

**Or using Python directly:**

```bash
python examples/basic.py
```

---

### FastAPI Server Example

You can also run MCPOmni Connect as a FastAPI server for web or API-based interaction.

**Using [uv](https://github.com/astral-sh/uv):**

```bash
uv run examples/fast_api_iml.py
```

**Or using Python directly:**

```bash
python examples/fast_api_iml.py
```

### Web Client

A simple web client is provided in `examples/index.html`.

- Open it in your browser after starting the FastAPI server.
- It connects to `http://localhost:8000` and provides a chat interface.
- The FastAPI server will start on `http://localhost:8000` by default.
- You can interact with the API (see `examples/index.html` for a simple web client).

### FastAPI API Endpoints

#### `/chat/agent_chat` (POST)

- **Description:** Send a chat query to the agent and receive a streamed response.
- **Request:**
  ```json
  {
    "query": "Your question here",
    "chat_id": "unique-chat-id"
  }
  ```
- **Response:** Streamed JSON lines, each like:
  ```json
  {
    "message_id": "...",
    "usid": "...",
    "role": "assistant",
    "content": "Response text",
    "meta": [],
    "likeordislike": null,
    "time": "2024-06-10 12:34:56"
  }
  ```

## 🛠️ Developer Integration

MCPOmni Connect is not just a CLI tool—it's also a powerful Python library that you can use to build your own backend services, custom clients, or API servers.

### Build Your Own MCP Client

You can import MCPOmni Connect in your Python project to:

- Connect to one or more MCP servers
- Choose between **ReAct Agent** mode (autonomous tool use) or **Orchestrator Agent** mode (multi-step, multi-server planning)
- Manage memory, context, and tool orchestration
- Expose your own API endpoints (e.g., with FastAPI, Flask, etc.)

#### Example: Custom Backend with FastAPI

See [`examples/fast_api_iml.py`](examples/fast_api_iml.py) for a full-featured example.

**Minimal Example:**

```python
from mcpomni_connect.client import Configuration, MCPClient
from mcpomni_connect.llm import LLMConnection
from mcpomni_connect.agents.react_agent import ReactAgent
from mcpomni_connect.agents.orchestrator import OrchestratorAgent

config = Configuration()
client = MCPClient(config)
llm_connection = LLMConnection(config)

# Choose agent mode
agent = ReactAgent(...)  # or OrchestratorAgent(...)

# Use in your API endpoint
response = await agent.run(
    query="Your user query",
    sessions=client.sessions,
    llm_connection=llm_connection,
    # ...other arguments...
)
```

#### FastAPI Integration

You can easily expose your MCP client as an API using FastAPI.  
See the [FastAPI example](examples/fast_api_iml.py) for:

- Async server startup and shutdown
- Handling chat requests with different agent modes
- Streaming responses to clients

**Key Features for Developers:**

- Full control over agent configuration and limits
- Support for both chat and autonomous agentic modes
- Easy integration with any Python web framework

---

### Server Configuration Examples

#### Basic OpenAI Configuration

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
    "model": "gpt-4",
    "temperature": 0.5,
    "max_tokens": 5000,
    "max_context_length": 30000,
    "top_p": 0
  },
  "mcpServers": {
    "ev_assistant": {
      "transport_type": "streamable_http",
      "auth": {
        "method": "oauth"
      },
      "url": "http://localhost:8000/mcp"
    },
    "sse-server": {
      "transport_type": "sse",
      "url": "http://localhost:3000/sse",
      "headers": {
        "Authorization": "Bearer token"
      },
      "timeout": 60,
      "sse_read_timeout": 120
    },
    "streamable_http-server": {
      "transport_type": "streamable_http",
      "url": "http://localhost:3000/mcp",
      "headers": {
        "Authorization": "Bearer token"
      },
      "timeout": 60,
      "sse_read_timeout": 120
    }
  }
}
```

#### Anthropic Claude Configuration

```json
{
  "LLM": {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.7,
    "max_tokens": 4000,
    "max_context_length": 200000,
    "top_p": 0.95
  }
}
```

#### Groq Configuration

```json
{
  "LLM": {
    "provider": "groq",
    "model": "llama-3.1-8b-instant",
    "temperature": 0.5,
    "max_tokens": 2000,
    "max_context_length": 8000,
    "top_p": 0.9
  }
}
```

#### Azure OpenAI Configuration

```json
{
  "LLM": {
    "provider": "azureopenai",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "max_context_length": 100000,
    "top_p": 0.95,
    "azure_endpoint": "https://your-resource.openai.azure.com",
    "azure_api_version": "2024-02-01",
    "azure_deployment": "your-deployment-name"
  }
}
```

#### Ollama Local Model Configuration

```json
{
  "LLM": {
    "provider": "ollama",
    "model": "llama3.1:8b",
    "temperature": 0.5,
    "max_tokens": 5000,
    "max_context_length": 100000,
    "top_p": 0.7,
    "ollama_host": "http://localhost:11434"
  }
}
```

#### OpenRouter Configuration

```json
{
  "LLM": {
    "provider": "openrouter",
    "model": "anthropic/claude-3.5-sonnet",
    "temperature": 0.7,
    "max_tokens": 4000,
    "max_context_length": 200000,
    "top_p": 0.95
  }
}
```

### 🔐 Authentication Methods

MCPOmni Connect supports multiple authentication methods for secure server connections:

#### OAuth 2.0 Authentication

```json
{
  "server_name": {
    "transport_type": "streamable_http",
    "auth": {
      "method": "oauth"
    },
    "url": "http://your-server/mcp"
  }
}
```

#### Bearer Token Authentication

```json
{
  "server_name": {
    "transport_type": "streamable_http",
    "headers": {
      "Authorization": "Bearer your-token-here"
    },
    "url": "http://your-server/mcp"
  }
}
```

#### Custom Headers

```json
{
  "server_name": {
    "transport_type": "streamable_http",
    "headers": {
      "X-Custom-Header": "value",
      "Authorization": "Custom-Auth-Scheme token"
    },
    "url": "http://your-server/mcp"
  }
}
```

## 🔄 Dynamic Server Configuration

MCPOmni Connect supports dynamic server configuration through commands:

#### Add New Servers

```bash
# Add one or more servers from a configuration file
/add_servers:path/to/config.json
```

The configuration file can include multiple servers with different authentication methods:

```json
{
  "new-server": {
    "transport_type": "streamable_http",
    "auth": {
      "method": "oauth"
    },
    "url": "http://localhost:8000/mcp"
  },
  "another-server": {
    "transport_type": "sse",
    "headers": {
      "Authorization": "Bearer token"
    },
    "url": "http://localhost:3000/sse"
  }
}
```

#### Remove Servers

```bash
# Remove a server by its name
/remove_server:server_name
```

## 🎯 Usage

### Interactive Commands

- `/tools` - List all available tools across servers
- `/prompts` - View available prompts
- `/prompt:<name>/<args>` - Execute a prompt with arguments
- `/resources` - List available resources
- `/resource:<uri>` - Access and analyze a resource
- `/debug` - Toggle debug mode
- `/refresh` - Update server capabilities
- `/memory` - Toggle Redis memory persistence (on/off)
- `/mode:auto` - Switch to autonomous agentic mode
- `/mode:chat` - Switch back to interactive chat mode
- `/add_servers:<config.json>` - Add one or more servers from a configuration file
- `/remove_server:<server_name>` - Remove a server by its name

### Memory and Chat History

```bash
# Enable Redis memory persistence
/memory

# Check memory status
Memory persistence is now ENABLED using Redis

# Disable memory persistence
/memory

# Check memory status
Memory persistence is now DISABLED
```

### Operation Modes

```bash
# Switch to autonomous mode
/mode:auto

# System confirms mode change
Now operating in AUTONOMOUS mode. I will execute tasks independently.

# Switch back to chat mode
/mode:chat

# System confirms mode change
Now operating in CHAT mode. I will ask for approval before executing tasks.
```

### Mode Differences

- **Chat Mode (Default)**

  - Requires explicit approval for tool execution
  - Interactive conversation style
  - Step-by-step task execution
  - Detailed explanations of actions

- **Autonomous Mode**

  - Independent task execution
  - Self-guided decision making
  - Automatic tool selection and chaining
  - Progress updates and final results
  - Complex task decomposition
  - Error handling and recovery

- **Orchestrator Mode**
  - Advanced planning for complex multi-step tasks
  - Strategic delegation across multiple MCP servers
  - Intelligent agent coordination and communication
  - Parallel task execution when possible
  - Dynamic resource allocation
  - Sophisticated workflow management
  - Real-time progress monitoring across agents
  - Adaptive task prioritization

### Prompt Management

```bash
# List all available prompts
/prompts

# Basic prompt usage
/prompt:weather/location=tokyo

# Prompt with multiple arguments depends on the server prompt arguments requirements
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

# Nested argument structures
/prompt:market-research/target=smartphones/criteria={
    "price_range": {"min": 500, "max": 1000},
    "features": ["5G", "wireless-charging"],
    "markets": ["US", "EU", "Asia"]
}
```

### Advanced Prompt Features

- **Argument Validation**: Automatic type checking and validation
- **Default Values**: Smart handling of optional arguments
- **Context Awareness**: Prompts can access previous conversation context
- **Cross-Server Execution**: Seamless execution across multiple MCP servers
- **Error Handling**: Graceful handling of invalid arguments with helpful messages
- **Dynamic Help**: Detailed usage information for each prompt

### AI-Powered Interactions

The client intelligently:

- Chains multiple tools together
- Provides context-aware responses
- Automatically selects appropriate tools
- Handles errors gracefully
- Maintains conversation context

### Model Support with LiteLLM

- **Unified Model Access**
  - Single interface for 100+ models across all major providers
  - Automatic provider detection and routing
  - Consistent API regardless of underlying provider
  - Native function calling for compatible models
  - ReAct Agent fallback for models without function calling
- **Supported Providers**
  - **OpenAI**: GPT-4, GPT-3.5, and all model variants
  - **Anthropic**: Claude 3.5 Sonnet, Claude 3 Haiku, Claude 3 Opus
  - **Google**: Gemini Pro, Gemini Flash, PaLM models
  - **Groq**: Ultra-fast inference for Llama, Mixtral, Gemma
  - **DeepSeek**: DeepSeek-V3, DeepSeek-Coder, and specialized models
  - **Azure OpenAI**: Enterprise-grade OpenAI models
  - **OpenRouter**: Access to 200+ models from various providers
  - **Ollama**: Local model execution with privacy
- **Advanced Features**
  - Automatic model capability detection
  - Dynamic tool execution based on model features
  - Intelligent fallback mechanisms
  - Provider-specific optimizations

### Token & Usage Management

MCPOmni Connect now provides advanced controls and visibility over your API usage and resource limits.

#### View API Usage Stats

Use the `/api_stats` command to see your current usage:

```bash
/api_stats
```

This will display:

- **Total tokens used**
- **Total requests made**
- **Total response tokens**
- **Number of requests**

#### Set Usage Limits

You can set limits to automatically stop execution when thresholds are reached:

- **Total Request Limit:**  
  Set the maximum number of requests allowed in a session.
- **Total Token Usage Limit:**  
  Set the maximum number of tokens that can be used.
- **Tool Call Timeout:**  
  Set the maximum time (in seconds) a tool call can take before being terminated.
- **Max Steps:**  
  Set the maximum number of steps the agent can take before stopping.

You can configure these in your `servers_config.json` under the `AgentConfig` section:

```json
"AgentConfig": {
    "tool_call_timeout": 30,        // Tool call timeout in seconds
    "max_steps": 15,                // Max number of steps before termination
    "request_limit": 1000,          // Max number of requests allowed
    "total_tokens_limit": 100000    // Max number of tokens allowed
}
```

- When any of these limits are reached, the agent will automatically stop running and notify you.

#### Example Commands

```bash
# Check your current API usage and limits
/api_stats

# Set a new request limit (example)
# (This can be done by editing servers_config.json or via future CLI commands)
```

## 🔧 Advanced Features

### Tool Orchestration

```python
# Example of automatic tool chaining if the tool is available in the servers connected
User: "Find charging stations near Silicon Valley and check their current status"

# Client automatically:
1. Uses Google Maps API to locate Silicon Valley
2. Searches for charging stations in the area
3. Checks station status through EV network API
4. Formats and presents results
```

### Resource Analysis

```python
# Automatic resource processing
User: "Analyze the contents of /path/to/document.pdf"

# Client automatically:
1. Identifies resource type
2. Extracts content
3. Processes through LLM
4. Provides intelligent summary
```

### Demo

![mcp_client_new1-MadewithClipchamp-ezgif com-optimize](https://github.com/user-attachments/assets/9c4eb3df-d0d5-464c-8815-8f7415a47fce)

## 🔍 Troubleshooting

> 📖 **For comprehensive configuration help**, see the [⚙️ Configuration Guide](#%EF%B8%8F-configuration-guide) section above, which covers:
>
> - Config file differences (`.env` vs `servers_config.json`)
> - Transport type selection and authentication
> - OAuth server behavior explanation
> - Common connection issues and solutions

### Common Issues and Solutions

1. **Connection Issues**

   ```bash
   Error: Could not connect to MCP server
   ```

   - Check if the server is running
   - Verify server configuration in `servers_config.json`
   - Ensure network connectivity
   - Check server logs for errors
   - **See [Transport Types & Authentication](#-transport-types--authentication) for detailed setup**

2. **API Key Issues**

   ```bash
   Error: Invalid API key
   ```

   - Verify API key is correctly set in `.env`
   - Check if API key has required permissions
   - Ensure API key is for correct environment (production/development)
   - **See [Configuration Files Overview](#configuration-files-overview) for correct setup**

3. **Redis Connection**

   ```bash
   Error: Could not connect to Redis
   ```

   - Verify Redis server is running
   - Check Redis connection settings in `.env`
   - Ensure Redis password is correct (if configured)

4. **Tool Execution Failures**
   ```bash
   Error: Tool execution failed
   ```
   - Check tool availability on connected servers
   - Verify tool permissions
   - Review tool arguments for correctness

### Debug Mode

Enable debug mode for detailed logging:

```bash
/debug
```

For additional support, please:

1. Check the [Issues](https://github.com/Abiorh001/mcp_omni_connect/issues) page
2. Review closed issues for similar problems
3. Open a new issue with detailed information if needed

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

## 📖 Documentation

Complete documentation is available at: **[MCPOmni Connect Docs](https://abiorh001.github.io/mcp_omni_connect)**

To build documentation locally:

```bash
./docs.sh serve    # Start development server at http://127.0.0.1:8080
./docs.sh build    # Build static documentation
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact & Support

- **Author**: Abiola Adeshina
- **Email**: abiolaadedayo1993@gmail.com
- **GitHub Issues**: [Report a bug](https://github.com/Abiorh001/mcp_omni_connect/issues)

---

<p align="center">Built with ❤️ by the MCPOmni Connect Team</p>
