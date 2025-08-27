# 🚀 MCPOmni Connect - Complete AI Platform: OmniAgent + Universal MCP Client

[![PyPI Downloads](https://static.pepy.tech/badge/mcpomni-connect)](https://pepy.tech/projects/mcpomni-connect)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/Abiorh001/mcp_omni_connect/actions)
[![PyPI version](https://badge.fury.io/py/mcpomni-connect.svg)](https://badge.fury.io/py/mcpomni-connect)
[![Last Commit](https://img.shields.io/github/last-commit/Abiorh001/mcp_omni_connect)](https://github.com/Abiorh001/mcp_omni_connect/commits/main)
[![Open Issues](https://img.shields.io/github/issues/Abiorh001/mcp_omni_connect)](https://github.com/Abiorh001/mcp_omni_connect/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/Abiorh001/mcp_omni_connect)](https://github.com/Abiorh001/mcp_omni_connect/pulls)

**MCPOmni Connect** is the complete AI platform that evolved from a world-class MCP client into a revolutionary ecosystem. It now includes **OmniAgent** - the ultimate AI agent builder born from MCPOmni Connect's powerful foundation. Build production-ready AI agents, use the advanced MCP CLI, or combine both for maximum power.

## 📋 Table of Contents

### 🚀 **Getting Started**
- [🚀 Quick Start (2 minutes)](#-quick-start-2-minutes)
- [🌟 What is MCPOmni Connect?](#-complete-ai-platform---two-powerful-systems)
- [💡 What Can You Build? (Examples)](#-what-can-you-build-see-real-examples)
- [🎯 Choose Your Path](#-getting-started---choose-your-path)

### 📖 **Core Information**  
- [✨ Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [🔥 Local Tools System](#-local-tools-system---create-custom-ai-tools)

### ⚙️ **Setup & Configuration**
- [⚙️ Configuration Guide](#️-configuration-guide)
- [🧠 Vector Database Setup](#-vector-database--smart-memory-setup-complete-guide)
- [📊 Tracing & Observability](#-opik-tracing--observability-setup-latest-feature)

### 🛠️ **Development & Integration**
- [🧑‍💻 Examples & Usage](#-examples)
- [🛠️ Developer Integration](#️-developer-integration)
- [🧪 Testing](#-testing)

### 📚 **Reference & Support**
- [🔍 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📖 Documentation](#-documentation)

---

## 🚀 Quick Start (2 minutes)

**New to MCPOmni Connect?** Get started in 2 minutes:

### Step 1: Install
```bash
# Install with uv (recommended)
uv add mcpomni-connect

# Or with pip
pip install mcpomni-connect
```

### Step 2: Set API Key
```bash
# Create .env file with your LLM API key
echo "LLM_API_KEY=your_openai_api_key_here" > .env
```

### Step 3: Run Examples
```bash
# Try the basic MCP client
python examples/basic.py

# Or try OmniAgent with custom tools
python examples/omni_agent_example.py

# Or use the advanced MCP CLI
python examples/run.py
```

### What Can You Build?
- **Custom AI Agents**: Register your Python functions as AI tools
- **MCP Integration**: Connect to any Model Context Protocol server
- **Smart Memory**: Vector databases for long-term AI memory
- **Background Agents**: Self-flying autonomous task execution
- **Production Monitoring**: Opik tracing for performance optimization

➡️ **Next**: Check out [Examples](#-what-can-you-build-see-real-examples) or jump to [Configuration Guide](#️-configuration-guide)

---

## 🌟 **Complete AI Platform - Two Powerful Systems:**

### 1. 🤖 **OmniAgent System** *(Revolutionary AI Agent Builder)*
Born from MCPOmni Connect's foundation - create intelligent, autonomous agents with:
- **🛠️ Local Tools System** - Register your Python functions as AI tools
- **🚁 Self-Flying Background Agents** - Autonomous task execution
- **🧠 Multi-Tier Memory** - Vector databases, Redis, PostgreSQL, MySQL, SQLite
- **📡 Real-Time Events** - Live monitoring and streaming
- **🔧 MCP + Local Tool Orchestration** - Seamlessly combine both tool types

### 2. 🔌 **Universal MCP Client** *(World-Class CLI)*
Advanced command-line interface for connecting to any Model Context Protocol server with:
- **🌐 Multi-Protocol Support** - stdio, SSE, HTTP, Docker, NPX transports
- **🔐 Authentication** - OAuth 2.0, Bearer tokens, custom headers
- **🧠 Advanced Memory** - Redis, Database, Vector storage with intelligent retrieval
- **📡 Event Streaming** - Real-time monitoring and debugging
- **🤖 Agentic Modes** - ReAct, Orchestrator, and Interactive chat modes

**🎯 Perfect for:** Developers who want the complete AI ecosystem - build custom agents AND have world-class MCP connectivity.

## 🚀 NEW: OmniAgent - Build Your Own AI Agents! 

**🌟 Introducing OmniAgent** - A revolutionary AI agent system that brings plug-and-play intelligence to your applications!

### ✅ OmniAgent Revolutionary Capabilities:
- **🧠 Multi-tier memory management** with vector search and semantic retrieval
- **🛠️ XML-based reasoning** with strict tool formatting for reliable execution  
- **🔧 Advanced tool orchestration** - Seamlessly combine MCP server tools + local tools
- **🚁 Self-flying background agents** with autonomous task execution
- **📡 Real-time event streaming** for monitoring and debugging
- **🏗️ Production-ready infrastructure** with error handling and retry logic
- **⚡ Plug-and-play intelligence** - No complex setup required!

### 🔥 **LOCAL TOOLS SYSTEM** *(MAJOR FEATURE!)*
- **🎯 Easy Tool Registration**: `@tool_registry.register_tool("tool_name")`
- **🔌 Custom Tool Creation**: Register your own Python functions as AI tools
- **🔄 Runtime Tool Management**: Add/remove tools dynamically
- **⚙️ Type-Safe Interface**: Automatic parameter validation and documentation
- **📖 Rich Examples**: Study `run_omni_agent.py` for 12+ EXAMPLE tool registration patterns

---

## 💡 **What Can You Build? (See Real Examples)**

### 🔌 **MCP Client Usage** *(Connect to MCP Servers)*
```bash
# Basic MCP client usage - Simple connection patterns
python examples/basic.py

# Advanced MCP CLI - Full-featured client interface  
python examples/run.py
```

### 🤖 **OmniAgent System** *(Build Custom AI Agents)*
```bash
# Complete OmniAgent demo - All features showcase
python examples/omni_agent_example.py

# Advanced OmniAgent patterns - Study 12+ tool examples
python examples/run_omni_agent.py
```

### 🚁 **Background Agent Automation** *(Self-Flying Agents)*
```bash
# Self-flying background agents - Autonomous task execution
python examples/background_agent_example.py
```

### 🌐 **Web Applications** *(User Interfaces)*
```bash
# FastAPI implementation - Clean API endpoints
python examples/fast_api_iml.py

# Web server with UI - Interactive interface for OmniAgent
python examples/web_server.py
# Open http://localhost:8000 for web interface
```

### 🔧 **LLM Provider Configuration** *(Multiple Providers)*
All LLM provider examples consolidated in:
```bash
# See examples/llm_usage-config.json for:
# - Anthropic Claude models
# - Groq ultra-fast inference  
# - Azure OpenAI enterprise
# - Ollama local models
# - OpenRouter 200+ models
# - And more providers...
```

---

## ✨ Key Features

> **🚀 Want to start building right away?** Jump to [Quick Start](#-quick-start-2-minutes) | [Examples](#-what-can-you-build-see-real-examples) | [Configuration](#️-configuration-guide)

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

### 💾 Advanced Memory Management *(UPDATED!)*

- **Multi-Backend Memory Storage**
  - **In-Memory**: Fast development storage
  - **Redis**: Persistent memory with real-time access
  - **Database**: PostgreSQL, MySQL, SQLite support 
  - **File Storage**: Save/load conversation history
  - Runtime switching: `/memory_store:redis`, `/memory_store:database:postgresql://user:pass@host/db`
- **Multi-Tier Memory Strategy**
  - **Short-term Memory**: Sliding window or token budget strategies
  - **Long-term Memory**: Vector database storage for semantic retrieval
  - **Episodic Memory**: Context-aware conversation history
  - Runtime configuration: `/memory_mode:sliding_window:5`, `/memory_mode:token_budget:3000`
- **Vector Database Integration *(NEW!)*
  - **Multiple Provider Support**: ChromaDB (local/remote/cloud) + Qdrant (remote)
  - **Smart Fallback**: Automatic failover to local storage if remote fails
  - **Semantic Search**: Intelligent context retrieval across conversations  
  - **Long-term & Episodic Memory**: Enable with `ENABLE_VECTOR_DB=true`
  - **⚠️ Startup Impact**: 30-60s initial load (sentence transformer), then fast
- **Real-Time Event Streaming *(NEW!)*
  - **In-Memory Events**: Fast development event processing
  - **Redis Streams**: Persistent event storage and streaming
  - Runtime switching: `/event_store:redis_stream`, `/event_store:in_memory`
- **Advanced Tracing & Observability *(LATEST!)*
  - **Opik Integration**: Production-grade tracing and monitoring
    - **Real-time Performance Tracking**: Monitor LLM calls, tool executions, and agent performance
    - **Detailed Call Traces**: See exactly where time is spent in your AI workflows
    - **System Observability**: Understand bottlenecks and optimize performance
    - **Open Source**: Built on Opik, the open-source observability platform
  - **Easy Setup**: Just add your Opik credentials to start monitoring
  - **Zero Code Changes**: Automatic tracing with `@track` decorators
  - **Performance Insights**: Identify slow operations and optimization opportunities

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

> **📚 Prefer hands-on learning?** Skip to [Examples](#-what-can-you-build-see-real-examples) or [Configuration](#️-configuration-guide)

### Core Components

```
MCPOmni Connect Platform
├── 🤖 OmniAgent System (Revolutionary Agent Builder)
│   ├── Local Tools Registry
│   ├── Background Agent Manager  
│   ├── Custom Agent Creation
│   └── Agent Orchestration Engine
├── 🔌 Universal MCP Client (World-Class CLI)
│   ├── Transport Layer (stdio, SSE, HTTP, Docker, NPX)
│   ├── Multi-Server Orchestration
│   ├── Authentication & Security
│   └── Connection Lifecycle Management
├── 🧠 Shared Memory System (Both Systems)
│   ├── Multi-Backend Storage (Redis, DB, In-Memory)
│   ├── Vector Database Integration (ChromaDB, Qdrant)
│   ├── Memory Strategies (Sliding Window, Token Budget)
│   └── Session Management
├── 📡 Event System (Both Systems)
│   ├── In-Memory Event Processing
│   ├── Redis Streams for Persistence
│   └── Real-Time Event Monitoring
├── 🛠️ Tool Management (Both Systems)
│   ├── Dynamic Tool Discovery
│   ├── Cross-Server Tool Routing
│   ├── Local Python Tool Registration
│   └── Tool Execution Engine
└── 🤖 AI Integration (Both Systems)
    ├── LiteLLM (100+ Models)
    ├── Context Management
    ├── ReAct Agent Processing
    └── Response Generation
```

## 🚀 Getting Started

### ✅ **Minimal Setup (Just Python + API Key)**

**Required:**
- Python 3.10+
- LLM API key (OpenAI, Anthropic, Groq, etc.)

**Optional (for advanced features):**
- Redis (persistent memory)
- Vector DB (Support both Qdrant and ChromaDB)
- Database (PostgreSQL/MySQL/SQLite)
- ⚠️ **Vector DB startup**: 30-60s initial load time

### 📦 **Installation**

```bash
# Option 1: UV (recommended - faster)
uv add mcpomni-connect

# Option 2: Pip (standard)
pip install mcpomni-connect
```

### ⚡ **Quick Configuration**

**Minimal setup** (get started immediately):
```bash
# Just set your API key - that's it!
echo "LLM_API_KEY=your_api_key_here" > .env
```

**Advanced setup** (optional features):
> **📖 Need more options?** See the complete [Configuration Guide](#configuration-guide) below for all environment variables, vector database setup, memory configuration, and advanced features.

### 🎯 **Choose Your Path**

**Path A: Build Custom Agents (OmniAgent)**
```bash
python examples/omni_agent_example.py
```

**Path B: Advanced MCP Client (CLI)**
```bash
python examples/run.py
```

**Path C: Web Interface**
```bash
python examples/web_server.py
# Open http://localhost:8000
```

## ⚙️ Configuration Guide

> **⚡ Quick Setup**: Only need `LLM_API_KEY` to get started! | **🔍 Detailed Setup**: [Vector DB](#-vector-database--smart-memory-setup-complete-guide) | [Tracing](#-opik-tracing--observability-setup-latest-feature)

### Environment Variables

Create a `.env` file with your configuration. **Only the LLM API key is required** - everything else is optional for advanced features.

#### **🔥 REQUIRED (Start Here)**
```bash
# ===============================================
# REQUIRED: AI Model API Key (Choose one provider)
# ===============================================
LLM_API_KEY=your_openai_api_key_here
# OR for other providers:
# LLM_API_KEY=your_anthropic_api_key_here
# LLM_API_KEY=your_groq_api_key_here
# LLM_API_KEY=your_azure_openai_api_key_here
# See examples/llm_usage-config.json for all provider configs
```

#### **⚡ OPTIONAL: Advanced Features**
```bash
# ===============================================
# Embeddings (OPTIONAL) - NEW!
# ===============================================
# For generating text embeddings (vector representations)
# Choose one provider - same key works for all embedding models
EMBEDDING_API_KEY=your_embedding_api_key_here
# OR for other providers:
# EMBEDDING_API_KEY=your_cohere_api_key_here
# EMBEDDING_API_KEY=your_huggingface_api_key_here
# EMBEDDING_API_KEY=your_mistral_api_key_here
# See docs/EMBEDDING_README.md for all provider configs

# ===============================================
# Tracing & Observability (OPTIONAL) - NEW!
# ===============================================
# For advanced monitoring and performance optimization
# 🔗 Sign up: https://www.comet.com/signup?from=llm
OPIK_API_KEY=your_opik_api_key_here
OPIK_WORKSPACE=your_opik_workspace_name

# ===============================================
# Vector Database (OPTIONAL) - Smart Memory
# ===============================================
# ⚠️ Warning: 30-60s startup time for sentence transformer
# ⚠️ IMPORTANT: You MUST choose a provider - no local fallback
ENABLE_VECTOR_DB=true # Default: false

# Choose ONE provider (required if ENABLE_VECTOR_DB=true):

# Option 1: Qdrant Remote (RECOMMENDED)
OMNI_MEMORY_PROVIDER=qdrant-remote
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Option 2: ChromaDB Remote
# OMNI_MEMORY_PROVIDER=chroma-remote
# CHROMA_HOST=localhost
# CHROMA_PORT=8000

# Option 3: ChromaDB Cloud
# OMNI_MEMORY_PROVIDER=chroma-cloud
# CHROMA_TENANT=your_tenant
# CHROMA_DATABASE=your_database
# CHROMA_API_KEY=your_api_key
# ===============================================
# Persistent Memory Storage (OPTIONAL)
# ===============================================
# These have sensible defaults - only set if you need custom configuration

# Redis - for memory_store_type="redis" (defaults to: redis://localhost:6379/0)
# REDIS_URL=redis://your-remote-redis:6379/0
# REDIS_URL=redis://:password@localhost:6379/0  # With password

# Database - for memory_store_type="database" (defaults to: sqlite:///mcpomni_memory.db)
# DATABASE_URL=postgresql://user:password@localhost:5432/mcpomni
# DATABASE_URL=mysql://user:password@localhost:3306/mcpomni
```

> **💡 Quick Start**: Just set `LLM_API_KEY` and you're ready to go! Add other variables only when you need advanced features.

### **Server Configuration (`servers_config.json`)**

For MCP server connections and agent settings:

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

Start the CLI - ensure your API key is exported or create `.env` file:

```bash
# Basic MCP client
python examples/basic.py

# Or advanced MCP CLI
python examples/run.py
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
   echo "LLM_API_KEY=your_api_key_here" > .env

   # Configure your servers in servers_config.json
   ```

3. **Start Client**

   ```bash
   uv run examples/run.py
   ```

   Or:

   ```bash
   python examples/run.py
   ```





## 🎯 **Getting Started - Choose Your Path**

### When to Use What?

| **Use Case** | **Choose** | **Best For** |
|-------------|------------|--------------|
| Build custom AI apps | **OmniAgent** | Web apps, automation, custom workflows |
| Connect to MCP servers | **MCP CLI** | Daily workflow, server management, debugging |
| Learn & experiment | **Examples** | Understanding patterns, proof of concepts |
| Production deployment | **Both** | Full-featured AI applications |

### **Path 1: 🤖 Build Custom AI Agents (OmniAgent)**
Perfect for: Custom applications, automation, web apps
```bash
# Study the examples to learn patterns:
python examples/basic.py                    # Simple MCP client
python examples/omni_agent_example.py       # Complete OmniAgent demo
python examples/background_agent_example.py # Self-flying agents
python examples/web_server.py              # Web interface

# Then build your own using the patterns!
```

### **Path 2: 🔌 Advanced MCP Client (CLI)**
Perfect for: Daily workflow, server management, debugging
```bash
# Basic MCP client - Simple connection patterns
python examples/basic.py

# World-class MCP client with advanced features
python examples/run.py

# Features: Connect to MCP servers, agentic modes, advanced memory
```

### **Path 3: 🧪 Study Tool Patterns (Learning)**
Perfect for: Learning, understanding patterns, experimentation
```bash
# Comprehensive testing interface - Study 12+ EXAMPLE tools
python examples/run_omni_agent.py --mode cli

# Study this file to see tool registration patterns and CLI features
# Contains many examples of how to create custom tools
```

**💡 Pro Tip:** Most developers use **both paths** - the MCP CLI for daily workflow and OmniAgent for building custom solutions!

---

## 🔥 Local Tools System - Create Custom AI Tools!

One of OmniAgent's most powerful features is the ability to **register your own Python functions as AI tools**. The agent can then intelligently use these tools to complete tasks.

### 🎯 Quick Tool Registration Example

```python
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry

# Create tool registry
tool_registry = ToolRegistry()

# Register your custom tools with simple decorator
@tool_registry.register_tool("calculate_area")
def calculate_area(length: float, width: float) -> str:
    """Calculate the area of a rectangle."""
    area = length * width
    return f"Area of rectangle ({length} x {width}): {area} square units"

@tool_registry.register_tool("analyze_text")
def analyze_text(text: str) -> str:
    """Analyze text and return word count and character count."""
    words = len(text.split())
    chars = len(text)
    return f"Analysis: {words} words, {chars} characters"

@tool_registry.register_tool("system_status")
def get_system_status() -> str:
    """Get current system status information."""
    import platform
    import time
    return f"System: {platform.system()}, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"

# Use tools with OmniAgent
agent = OmniAgent(
    name="my_agent",
    local_tools=tool_registry,  # Your custom tools!
    # ... other config
)

# Now the AI can use your tools!
result = await agent.run("Calculate the area of a 10x5 rectangle and tell me the current system time")
```

### 📖 Tool Registration Patterns (Create Your Own!)

**No built-in tools** - You create exactly what you need! Study these EXAMPLE patterns from `run_omni_agent.py`:

**Mathematical Tools Examples:**
```python
@tool_registry.register_tool("calculate_area")
def calculate_area(length: float, width: float) -> str:
    area = length * width
    return f"Area: {area} square units"

@tool_registry.register_tool("analyze_numbers") 
def analyze_numbers(numbers: str) -> str:
    num_list = [float(x.strip()) for x in numbers.split(",")]
    return f"Count: {len(num_list)}, Average: {sum(num_list)/len(num_list):.2f}"
```

**System Tools Examples:**
```python
@tool_registry.register_tool("system_info")
def get_system_info() -> str:
    import platform
    return f"OS: {platform.system()}, Python: {platform.python_version()}"
```

**File Tools Examples:**
```python
@tool_registry.register_tool("list_files")
def list_directory(path: str = ".") -> str:
    import os
    files = os.listdir(path)
    return f"Found {len(files)} items in {path}"
```

### 🎨 Tool Registration Patterns

**1. Simple Function Tools:**
```python
@tool_registry.register_tool("weather_check")
def check_weather(city: str) -> str:
    """Get weather information for a city."""
    # Your weather API logic here
    return f"Weather in {city}: Sunny, 25°C"
```

**2. Complex Analysis Tools:**
```python
@tool_registry.register_tool("data_analysis")
def analyze_data(data: str, analysis_type: str = "summary") -> str:
    """Analyze data with different analysis types."""
    import json
    try:
        data_obj = json.loads(data)
        if analysis_type == "summary":
            return f"Data contains {len(data_obj)} items"
        elif analysis_type == "detailed":
            # Complex analysis logic
            return "Detailed analysis results..."
    except:
        return "Invalid data format"
```

**3. File Processing Tools:**
```python
@tool_registry.register_tool("process_file")
def process_file(file_path: str, operation: str) -> str:
    """Process files with different operations."""
    try:
        if operation == "read":
            with open(file_path, 'r') as f:
                content = f.read()
            return f"File content (first 100 chars): {content[:100]}..."
        elif operation == "count_lines":
            with open(file_path, 'r') as f:
                lines = len(f.readlines())
            return f"File has {lines} lines"
    except Exception as e:
        return f"Error processing file: {e}"
```

---



### 🧠 **Vector Database & Smart Memory Setup** *(COMPLETE GUIDE)*

MCPOmni Connect provides advanced memory capabilities through vector databases for intelligent, semantic search and long-term memory.

#### **⚡ Quick Start (Choose Your Provider)**
```bash
# Enable vector memory - you MUST choose a provider
ENABLE_VECTOR_DB=true

# Option 1: Qdrant (recommended)
OMNI_MEMORY_PROVIDER=qdrant-remote
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Option 2: ChromaDB Remote
OMNI_MEMORY_PROVIDER=chroma-remote
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

#### **⚠️ Important: Startup Time Impact**
- **Vector DB disabled**: ~1-2 seconds startup
- **Vector DB enabled**: ~30-60 seconds startup (sentence transformer model loading)
- **Memory usage**: ~2-4GB (includes sentence transformer model)
- **Recommendation**: Enable during development setup, then it's fast for all subsequent usage

#### **🔧 Vector Database Providers**

**1. Qdrant Remote (Recommended Default)**
```bash
# Install and run Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Configure
ENABLE_VECTOR_DB=true
OMNI_MEMORY_PROVIDER=qdrant-remote
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

**2. ChromaDB Remote**
```bash
# Install and run ChromaDB server
docker run -p 8000:8000 chromadb/chroma

# Configure
ENABLE_VECTOR_DB=true
OMNI_MEMORY_PROVIDER=chroma-remote
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

**3. ChromaDB Cloud**
```bash
ENABLE_VECTOR_DB=true
OMNI_MEMORY_PROVIDER=chroma-cloud
CHROMA_TENANT=your_tenant
CHROMA_DATABASE=your_database
CHROMA_API_KEY=your_api_key
```

#### **⚠️ Important: No Local Fallback**
- **Local ChromaDB support has been removed** for performance reasons
- **You must configure a vector database provider** - no automatic fallback
- **If no provider is configured or fails**: Vector DB will be disabled
- **This ensures fast startup** when vector DB is not needed

#### **✨ What You Get**
- **Long-term Memory**: Persistent storage across sessions
- **Episodic Memory**: Context-aware conversation history
- **Semantic Search**: Find relevant information by meaning, not exact text
- **Multi-session Context**: Remember information across different conversations
- **Automatic Summarization**: Intelligent memory compression for efficiency



### 📊 **Opik Tracing & Observability Setup** *(LATEST FEATURE!)*

**Monitor and optimize your AI agents with production-grade observability:**

#### **🚀 Quick Setup**

1. **Sign up for Opik** (Free & Open Source):
   - Visit: **[https://www.comet.com/signup?from=llm](https://www.comet.com/signup?from=llm)**
   - Create your account and get your API key and workspace name

2. **Add to your `.env` file** (see [Environment Variables](#environment-variables) above):
   ```bash
   OPIK_API_KEY=your_opik_api_key_here
   OPIK_WORKSPACE=your_opik_workspace_name
   ```

#### **✨ What You Get Automatically**

Once configured, MCPOmni Connect automatically tracks:

- **🔥 LLM Call Performance**: Execution time, token usage, response quality
- **🛠️ Tool Execution Traces**: Which tools were used and how long they took
- **🧠 Memory Operations**: Vector DB queries, memory retrieval performance
- **🤖 Agent Workflow**: Complete trace of multi-step agent reasoning
- **📊 System Bottlenecks**: Identify exactly where time is spent

#### **📈 Benefits**

- **Performance Optimization**: See which LLM calls or tools are slow
- **Cost Monitoring**: Track token usage and API costs
- **Debugging**: Understand agent decision-making processes
- **Production Monitoring**: Real-time observability for deployed agents
- **Zero Code Changes**: Works automatically with existing agents

#### **🔍 Example: What You'll See**

```
Agent Execution Trace:
├── agent_execution: 4.6s
│   ├── tools_registry_retrieval: 0.02s ✅
│   ├── memory_retrieval_step: 0.08s ✅
│   ├── llm_call: 4.5s ⚠️ (bottleneck identified!)
│   ├── response_parsing: 0.01s ✅
│   └── action_execution: 0.03s ✅
```

**💡 Pro Tip**: Opik is completely optional. If you don't set the credentials, MCPOmni Connect works normally without tracing.

### 🖥️ Updated CLI Commands *(NEW!)*

**Memory Store Management:**
```bash
# Switch between memory backends
/memory_store:in_memory                    # Fast in-memory storage (default)
/memory_store:redis                        # Redis persistent storage  
/memory_store:database                     # SQLite database storage
/memory_store:database:postgresql://user:pass@host/db  # PostgreSQL
/memory_store:database:mysql://user:pass@host/db       # MySQL

# Memory strategy configuration
/memory_mode:sliding_window:10             # Keep last 10 messages
/memory_mode:token_budget:5000             # Keep under 5000 tokens
```

**Event Store Management:**
```bash
# Switch between event backends
/event_store:in_memory                     # Fast in-memory events (default)
/event_store:redis_stream                  # Redis Streams for persistence
```

**Enhanced Commands:**
```bash
# Memory operations
/history                                   # Show conversation history
/clear_history                            # Clear conversation history
/save_history <file>                      # Save history to file
/load_history <file>                      # Load history from file

# Server management
/add_servers:<config.json>                # Add servers from config
/remove_server:<server_name>              # Remove specific server
/refresh                                  # Refresh server capabilities

# Debugging and monitoring
/debug                                    # Toggle debug mode
/api_stats                               # Show API usage statistics
```

---

### 🚀 MCPOmni Connect CLI - World-Class MCP Client

The MCPOmni Connect CLI is the most advanced MCP client available, providing professional-grade MCP functionality with enhanced memory, event management, and agentic modes:

```bash
# Launch the advanced MCP CLI
python examples/run.py

# Core MCP client commands:
/tools                                    # List all available tools
/prompts                                  # List all available prompts  
/resources                               # List all available resources
/prompt:<name>                           # Execute a specific prompt
/resource:<uri>                          # Read a specific resource
/subscribe:<uri>                         # Subscribe to resource updates
/query <your_question>                   # Ask questions using tools

# Advanced platform features:
/memory_store:redis                      # Switch to Redis memory
/event_store:redis_stream               # Switch to Redis events
/add_servers:<config.json>              # Add MCP servers dynamically
/remove_server:<name>                   # Remove MCP server
/mode:auto                              # Switch to autonomous agentic mode
/mode:orchestrator                      # Switch to multi-server orchestration
  ```

## 🛠️ Developer Integration

MCPOmni Connect is not just a CLI tool—it's also a powerful Python library. **OmniAgent consolidates everything** - you no longer need to manually manage MCP clients, configurations, and agents separately!

### Build Apps with OmniAgent *(Recommended)*

**OmniAgent automatically includes MCP client functionality** - just specify your MCP servers and you're ready to go:

```python
from mcpomni_connect.omni_agent import OmniAgent
from mcpomni_connect.memory_store.memory_router import MemoryRouter
from mcpomni_connect.events.event_router import EventRouter
from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry

# Create tool registry for custom tools
tool_registry = ToolRegistry()

@tool_registry.register_tool("analyze_data")
def analyze_data(data: str) -> str:
    """Analyze data and return insights."""
    return f"Analysis complete: {len(data)} characters processed"

# OmniAgent automatically handles MCP connections + your tools
agent = OmniAgent(
    name="my_app_agent",
    system_instruction="You are a helpful assistant with access to MCP servers and custom tools.",
    model_config={
        "provider": "openai", 
        "model": "gpt-4o",
        "temperature": 0.7
    },
    # Your custom local tools
    local_tools=tool_registry,
    # MCP servers - automatically connected!
    mcp_tools=[
        {
            "name": "filesystem",
            "transport_type": "stdio", 
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home"]
        },
        {
            "name": "github",
            "transport_type": "streamable_http",
            "url": "http://localhost:8080/mcp",
            "headers": {"Authorization": "Bearer your-token"}
        }
    ],
    memory_store=MemoryRouter(memory_store_type="redis"),
    event_router=EventRouter(event_store_type="in_memory")
)

# Use in your app - gets both MCP tools AND your custom tools!
result = await agent.run("List files in the current directory and analyze the filenames")
```

### Legacy Manual Approach *(Not Recommended)*

If you need the old manual approach for some reason:

### FastAPI Integration with OmniAgent

OmniAgent makes building APIs incredibly simple. See [`examples/web_server.py`](examples/web_server.py) for a complete FastAPI example:

```python
from fastapi import FastAPI
from mcpomni_connect.omni_agent import OmniAgent

app = FastAPI()
agent = OmniAgent(...)  # Your agent setup from above

@app.post("/chat")
async def chat(message: str, session_id: str = None):
    result = await agent.run(message, session_id)
    return {"response": result['response'], "session_id": result['session_id']}

@app.get("/tools") 
async def get_tools():
    # Returns both MCP tools AND your custom tools automatically
    return agent.get_available_tools()
```

**Key Benefits:**

- **One OmniAgent = MCP + Custom Tools + Memory + Events**
- **Automatic tool discovery** from all connected MCP servers
- **Built-in session management** and conversation history
- **Real-time event streaming** for monitoring
- **Easy integration** with any Python web framework

---

### Server Configuration Examples

> **💡 Quick Reference**: See `examples/llm_usage-config.json` for all LLM provider configurations (Anthropic, Groq, Azure, Ollama, OpenRouter, etc.)

#### Basic OpenAI Configuration

```json
{
  "AgentConfig": {
    "tool_call_timeout": 30,
    "max_steps": 15,
    "request_limit": 0,          // 0 = unlimited (production mode), set > 0 to enable limits
    "total_tokens_limit": 0,     // 0 = unlimited (production mode), set > 0 to enable limits
    "memory_results_limit": 5,   // Number of memory results to retrieve (1-100, default: 5)
    "memory_similarity_threshold": 0.5  // Similarity threshold for memory filtering (0.0-1.0, default: 0.5)
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
    "request_limit": 0,          // 0 = unlimited (production mode), set > 0 to enable limits
    "total_tokens_limit": 0,     // 0 = unlimited (production mode), set > 0 to enable limits
    "memory_results_limit": 5,   // Number of memory results to retrieve (1-100, default: 5)
    "memory_similarity_threshold": 0.5  // Similarity threshold for memory filtering (0.0-1.0, default: 0.5)
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

> **🚨 Most Common Issues**: Check [Quick Fixes](#-quick-fixes-common-issues) below first!
> 
> **📖 For comprehensive setup help**: See [⚙️ Configuration Guide](#️-configuration-guide) | [🧠 Vector DB Setup](#-vector-database--smart-memory-setup-complete-guide)

### 🚨 **Quick Fixes (Common Issues)**

| **Error** | **Quick Fix** |
|-----------|---------------|
| `Error: Invalid API key` | Check your `.env` file: `LLM_API_KEY=your_actual_key` |
| `ModuleNotFoundError: mcpomni_connect` | Run: `uv add mcpomni-connect` or `pip install mcpomni-connect` |
| `Connection refused` | Ensure MCP server is running before connecting |
| `ChromaDB not available` | Install: `pip install chromadb` - [See Vector DB Setup](#-vector-database--smart-memory-setup-complete-guide) |
| `Redis connection failed` | Install Redis or use in-memory mode (default) |
| `Tool execution failed` | Check tool permissions and arguments |

### Detailed Issues and Solutions

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

### **Getting Help**

1. **First**: Check the [Quick Fixes](#-quick-fixes-common-issues) above
2. **Examples**: Study working examples in the `examples/` directory
3. **Issues**: Search [GitHub Issues](https://github.com/Abiorh001/mcp_omni_connect/issues) for similar problems
4. **New Issue**: [Create a new issue](https://github.com/Abiorh001/mcp_omni_connect/issues/new) with detailed information

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
