# 🚀 OmniCoreAgent - Complete AI Development Platform

> **ℹ️ Project Renaming Notice:**  
> This project was previously known as **`mcp_omni-connect`**.  
> It has been renamed to **`omnicoreagent`** to reflect its evolution into a complete AI development platform—combining both a world-class MCP client and a powerful AI agent builder framework.

> **⚠️ Breaking Change:**  
> The package name has changed from **`mcp_omni-connect`** to **`omnicoreagent`**.  
> Please uninstall the old package and install the new one:
>
> ```bash
> pip uninstall mcp_omni-connect
> pip install omnicoreagent
> ```
>
> All imports and CLI commands now use `omnicoreagent`.  
> Update your code and scripts accordingly.

[![PyPI Downloads](https://static.pepy.tech/badge/omnicoreagent)](https://pepy.tech/projects/omnicoreagent)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/Abiorh001/omnicoreagent/actions)
[![PyPI version](https://badge.fury.io/py/omnicoreagent.svg)](https://badge.fury.io/py/omnicoreagent)
[![Last Commit](https://img.shields.io/github/last-commit/Abiorh001/omnicoreagent)](https://github.com/Abiorh001/omnicoreagent/commits/main)
[![Open Issues](https://img.shields.io/github/issues/Abiorh001/omnicoreagent)](https://github.com/Abiorh001/omnicoreagent/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/Abiorh001/omnicoreagent)](https://github.com/Abiorh001/omnicoreagent/pulls)

<p align="center">
  <img src="Gemini_Generated_Image_pfgm65pfgm65pfgmcopy.png" alt="OmniCoreAgent Logo" width="250"/>
</p>

**OmniCoreAgent** is the complete AI development platform that combines two powerful systems into one revolutionary ecosystem. Build production-ready AI agents with **OmniAgent**, use the advanced MCP client with **MCPOmni Connect**, or combine both for maximum power.

## 📋 Table of Contents

### 🚀 **Getting Started**
- [🚀 Quick Start (2 minutes)](#-quick-start-2-minutes)
- [🌟 What is OmniCoreAgent?](#-what-is-omnicoreagent)
- [💡 What Can You Build? (Examples)](#-what-can-you-build-see-real-examples)
- [🎯 Choose Your Path](#-choose-your-path)
- [🧠 Semantic Tool Knowledge Base](#-semantic-tool-knowledge-base)

### 🤖 **OmniAgent System**

- [✨ OmniAgent Features](#-omniagent---revolutionary-ai-agent-builder)
- [🔥 Local Tools System](#-local-tools-system---create-custom-ai-tools)
- [🧩 OmniAgent Workflow System](#-omniagent-workflow-system--multi-agent-orchestration)
- [🚁 Background Agent System](#-background-agent-system---autonomous-task-automation)
- [🛠️ Building Custom Agents](#-building-custom-agents)
- [📚 OmniAgent Examples](#-omniagent-examples)

### 🔌 **MCPOmni Connect System**
- [✨ MCP Client Features](#-mcpomni-connect---world-class-mcp-client)
- [🚦 Transport Types & Authentication](#-transport-types--authentication)
- [🖥️ CLI Commands](#️-cli-commands)
- [📚 MCP Usage Examples](#-mcp-usage-examples)

### 📖 **Core Information**
- [✨ Platform Features](#-platform-features)
- [🏗️ Architecture](#️-architecture)

### ⚙️ **Setup & Configuration**
- [⚙️ Configuration Guide](#️-configuration-guide)
- [🧠 Vector Database Setup](#-vector-database--smart-memory-setup-complete-guide)
- [📊 Tracing & Observability](#-opik-tracing--observability-setup-latest-feature)

### 🛠️ **Development & Integration**
- [🧑‍💻 Developer Integration](#-developer-integration)
- [🧪 Testing](#-testing)

### 📚 **Reference & Support**
- [🔍 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📖 Documentation](#-documentation)

---

**New to OmniCoreAgent?** Get started in 2 minutes:

### Step 1: Install
```bash
# Install with uv (recommended)
uv add omnicoreagent

# Or with pip
pip install omnicoreagent
```

### Step 2: Set API Key
```bash
# Create .env file with your LLM API key
echo "LLM_API_KEY=your_openai_api_key_here" > .env
```

### Step 3: Run Examples
```bash
# Try OmniAgent with custom tools
python examples/omni_agent_example.py

# Try MCPOmni Connect (MCP client)
python examples/run_mcp.py

# Try the integrated platform
python examples/run_omni_agent.py
```

### What Can You Build?
- **Custom AI Agents**: Register your Python functions as AI tools with OmniAgent
- **MCP Integration**: Connect to any Model Context Protocol server with MCPOmni Connect
- **Smart Memory**: Vector databases for long-term AI memory
- **Background Agents**: Self-flying autonomous task execution
- **Production Monitoring**: Opik tracing for performance optimization

➡️ **Next**: Check out [Examples](#-what-can-you-build-see-real-examples) or jump to [Configuration Guide](#️-configuration-guide)

---

## 🌟 **What is OmniCoreAgent?**

OmniCoreAgent is a comprehensive AI development platform consisting of two integrated systems:

### 1. 🤖 **OmniAgent** *(Revolutionary AI Agent Builder)*
Create intelligent, autonomous agents with custom capabilities:
- **🛠️ Local Tools System** - Register your Python functions as AI tools
- **🚁 Self-Flying Background Agents** - Autonomous task execution
- **🧠 Multi-Tier Memory** - Vector databases, Redis, PostgreSQL, MySQL, SQLite
- **📡 Real-Time Events** - Live monitoring and streaming
- **🔧 MCP + Local Tool Orchestration** - Seamlessly combine both tool types

### 2. 🔌 **MCPOmni Connect** *(World-Class MCP Client)*
Advanced command-line interface for connecting to any Model Context Protocol server with:
- **🌐 Multi-Protocol Support** - stdio, SSE, HTTP, Docker, NPX transports
- **🔐 Authentication** - OAuth 2.0, Bearer tokens, custom headers
- **🧠 Advanced Memory** - Redis, Database, Vector storage with intelligent retrieval
- **📡 Event Streaming** - Real-time monitoring and debugging
- **🤖 Agentic Modes** - ReAct, Orchestrator, and Interactive chat modes

**🎯 Perfect for:** Developers who want the complete AI ecosystem - build custom agents AND have world-class MCP connectivity.

---

## 💡 **What Can You Build? (See Real Examples)**

### 🤖 **OmniAgent System** *(Build Custom AI Agents)*
```bash
# Complete OmniAgent demo - All features showcase
python examples/omni_agent_example.py

# Advanced OmniAgent patterns - Study 12+ tool examples
python examples/run_omni_agent.py

# Self-flying background agents - Autonomous task execution with Background Agent Manager
python examples/background_agent_example.py


# Web server with UI - Interactive interface for OmniAgent
python examples/web_server.py
# Open http://localhost:8000 for web interface

# FastAPI implementation - Clean API endpoints
python examples/fast_api_impl.py

# Enhanced web server - Production-ready with advanced features
python examples/enhanced_web_server.py
```

### 🔌 **MCPOmni Connect System** *(Connect to MCP Servers)*
```bash
# Basic MCP client usage
python examples/run_mcp.py

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

## 🎯 **Choose Your Path**

### When to Use What?

| **Use Case** | **Choose** | **Best For** |
|-------------|------------|--------------|
| Build custom AI apps | **OmniAgent** | Web apps, automation, custom workflows |
| Connect to MCP servers | **MCPOmni Connect** | Daily workflow, server management, debugging |
| Learn & experiment | **Examples** | Understanding patterns, proof of concepts |
| Production deployment | **Both** | Full-featured AI applications |

### **Path 1: 🤖 Build Custom AI Agents (OmniAgent)**
Perfect for: Custom applications, automation, web apps
```bash
# Study the examples to learn patterns:
python examples/basic.py                    # Simple introduction
python examples/omni_agent_example.py       # Complete OmniAgent demo
python examples/background_agent_example.py # Self-flying agents
python examples/web_server.py              # Web interface
python examples/fast_api_impl.py           # FastAPI integration
python examples/enhanced_web_server.py    # Production-ready web server

# Then build your own using the patterns!
```

### **Path 2: 🔌 Advanced MCP Client (MCPOmni Connect)**
Perfect for: Daily workflow, server management, debugging
```bash
# Basic MCP client
python examples/run_mcp.py


# Features: Connect to MCP servers, agentic modes, advanced memory
```

### **Path 3: 🧪 Study Tool Patterns (Learning)**
Perfect for: Learning, understanding patterns, experimentation
```bash
# Comprehensive testing interface - Study 12+ EXAMPLE tools
python examples/run_omni_agent.py 

# Study this file to see tool registration patterns and CLI features
# Contains many examples of how to create custom tools
```

**💡 Pro Tip:** Most developers use **both paths** - MCPOmni Connect for daily workflow and OmniAgent for building custom solutions!

---

## 🧠 **Semantic Tool Knowledge Base**

### Why You Need It

As your AI agents grow and connect to more MCP servers, finding the right tool quickly becomes challenging. Relying on static lists or manual selection is slow, inflexible, and can overload your agent’s context window—making it harder for the agent to choose the best tool for each task.

The **Semantic Tool Knowledge Base** solves this by automatically embedding all available tools into a vector database. This enables your agent to use semantic search: it can instantly and intelligently retrieve the most relevant tools based on the meaning of your query, not just keywords. As your tool ecosystem expands, the agent always finds the best match—no manual updates or registry management

### Usefulness

- **Scalable Tool Discovery:** Connect unlimited MCP servers and tools; the agent finds what it needs, when it needs it.
- **Context-Aware Retrieval:** The agent uses semantic similarity to select tools that best match the user’s intent, not just keywords.
- **Unified Access:** All tools are accessible via a single `tools_retriever` interface, simplifying agent logic.
- **Fallback Reliability:** If semantic search fails, the agent falls back to fast keyword (BM25) search for robust results.
- **No Manual Registry:** Tools are automatically indexed and updated—no need to maintain a static list.

---

### How to Enable

Add these options to your agent config:

```json
"agent_config": {
    "enable_tools_knowledge_base": true,      // Enable semantic tool KB, default: false
    "tools_results_limit": 10,                // Max tools to retrieve per query
    "tools_similarity_threshold": 0.1,        // Similarity threshold for semantic search
    ...
}
```

When enabled, all MCP server tools are embedded into your chosen vector DB (Qdrant, ChromaDB, MongoDB, etc.) and standard DB. The agent uses `tools_retriever` to fetch tools at runtime.

---

### Example Usage

```python
agent = OmniAgent(
    ...,
    agent_config={
        "enable_tools_knowledge_base": True,
        "tools_results_limit": 10,
        "tools_similarity_threshold": 0.1,
        # other config...
    },
    ...
)
```

---

### Benefits Recap

- **Instant access to thousands of tools**
- **Context-aware, semantic selection**
- **No manual registry management**
- **Reliable fallback search**
- **Scales with your infrastructure**

---

**Note:** Choose your vector DB provider via environment variables. See [Vector Database Setup](#-vector-database--smart-memory-setup-complete-guide)
---

# 🤖 OmniAgent - Revolutionary AI Agent Builder

**🌟 Introducing OmniAgent** - A revolutionary AI agent system that brings plug-and-play intelligence to your applications!

## ✅ OmniAgent Revolutionary Capabilities:
- **🧠 Multi-tier memory management** with vector search and semantic retrieval
- **🛠️ XML-based reasoning** with strict tool formatting for reliable execution  
- **🔧 Advanced tool orchestration** - Seamlessly combine MCP server tools + local tools
- **🚁 Self-flying background agents** with autonomous task execution
- **📡 Real-time event streaming** for monitoring and debugging
- **🏗️ Production-ready infrastructure** with error handling and retry logic
- **⚡ Plug-and-play intelligence** - No complex setup required!

## 🔥 **LOCAL TOOLS SYSTEM** - Create Custom AI Tools!

One of OmniAgent's most powerful features is the ability to **register your own Python functions as AI tools**. The agent can then intelligently use these tools to complete tasks.

### 🎯 Quick Tool Registration Example

```python
from omnicoreagent.omni_agent import OmniAgent
from omnicoreagent.core.tools.local_tools_registry import ToolRegistry

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

## 🛠️ Building Custom Agents

### Basic Agent Setup

```python
from omnicoreagent.omni_agent import OmniAgent
from omnicoreagent.core.memory_store.memory_router import MemoryRouter
from omnicoreagent.core.events.event_router import EventRouter
from omnicoreagent.core.tools.local_tools_registry import ToolRegistry

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
    agent_config={
        "tool_call_timeout": 30,
        "max_steps": 10,
        "request_limit": 0,          # 0 = unlimited (production mode), set > 0 to enable limits
        "total_tokens_limit": 0,     # 0 = unlimited (production mode), set > 0 to enable limits
        "memory_results_limit": 5,   # Number of memory results to retrieve (1-100, default: 5)
        "memory_similarity_threshold": 0.5  # Similarity threshold for memory filtering (0.0-1.0, default: 0.5)
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
    embedding_config={
        "provider": "openai",
        "model": "text-embedding-3-small",
        "dimensions": 1536,
        "encoding_format": "float",
    },
    memory_store=MemoryRouter(memory_store_type="redis"),
    event_router=EventRouter(event_store_type="in_memory")
)

# Use in your app - gets both MCP tools AND your custom tools!
result = await agent.run("List files in the current directory and analyze the filenames")
```

## 🧩 **OmniAgent Workflow System** – Multi Agent Orchestration

OmniCoreAgent now includes a powerful **workflow system** for orchestrating multiple agents in your application.  
You can choose from three workflow agents, each designed for different orchestration patterns:

- **SequentialAgent** – Chain agents step-by-step, passing output from one to the next.
- **ParallelAgent** – Run multiple agents concurrently, each with its own task.
- **RouterAgent** – Use an intelligent router agent to select the best sub-agent for a given task.

All three workflow agents are available in the `omni_agent/workflow/` directory, and usage examples are provided in the `examples/` folder.

---

### 🤖 **SequentialAgent** – Step-by-Step Agent Chaining

**Purpose:**  
Run a list of agents in sequence, passing the output of each agent as the input to the next.  
This is ideal for multi-stage processing pipelines, where each agent performs a specific transformation or analysis.

**How it works:**

- You provide a list of `OmniAgent` instances.
- The first agent receives the initial query (or uses its system instruction if no query is provided).
- Each agent’s output is passed as the input to the next agent.
- The same session ID is used for all agents, ensuring shared context and memory.

**Example Usage:**

```python
from omnicoreagent.omni_agent.workflow.sequential_agent import SequentialAgent

# Create your agents (see examples/ for full setup)
agents = [agent1, agent2, agent3]

seq_agent = SequentialAgent(sub_agents=agents)
await seq_agent.initialize()
result = await seq_agent.run(initial_task="Analyze this data and summarize results")
print(result)
```

**Typical Use Cases:**

- Data preprocessing → analysis → reporting
- Multi-step document processing
- Chained reasoning tasks

---

### ⚡ **ParallelAgent** – Concurrent Agent Execution

**Purpose:**  
Run multiple agents at the same time, each with its own task or system instruction.  
This is perfect for scenarios where you want to gather results from several agents independently and quickly.

**How it works:**

- You provide a list of `OmniAgent` instances.
- Optionally, you can specify a dictionary of tasks for each agent (`agent_name: task`). If no task is provided, the agent uses its system instruction.
- All agents are run concurrently, sharing the same session ID for context.
- Results are returned as a dictionary mapping agent names to their outputs.

**Example Usage:**

```python
from omnicoreagent.omni_agent.workflow.parallel_agent import ParallelAgent

agents = [agent1, agent2, agent3]
tasks = {
    "agent1": "Summarize this article",
    "agent2": "Extract keywords",
    "agent3": None  # Uses system instruction
}

par_agent = ParallelAgent(sub_agents=agents)
await par_agent.initialize()
results = await par_agent.run(agent_tasks=tasks)
print(results)
```

**Typical Use Cases:**

- Running multiple analyses on the same data
- Gathering different perspectives or answers in parallel
- Batch processing with independent agents

---

### 🧠 **RouterAgent** – Intelligent Task Routing

**Purpose:**  
Automatically select the most suitable agent for a given task using LLM-powered reasoning and XML-based decision making.  
The RouterAgent analyzes the user’s query and agent capabilities, then routes the task to the best-fit agent.

**How it works:**

- You provide a list of `OmniAgent` instances and configuration for the router.
- The RouterAgent builds a registry of agent capabilities (using system instructions and available tools).
- When a task is received, the RouterAgent uses its internal LLM to select the best agent and forwards the task.
- The selected agent executes the task and returns the result.

**Example Usage:**

```python
from omnicoreagent.omni_agent.workflow.router_agent import RouterAgent

agents = [agent1, agent2, agent3]
router = RouterAgent(
    sub_agents=agents,
    model_config={...},
    agent_config={...},
    memory_router=...,
    event_router=...,
    debug=True
)
await router.initialize()
result = await router.run(task="Find and summarize recent news about AI")
print(result)
```

**Typical Use Cases:**

- Dynamic agent selection based on user query
- Multi-domain assistants (e.g., code, data, research)
- Intelligent orchestration in complex workflows

---

### 📚 **Workflow Agent Examples**

See the `examples/` directory for ready-to-run demos of each workflow agent:

- `examples/sequential_agent.py`
- `examples/parallel_agent.py`
- `examples/router_agent.py`

Each example shows how to set up agents, configure workflows, and process results.

---

### 🛠️ **How to Choose?**

| Workflow Agent   | Best For                                      |
|------------------|-----------------------------------------------|
| SequentialAgent  | Multi-stage pipelines, step-by-step tasks     |
| ParallelAgent    | Fast batch processing, independent analyses   |
| RouterAgent      | Smart routing, dynamic agent selection        |

You can combine these workflow agents for advanced orchestration patterns in your AI applications.

---

**Ready to build?**  
Explore the examples, study the API, and start orchestrating powerful multi-agent workflows with OmniCoreAgent!

## 🚁 Background Agent System - Autonomous Task Automation

The Background Agent System is one of OmniAgent's most powerful features, providing fully autonomous task execution with intelligent lifecycle management. Background agents run independently, executing scheduled tasks without human intervention.

### ✨ Background Agent Features

- **🔄 Autonomous Execution** - Agents run independently in the background
- **⏰ Flexible Scheduling** - Time-based, interval-based, and cron-style scheduling
- **🧠 Full OmniAgent Capabilities** - Access to all local tools and MCP servers
- **📊 Lifecycle Management** - Create, update, pause, resume, and delete agents
- **🔧 Background Agent Manager** - Central control system for all background agents
- **📡 Real-Time Monitoring** - Track agent status and execution results
- **🛠️ Task Management** - Update tasks, schedules, and configurations dynamically

### 🔧 Background Agent Manager

The Background Agent Manager handles the complete lifecycle of background agents:

#### **Core Capabilities:**
- **Create New Agents** - Deploy autonomous agents with custom tasks
- **Update Agent Tasks** - Modify agent instructions and capabilities dynamically
- **Schedule Management** - Update timing, intervals, and execution schedules
- **Agent Control** - Start, stop, pause, and resume agents
- **Health Monitoring** - Track agent status and performance
- **Resource Management** - Manage agent memory and computational resources

#### **Scheduler Support:**
- **APScheduler** *(Current)* - Advanced Python task scheduling
  - Cron-style scheduling
  - Interval-based execution
  - Date-based scheduling
  - Timezone support
- **Future Roadmap**:
  - **RabbitMQ** - Message queue-based task distribution
  - **Redis Pub/Sub** - Event-driven agent communication
  - **Celery** - Distributed task execution
  - **Kubernetes Jobs** - Container-based agent deployment

### 🎯 Background Agent Usage Examples

#### **1. Basic Background Agent Creation**

```python
from omnicoreagent import (
    OmniAgent,
    MemoryRouter,
    EventRouter,
    BackgroundAgentManager,
    ToolRegistry,
    logger,
)

# Initialize the background agent service
memory_router = MemoryRouter(memory_store_type="redis")
event_router = EventRouter(event_store_type="redis_stream")
bg_service = BackgroundAgentService(memory_router, event_router)

# Start the background agent manager
bg_service.start_manager()

# Create tool registry for the background agent
tool_registry = ToolRegistry()

@tool_registry.register_tool("monitor_system")
def monitor_system() -> str:
    """Monitor system resources and status."""
    import psutil
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    return f"System Status - CPU: {cpu}%, Memory: {memory}%"

# Configure the background agent
agent_config = {
    "agent_id": "system_monitor",
    "system_instruction": "You are a system monitoring agent. Check system resources and send alerts when thresholds are exceeded.",
    "model_config": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.3
    },
    "agent_config": {
        "max_steps": 10,
        "tool_call_timeout": 60
    },
    "interval": 300,  # 5 minutes in seconds
    "task_config": {
        "query": "Monitor system resources and send alerts if CPU > 80% or Memory > 90%",
        "schedule": "every 5 minutes",
        "interval": 300,
        "max_retries": 2,
        "retry_delay": 30
    },
    "local_tools": tool_registry
}

# Create and deploy background agent
result = await bg_service.create(agent_config)
print(f"Background agent '{agent_config['agent_id']}' created successfully!")
print(f"Details: {result}")
```

#### **4. Web Application Integration**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Request models for API
class BackgroundAgentRequest(BaseModel):
    agent_id: str
    query: str = None
    schedule: str = None

class TaskUpdateRequest(BaseModel):
    agent_id: str
    query: str

# FastAPI integration
app = FastAPI()

# Initialize background service
@app.on_event("startup")
async def startup():
    memory_router = MemoryRouter(memory_store_type="redis")
    event_router = EventRouter(event_store_type="redis_stream")
    app.state.bg_service = BackgroundAgentService(memory_router, event_router)
    app.state.bg_service.start_manager()

@app.on_event("shutdown")
async def shutdown():
    app.state.bg_service.shutdown_manager()

# API endpoints (same as shown in REST API section above)
@app.post("/api/background/create")
async def create_background_agent(payload: BackgroundAgentRequest):
    # Parse schedule to interval seconds
    def parse_schedule(schedule_str: str) -> int:
        import re
        if not schedule_str:
            return 3600  # Default 1 hour
        
        # Try parsing as raw number
        try:
            return max(1, int(schedule_str))
        except:
            pass
        
        # Parse text patterns
        text = schedule_str.lower().strip()
        
        # Match patterns like "5 minutes", "every 30 seconds", etc.
        patterns = [
            (r"(\d+)(?:\s*)(second|sec|s)s?", 1),
            (r"(\d+)(?:\s*)(minute|min|m)s?", 60),
            (r"(\d+)(?:\s*)(hour|hr|h)s?", 3600),
            (r"every\s+(\d+)\s+(second|sec|s)s?", 1),
            (r"every\s+(\d+)\s+(minute|min|m)s?", 60),
            (r"every\s+(\d+)\s+(hour|hr|h)s?", 3600)
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                return max(1, value * multiplier)
        
        return 3600  # Default fallback

    interval_seconds = parse_schedule(payload.schedule)
    
    agent_config = {
        "agent_id": payload.agent_id,
        "system_instruction": f"You are a background agent that performs: {payload.query}",
        "model_config": {
            "provider": "openai", 
            "model": "gpt-4o-mini", 
            "temperature": 0.3
        },
        "agent_config": {
            "max_steps": 10, 
            "tool_call_timeout": 60
        },
        "interval": interval_seconds,
        "task_config": {
            "query": payload.query,
            "schedule": payload.schedule or "immediate",
            "interval": interval_seconds,
            "max_retries": 2,
            "retry_delay": 30
        },
        "local_tools": build_tool_registry()  # Your custom tools
    }
    
    details = await app.state.bg_service.create(agent_config)
    app.state.bg_service.start_manager()
    
    return {
        "status": "success",
        "agent_id": payload.agent_id,
        "message": "Background agent created",
        "details": details
    }
```

#### **3. Agent Lifecycle Management**

```python
# List all background agents
agent_ids = bg_service.list()
print(f"Active agents: {len(agent_ids)}")
print(f"Agent IDs: {agent_ids}")

# Get detailed agent information
for agent_id in agent_ids:
    status = bg_service.get_agent_status(agent_id)
    print(f"""
Agent: {agent_id}
├── Running: {status.get('is_running', False)}
├── Scheduled: {status.get('scheduled', False)}
├── Query: {status.get('task_config', {}).get('query', 'N/A')}
├── Schedule: {status.get('task_config', {}).get('schedule', 'N/A')}
├── Interval: {status.get('task_config', {}).get('interval', 'N/A')}s
└── Session ID: {bg_service.manager.get_agent_session_id(agent_id)}
""")

# Update agent task
success = bg_service.update_task_config(
    agent_id="system_monitor",
    task_config={
        "query": "Monitor system resources and also check disk space. Alert if disk usage > 85%",
        "max_retries": 3,
        "retry_delay": 60
    }
)
print(f"Task update success: {success}")

# Agent control operations
bg_service.pause_agent("system_monitor")   # Pause scheduling
print("Agent paused")

bg_service.resume_agent("system_monitor")  # Resume scheduling
print("Agent resumed")

bg_service.stop_agent("system_monitor")    # Stop execution
print("Agent stopped")

bg_service.start_agent("system_monitor")   # Start execution
print("Agent started")

# Remove agent task permanently
success = bg_service.remove_task("system_monitor")
print(f"Task removal success: {success}")

# Get manager status
manager_status = bg_service.get_manager_status()
print(f"Manager status: {manager_status}")

# Connect MCP servers for agent (if configured)
await bg_service.connect_mcp("system_monitor")
print("MCP servers connected")

# Shutdown entire manager
bg_service.shutdown_manager()
print("Background agent manager shutdown")
```

#### **4. Background Agent with MCP Integration**

```python
# Background agent with both local tools and MCP servers
web_scraper_agent = await manager.create_agent(
    agent_id="web_scraper",
    task="Scrape news websites hourly, analyze sentiment, and store results",
    schedule={
        "type": "interval",
        "hours": 1
    },
    local_tools=tool_registry,  # Your custom tools
    mcp_tools=[  # MCP server connections
        {
            "name": "web_scraper",
            "transport_type": "stdio",
            "command": "npx",
            "args": ["-y", "@mcp/server-web-scraper"]
        },
        {
            "name": "database",
            "transport_type": "streamable_http",
            "url": "http://localhost:8080/mcp",
            "headers": {"Authorization": "Bearer db-token"}
        }
    ],
    system_instruction="You are a web scraping agent. Scrape news sites, analyze sentiment, and store results in the database."
)
```

### 🛠️ Background Agent Manager API

The BackgroundAgentService provides a comprehensive API for managing background agents:

#### **Agent Creation & Configuration**
```python
# Create new background agent
result = await bg_service.create(agent_config: dict)

# Agent configuration structure
agent_config = {
    "agent_id": "unique_agent_id",
    "system_instruction": "Agent role and behavior description",
    "model_config": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.3
    },
    "agent_config": {
        "max_steps": 10,
        "tool_call_timeout": 60
    },
    "interval": 300,  # Execution interval in seconds
    "task_config": {
        "query": "Main task description",
        "schedule": "human-readable schedule (e.g., 'every 5 minutes')",
        "interval": 300,
        "max_retries": 2,
        "retry_delay": 30
    },
    "local_tools": tool_registry,  # Optional custom tools
    "mcp_tools": mcp_server_configs  # Optional MCP server connections
}
```

#### **Agent Lifecycle Management**
```python
# Start the background agent manager
bg_service.start_manager()

# Agent control operations
bg_service.start_agent(agent_id: str)      # Start agent execution
bg_service.stop_agent(agent_id: str)       # Stop agent execution
bg_service.pause_agent(agent_id: str)      # Pause agent scheduling
bg_service.resume_agent(agent_id: str)     # Resume agent scheduling

# Shutdown manager (stops all agents)
bg_service.shutdown_manager()
```

#### **Agent Monitoring & Status**
```python
# List all agents
agent_ids = bg_service.list()  # Returns list of agent IDs

# Get specific agent status
status = bg_service.get_agent_status(agent_id: str)
# Returns: {
#     "is_running": bool,
#     "scheduled": bool,
#     "task_config": dict,
#     "session_id": str,
#     # ... other status info
# }

# Get manager status
manager_status = bg_service.get_manager_status()
```

#### **Task Management**
```python
# Update agent task configuration
success = bg_service.update_task_config(
    agent_id: str, 
    task_config: dict
)

# Remove agent task completely
success = bg_service.remove_task(agent_id: str)
```

#### **MCP Server Management**
```python
# Connect MCP servers for specific agent
await bg_service.connect_mcp(agent_id: str)
```

### 🌐 REST API Endpoints

The Background Agent system can be integrated into web applications with these REST endpoints:

#### **Agent Management Endpoints**
```bash
# Create new background agent
POST /api/background/create
{
    "agent_id": "system_monitor",
    "query": "Monitor system resources and alert on high usage",
    "schedule": "every 5 minutes"
}

# List all background agents
GET /api/background/list
# Returns: {
#   "status": "success",
#   "agents": [
#     {
#       "agent_id": "system_monitor",
#       "query": "Monitor system resources...",
#       "is_running": true,
#       "scheduled": true,
#       "schedule": "every 5 minutes",
#       "interval": 300,
#       "session_id": "session_123"
#     }
#   ]
# }
```

#### **Agent Control Endpoints**
```bash
# Start agent
POST /api/background/start
{"agent_id": "system_monitor"}

# Stop agent
POST /api/background/stop
{"agent_id": "system_monitor"}

# Pause agent
POST /api/background/pause
{"agent_id": "system_monitor"}

# Resume agent
POST /api/background/resume
{"agent_id": "system_monitor"}
```

#### **Task Management Endpoints**
```bash
# Update agent task
POST /api/task/update
{
    "agent_id": "system_monitor",
    "query": "Updated task description"
}

# Remove agent task
DELETE /api/task/remove/{agent_id}
```

#### **Status & Monitoring Endpoints**
```bash
# Get manager status
GET /api/background/status

# Get specific agent status
GET /api/background/status/{agent_id}

# Connect MCP servers for agent
POST /api/background/mcp/connect
{"agent_id": "system_monitor"}
```

#### **Event Streaming Endpoints**
```bash
# Get events for session
GET /api/events?session_id=session_123

# Stream real-time events
GET /api/events/stream/{session_id}
# Returns Server-Sent Events stream
```

### 📋 Schedule Parsing

The Background Agent system includes intelligent schedule parsing:

```python
# Flexible schedule input formats:
"300"                    # 300 seconds
"5 minutes"             # 5 minutes
"2 hours"               # 2 hours
"every 30 seconds"      # Every 30 seconds
"every 10 minutes"      # Every 10 minutes
"every 2 hours"         # Every 2 hours

# All converted to interval seconds automatically
# Minimum interval: 1 second
```

### 📅 Scheduling Configuration

The Background Agent system currently supports interval-based scheduling with intelligent parsing:

#### **Interval-Based Scheduling (Current Implementation)**
```python
# Schedule configuration in agent_config
agent_config = {
    "interval": 300,  # Execution interval in seconds
    "task_config": {
        "schedule": "every 5 minutes",  # Human-readable description
        "interval": 300,               # Same value in seconds
        "max_retries": 2,
        "retry_delay": 30
    }
}

# Flexible schedule input formats supported:
"300"                    # 300 seconds
"5 minutes"             # 5 minutes → 300 seconds
"2 hours"               # 2 hours → 7200 seconds
"30 seconds"            # 30 seconds
"every 30 seconds"      # Every 30 seconds
"every 10 minutes"      # Every 10 minutes → 600 seconds
"every 2 hours"         # Every 2 hours → 7200 seconds

# All automatically converted to interval seconds
# Minimum interval: 1 second
```

#### **Schedule Parsing Logic**
The system intelligently parses various schedule formats:
- **Raw numbers**: `"300"` → 300 seconds
- **Unit expressions**: `"5 minutes"` → 300 seconds
- **Every patterns**: `"every 10 minutes"` → 600 seconds
- **Supported units**: seconds (s/sec), minutes (m/min), hours (h/hr)

#### **Future Scheduling Features (Planned)**
```python
# Coming with future scheduler backends:
schedule = {
    "type": "cron",
    "cron": "0 9 * * 1-5",    # Weekdays at 9 AM
    "timezone": "UTC"
}

schedule = {
    "type": "date",
    "run_date": "2024-03-15 14:30:00",
    "timezone": "UTC"
}
```

### 🔄 Background Agent States

Background agents can be in different states managed by the Background Agent Manager:

- **`CREATED`** - Agent created but not yet started
- **`RUNNING`** - Agent is active and executing according to schedule
- **`PAUSED`** - Agent is temporarily stopped but retains configuration
- **`STOPPED`** - Agent execution stopped but agent still exists
- **`ERROR`** - Agent encountered an error during execution
- **`DELETED`** - Agent permanently removed

### 📊 Monitoring & Observability

#### **Real-Time Status Monitoring**
```python
# Get comprehensive agent status
status = await manager.get_agent_status("system_monitor")

print(f"""
Agent Status Report:
├── ID: {status['agent_id']}
├── Name: {status['name']}
├── State: {status['state']}
├── Last Run: {status['last_run']}
├── Next Run: {status['next_run']}
├── Success Rate: {status['success_rate']}%
├── Total Executions: {status['total_runs']}
├── Failed Executions: {status['failed_runs']}
└── Average Duration: {status['avg_duration']}s
""")
```

#### **Execution History**
```python
# Get detailed execution history
history = await manager.get_execution_history("system_monitor", limit=5)

for execution in history:
    print(f"""
Execution {execution['execution_id']}:
├── Start Time: {execution['start_time']}
├── Duration: {execution['duration']}s
├── Status: {execution['status']}
├── Result: {execution['result'][:100]}...
└── Tools Used: {execution['tools_used']}
""")
```

### 🚀 Future Scheduler Support

The Background Agent Manager is designed to support multiple scheduling backends:

#### **Current Support**
- **APScheduler** - Full-featured Python task scheduling
  - In-memory scheduler
  - Persistent job storage
  - Multiple trigger types
  - Timezone support

#### **Planned Future Support**
- **RabbitMQ** - Message queue-based task distribution
  - Distributed agent execution
  - Load balancing across workers
  - Reliable message delivery
  - Dead letter queues for failed tasks

- **Redis Pub/Sub** - Event-driven agent communication
  - Real-time event processing
  - Agent-to-agent communication
  - Scalable event distribution
  - Pattern-based subscriptions

- **Celery** - Distributed task queue
  - Horizontal scaling
  - Result backends
  - Task routing and priority
  - Monitoring and management tools

- **Kubernetes Jobs** - Container-based agent deployment
  - Cloud-native scaling
  - Resource management
  - Job persistence and recovery
  - Integration with CI/CD pipelines

### 📋 Background Agent Configuration

#### **Complete Configuration Example**
```python
# Comprehensive background agent setup
background_agent = await manager.create_agent(
    agent_id="comprehensive_agent",
    name="Comprehensive Background Agent",
    task="Monitor APIs, process data, and generate reports",
    
    # Scheduling configuration
    schedule={
        "type": "cron",
        "cron": "0 */6 * * *",  # Every 6 hours
        "timezone": "UTC"
    },
    
    # AI model configuration
    model_config={
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 2000
    },
    
    # Agent behavior configuration
    agent_config={
        "tool_call_timeout": 60,
        "max_steps": 20,
        "request_limit": 100,
        "total_tokens_limit": 10000,
        "memory_results_limit": 10,
        "memory_similarity_threshold": 0.7
    },
    
    # Custom tools
    local_tools=tool_registry,
    
    # MCP server connections
    mcp_tools=[
        {
            "name": "api_monitor",
            "transport_type": "streamable_http",
            "url": "http://localhost:8080/mcp",
            "headers": {"Authorization": "Bearer api-token"}
        }
    ],
    
    # Agent personality
    system_instruction="You are an autonomous monitoring agent. Execute tasks efficiently and report any issues.",
    
    # Memory and events
    memory_store=MemoryRouter(memory_store_type="redis"),
    event_router=EventRouter(event_store_type="redis_stream")
)
```

### 🔄 Error Handling & Recovery

Background agents include robust error handling:

```python
# Automatic retry configuration
agent_config = {
    "max_retries": 3,           # Retry failed executions
    "retry_delay": 60,          # Wait 60 seconds between retries
    "failure_threshold": 5,     # Pause agent after 5 consecutive failures
    "recovery_mode": "auto"     # Auto-resume after successful execution
}

# Error monitoring
try:
    result = await agent.execute_task()
except BackgroundAgentException as e:
    # Handle agent-specific errors
    await manager.handle_agent_error(agent_id, e)
```

### 📡 Event Integration

Background agents integrate with the event system for real-time monitoring:

```python
# Subscribe to background agent events
event_router = EventRouter(event_store_type="redis_stream")

# Listen for agent events
async for event in event_router.subscribe("background_agent.*"):
    if event.type == "agent_started":
        print(f"Agent {event.data['agent_id']} started execution")
    elif event.type == "agent_completed":
        print(f"Agent {event.data['agent_id']} completed task")
    elif event.type == "agent_failed":
        print(f"Agent {event.data['agent_id']} failed: {event.data['error']}")
```

### Basic Agent Usage
```bash
# Complete OmniAgent demo with custom tools
python examples/omni_agent_example.py

# Advanced patterns with 12+ tool examples
python examples/run_omni_agent.py
```

### Background Agents
```bash
# Self-flying autonomous agents
python examples/background_agent_example.py
```

### Web Applications
```bash
# FastAPI integration
python examples/fast_api_impl.py

# Full web interface
python examples/web_server.py
# Open http://localhost:8000
```

---

# 🔌 MCPOmni Connect - World-Class MCP Client

The MCPOmni Connect system is the most advanced MCP client available, providing professional-grade MCP functionality with enhanced memory, event management, and agentic modes.

## ✨ MCPOmni Connect Key Features

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

## 🚦 Transport Types & Authentication

MCPOmni Connect supports multiple ways to connect to MCP servers:

### 1. **stdio** - Direct Process Communication

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

### 2. **sse** - Server-Sent Events

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

### 3. **streamable_http** - HTTP with Optional OAuth

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

## 🖥️ CLI Commands

### Memory Store Management:
```bash
# Switch between memory backends
/memory_store:in_memory                    # Fast in-memory storage (default)
/memory_store:redis                        # Redis persistent storage  
/memory_store:database                     # SQLite database storage
/memory_store:database:postgresql://user:pass@host/db  # PostgreSQL
/memory_store:database:mysql://user:pass@host/db       # MySQL
/memory_store:mongodb                      # Mongodb persistent storage
/memory_store:mongodb:your_mongodb_connection_string   # Mongodb with custom URI

# Memory strategy configuration
/memory_mode:sliding_window:10             # Keep last 10 messages
/memory_mode:token_budget:5000             # Keep under 5000 tokens
```

### Event Store Management:
```bash
# Switch between event backends
/event_store:in_memory                     # Fast in-memory events (default)
/event_store:redis_stream                  # Redis Streams for persistence
```

### Core MCP Operations:
```bash
/tools                                    # List all available tools
/prompts                                  # List all available prompts  
/resources                               # List all available resources
/prompt:<name>                           # Execute a specific prompt
/resource:<uri>                          # Read a specific resource
/subscribe:<uri>                         # Subscribe to resource updates
/query <your_question>                   # Ask questions using tools
```

### Enhanced Commands:
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

# Agentic modes
/mode:auto                              # Switch to autonomous agentic mode
/mode:orchestrator                      # Switch to multi-server orchestration
/mode:chat                              # Switch to interactive chat mode

# Debugging and monitoring
/debug                                    # Toggle debug mode
/api_stats                               # Show API usage statistics
```

## 📚 MCP Usage Examples

### Basic MCP Client
```bash
# Launch the basic MCP client
python examples/basic_mcp.py
```

### Advanced MCP CLI
```bash
# Launch the advanced MCP CLI
python examples/run_mcp.py

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

---

## ✨ Platform Features

> **🚀 Want to start building right away?** Jump to [Quick Start](#-quick-start-2-minutes) | [Examples](#-what-can-you-build-see-real-examples) | [Configuration](#️-configuration-guide)

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

### 💾 Advanced Memory Management

- **Multi-Backend Memory Storage**
  - **In-Memory**: Fast development storage
  - **Redis**: Persistent memory with real-time access
  - **Database**: PostgreSQL, MySQL, SQLite support 
  - **Mongodb**: NoSQL document storage
  - **File Storage**: Save/load conversation history
  - Runtime switching: `/memory_store:redis`, `/memory_store:database:postgresql://user:pass@host/db`
- **Multi-Tier Memory Strategy**
  - **Short-term Memory**: Sliding window or token budget strategies
  - **Long-term Memory**: Vector database storage for semantic retrieval
  - **Episodic Memory**: Context-aware conversation history
  - Runtime configuration: `/memory_mode:sliding_window:5`, `/memory_mode:token_budget:3000`
- **Vector Database Integration**
  - **Multiple Provider Support**: Mongodb atlas, ChromaDB (remote/cloud), and Qdrant (remote)
  - **Smart Fallback**: Automatic failover to local storage if remote fails
  - **Semantic Search**: Intelligent context retrieval across conversations  
  - **Long-term & Episodic Memory**: Enable with `ENABLE_VECTOR_DB=true`
  
- **Real-Time Event Streaming**
  - **In-Memory Events**: Fast development event processing
  - **Redis Streams**: Persistent event storage and streaming
  - Runtime switching: `/event_store:redis_stream`, `/event_store:in_memory`
- **Advanced Tracing & Observability**
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
OmniCoreAgent Platform
├── 🤖 OmniAgent System (Revolutionary Agent Builder)
│   ├── Local Tools Registry
│   ├── Background Agent Manager (Lifecycle Management)
│   │   ├── Agent Creation & Deployment
│   │   ├── Task & Schedule Updates
│   │   ├── Agent Control (Start/Stop/Pause/Resume)
│   │   ├── Health Monitoring & Status Tracking
│   │   └── Scheduler Integration (APScheduler + Future: RabbitMQ, Redis Pub/Sub)
│   ├── Custom Agent Creation
│   └── Agent Orchestration Engine
├── 🔌 MCPOmni Connect System (World-Class MCP Client)
│   ├── Transport Layer (stdio, SSE, HTTP, Docker, NPX)
│   ├── Multi-Server Orchestration
│   ├── Authentication & Security
│   └── Connection Lifecycle Management
├── 🧠 Shared Memory System (Both Systems)
│   ├── Multi-Backend Storage (Redis, DB, In-Memory)
│   ├── Vector Database Integration (ChromaDB, Qdrant, MongoDB)
│   ├── Memory Strategies (Sliding Window, Token Budget)
│   └── Session Management
├── 📡 Event System (Both Systems)
│   ├── In-Memory Event Processing
│   ├── Redis Streams for Persistence
│   ├── Real-Time Event Monitoring
│   └── Background Agent Event Broadcasting
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

---

## 📦 Installation

### ✅ **Minimal Setup (Just Python + API Key)**

**Required:**
- Python 3.10+
- LLM API key (OpenAI, Anthropic, Groq, etc.)

**Optional (for advanced features):**
- Redis (persistent memory)
- Vector DB (Support Qdrant, ChromaDB, Mongodb atlas)
- Database (PostgreSQL/MySQL/SQLite)
- Opik account (for tracing/observability)

### 📦 **Installation**

```bash
# Option 1: UV (recommended - faster)
uv add omnicoreagent

# Option 2: Pip (standard)
pip install omnicoreagent
```

### ⚡ **Quick Configuration**

**Minimal setup** (get started immediately):
```bash
# Just set your API key - that's it!
echo "LLM_API_KEY=your_api_key_here" > .env
```

**Advanced setup** (optional features):
> **📖 Need more options?** See the complete [Configuration Guide](#️-configuration-guide) below for all environment variables, vector database setup, memory configuration, and advanced features.

---

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

# Option 4: MongoDB Atlas
# OMNI_MEMORY_PROVIDER=mongodb-remote
# MONGODB_URI="your_mongodb_connection_string"
# MONGODB_DB_NAME="db name"

# ===============================================
# Persistent Memory Storage (OPTIONAL)
# ===============================================
# These have sensible defaults - only set if you need custom configuration

# Redis - for memory_store_type="redis" (defaults to: redis://localhost:6379/0)
# REDIS_URL=redis://your-remote-redis:6379/0
# REDIS_URL=redis://:password@localhost:6379/0  # With password


# DATABASE_URL=sqlite:///omnicoreagent_memory.db
# DATABASE_URL=postgresql://user:password@localhost:5432/omnicoreagent
# DATABASE_URL=mysql://user:password@localhost:3306/omnicoreagent

# Mongodb - for memory_store_type="mongodb" (defaults to: mongodb://localhost:27017/omnicoreagent)
MONGODB_URI="your_mongodb_connection_string"
MONGODB_DB_NAME="db name"
```

> **💡 Quick Start**: Just set `LLM_API_KEY` and you're ready to go! Add other variables only when you need advanced features.

### **Server Configuration (`servers_config.json`)**

For MCP server connections and agent settings:

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
  "Embedding": {
    "provider": "openai",
    "model": "text-embedding-3-small",
    "dimensions": 1536,
    "encoding_format": "float"
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

#### Multiple Provider Examples

**Anthropic Claude Configuration**
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

**Groq Configuration**
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

**Azure OpenAI Configuration**
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

**Ollama Local Model Configuration**
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

**OpenRouter Configuration**
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

OmniCoreAgent supports multiple authentication methods for secure server connections:

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

OmniCoreAgent supports dynamic server configuration through commands:

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

---

## 🧠 Vector Database & Smart Memory Setup (Complete Guide)

OmniCoreAgent provides advanced memory capabilities through vector databases for intelligent, semantic search and long-term memory.

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

# Option 3: ChromaDB Cloud
OMNI_MEMORY_PROVIDER=chroma-cloud
CHROMA_TENANT=your_tenant
CHROMA_DATABASE=your_database
CHROMA_API_KEY=your_api_key

# Option 4: MongoDB Atlas
OMNI_MEMORY_PROVIDER=mongodb-remote
MONGODB_URI="your_mongodb_connection_string"
MONGODB_DB_NAME="db name"

# Disable vector memory (default)
ENABLE_VECTOR_DB=false
```

#### **🔧 Vector Database Providers**

**1. Qdrant Remote**
```bash
# Install and run Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Configure
ENABLE_VECTOR_DB=true
OMNI_MEMORY_PROVIDER=qdrant-remote
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

**2. MongoDB Atlas**
```bash
# Configure
ENABLE_VECTOR_DB=true
OMNI_MEMORY_PROVIDER=mongodb-remote
MONGODB_URI="your_mongodb_connection_string"
MONGODB_DB_NAME="db name"
```

**3. ChromaDB Remote**
```bash
# Install and run ChromaDB server
docker run -p 8000:8000 chromadb/chroma

# Configure
ENABLE_VECTOR_DB=true
OMNI_MEMORY_PROVIDER=chroma-remote
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

**4. ChromaDB Cloud**
```bash
ENABLE_VECTOR_DB=true
OMNI_MEMORY_PROVIDER=chroma-cloud
CHROMA_TENANT=your_tenant
CHROMA_DATABASE=your_database
CHROMA_API_KEY=your_api_key
```

#### **✨ What You Get**
- **Long-term Memory**: Persistent storage across sessions
- **Episodic Memory**: Context-aware conversation history
- **Semantic Search**: Find relevant information by meaning, not exact text
- **Multi-session Context**: Remember information across different conversations
- **Automatic Summarization**: Intelligent memory compression for efficiency

---

## 📊 Opik Tracing & Observability Setup (Latest Feature)

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

Once configured, OmniCoreAgent automatically tracks:

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

**💡 Pro Tip**: Opik is completely optional. If you don't set the credentials, OmniCoreAgent works normally without tracing.

---

## 🧑‍💻 Developer Integration

OmniCoreAgent is not just a CLI tool—it's also a powerful Python library. Both systems can be used programmatically in your applications.

### Using OmniAgent in Applications

```python
from omnicoreagent.omni_agent import OmniAgent
from omnicoreagent.core.memory_store.memory_router import MemoryRouter
from omnicoreagent.core.events.event_router import EventRouter
from omnicoreagent.core.tools.local_tools_registry import ToolRegistry

# Create tool registry for custom tools
tool_registry = ToolRegistry()

@tool_registry.register_tool("analyze_data")
def analyze_data(data: str) -> str:
    """Analyze data and return insights."""
    return f"Analysis complete: {len(data)} characters processed"

# OmniAgent automatically handles MCP connections + your tools
agent = OmniAgent(
    name="my_app_agent",
    system_instruction="You are a helpful assistant.",
    model_config={
        "provider": "openai", 
        "model": "gpt-4o",
        "temperature": 0.7
    },
    local_tools=tool_registry,  # Your custom tools!
    memory_store=MemoryRouter(memory_store_type="redis"),
    event_router=EventRouter(event_store_type="in_memory")
)

# Use in your app
result = await agent.run("Analyze some sample data")
```

### FastAPI Integration with OmniAgent

OmniAgent makes building APIs incredibly simple. See [`examples/web_server.py`](examples/web_server.py) for a complete FastAPI example:

```python
from fastapi import FastAPI
from omnicoreagent.omni_agent import OmniAgent

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

### Using MCPOmni Connect Programmatically

```python
from omnicoreagent.mcp_client import MCPClient

# Create MCP client
client = MCPClient(config_file="servers_config.json")

# Connect to servers
await client.connect_all()

# Use tools
tools = await client.list_tools()
result = await client.call_tool("tool_name", {"arg": "value"})
```

**Key Benefits:**

- **One OmniAgent = MCP + Custom Tools + Memory + Events**
- **Automatic tool discovery** from all connected MCP servers
- **Built-in session management** and conversation history
- **Real-time event streaming** for monitoring
- **Easy integration** with any Python web framework

---

## 🎯 Usage Patterns

### Interactive Commands

- `/tools` - List all available tools across servers
- `/prompts` - View available prompts
- `/prompt:<n>/<args>` - Execute a prompt with arguments
- `/resources` - List available resources
- `/resource:<uri>` - Access and analyze a resource
- `/debug` - Toggle debug mode
- `/refresh` - Update server capabilities
- `/memory` - Toggle Redis memory persistence (on/off)
- `/mode:auto` - Switch to autonomous agentic mode
- `/mode:chat` - Switch back to interactive chat mode
- `/add_servers:<config.json>` - Add one or more servers from a configuration file
- `/remove_server:<server_n>` - Remove a server by its name

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

OmniCoreAgent provides advanced controls and visibility over your API usage and resource limits.

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

- **Total Request Limit:** Set the maximum number of requests allowed in a session.
- **Total Token Usage Limit:** Set the maximum number of tokens that can be used.
- **Tool Call Timeout:** Set the maximum time (in seconds) a tool call can take before being terminated.
- **Max Steps:** Set the maximum number of steps the agent can take before stopping.

You can configure these in your `servers_config.json` under the `AgentConfig` section:

```json
"AgentConfig": {
    "agent_name": "OmniAgent",              // Unique agent identifier
    "tool_call_timeout": 30,                // Tool call timeout in seconds
    "max_steps": 15,                        // Max number of reasoning/tool steps before termination

    // --- Limits ---
    "request_limit": 0,                     // 0 = unlimited (production mode), set > 0 to enable limits
    "total_tokens_limit": 0,                // 0 = unlimited (production mode), set > 0 for hard cap on tokens

    // --- Memory Retrieval Config ---
    "memory_config": {
        "mode": "sliding_window",           // Options: sliding_window, episodic, vector
        "value": 100                        // Window size or parameter value depending on mode
    },
    "memory_results_limit": 5,              // Number of memory results to retrieve (1–100, default: 5)
    "memory_similarity_threshold": 0.5,     // Similarity threshold for memory filtering (0.0–1.0, default: 0.5)

    // --- Tool Retrieval Config ---
    "enable_tools_knowledge_base": false,   // Enable semantic tool retrieval (default: false)
    "tools_results_limit": 10,              // Max number of tools to retrieve (default: 10)
    "tools_similarity_threshold": 0.1       // Similarity threshold for tool retrieval (0.0–1.0, default: 0.1)
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
   Solution: Start your MCP server first, then connect with OmniCoreAgent
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

---

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
├── omni_agent/     # OmniAgent system tests
├── mcp_client/     # MCPOmni Connect system tests
└── integration/    # Integration tests for both systems
```

### Development Quick Start

1. **Installation**

   ```bash
   # Clone the repository
   git clone https://github.com/Abiorh001/omnicoreagent.git
   cd omnicoreagent

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

3. **Start Systems**

   ```bash
   # Try OmniAgent
   uv run examples/omni_agent_example.py

   # Or try MCPOmni Connect
   uv run examples/mcp_client_example.py
   ```

   Or:

   ```bash
   python examples/omni_agent_example.py
   python examples/mcp_client_example.py
   ```

---

## 🔍 Troubleshooting

> **🚨 Most Common Issues**: Check [Quick Fixes](#-quick-fixes-common-issues) below first!
> 
> **📖 For comprehensive setup help**: See [⚙️ Configuration Guide](#️-configuration-guide) | [🧠 Vector DB Setup](#-vector-database--smart-memory-setup-complete-guide)

### 🚨 **Quick Fixes (Common Issues)**

| **Error** | **Quick Fix** |
|-----------|---------------|
| `Error: Invalid API key` | Check your `.env` file: `LLM_API_KEY=your_actual_key` |
| `ModuleNotFoundError: omnicoreagent` | Run: `uv add omnicoreagent` or `pip install omnicoreagent` |
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
   - **See [Configuration Guide](#️-configuration-guide) for correct setup**

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

5. **Vector Database Issues**

   ```bash
   Error: Vector database connection failed
   ```

   - Ensure chosen provider (Qdrant, ChromaDB, MongoDB) is running
   - Check connection settings in `.env`
   - Verify API keys for cloud providers
   - **See [Vector Database Setup](#-vector-database--smart-memory-setup-complete-guide) for detailed configuration**

6. **Import Errors**

   ```bash
   ImportError: cannot import name 'OmniAgent'
   ```

   - Check package installation: `pip show omnicoreagent`
   - Verify Python version compatibility (3.10+)
   - Try reinstalling: `pip uninstall omnicoreagent && pip install omnicoreagent`

### Debug Mode

Enable debug mode for detailed logging:

```bash
# In MCPOmni Connect
/debug

# In OmniAgent
agent = OmniAgent(..., debug=True)
```

### **Getting Help**

1. **First**: Check the [Quick Fixes](#-quick-fixes-common-issues) above
2. **Examples**: Study working examples in the `examples/` directory
3. **Issues**: Search [GitHub Issues](https://github.com/Abiorh001/omnicoreagent/issues) for similar problems
4. **New Issue**: [Create a new issue](https://github.com/Abiorh001/omnicoreagent/issues/new) with detailed information

---

## 🤝 Contributing

We welcome contributions to OmniCoreAgent! Here's how you can help:

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/abiorh001/omnicoreagent.git
cd omnicoreagent

# Set up development environment
uv venv
source .venv/bin/activate
uv sync --dev

# Install pre-commit hooks
pre-commit install
```

### Contribution Areas

- **OmniAgent System**: Custom agents, local tools, background processing
- **MCPOmni Connect**: MCP client features, transport protocols, authentication
- **Shared Infrastructure**: Memory systems, vector databases, event handling
- **Documentation**: Examples, tutorials, API documentation
- **Testing**: Unit tests, integration tests, performance tests

### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with tests
3. Run the test suite: `pytest tests/ -v`
4. Update documentation as needed
5. Submit a pull request with a clear description

### Code Standards

- Python 3.10+ compatibility
- Type hints for all public APIs
- Comprehensive docstrings
- Unit tests for new functionality
- Follow existing code style

---

## 📖 Documentation

Complete documentation is available at: **[OmniCoreAgent Docs](https://abiorh001.github.io/omnicoreagent)**

### Documentation Structure

- **Getting Started**: Quick setup and first steps
- **OmniAgent Guide**: Custom agent development
- **MCPOmni Connect Guide**: MCP client usage
- **API Reference**: Complete code documentation
- **Examples**: Working code examples
- **Advanced Topics**: Vector databases, tracing, production deployment

### Build Documentation Locally

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material

# Serve documentation locally
mkdocs serve
# Open http://127.0.0.1:8000

# Build static documentation
mkdocs build
```

### Contributing to Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add new examples or use cases
- Improve existing tutorials
- Translate to other languages

---

## Demo

![omnicoreagent-demo-MadewithClipchamp-ezgif com-optimize](https://github.com/user-attachments/assets/9c4eb3df-d0d5-464c-8815-8f7415a47fce)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact & Support

- **Author**: Abiola Adeshina
- **Email**: abiolaadedayo1993@gmail.com
- **GitHub**: [https://github.com/Abiorh001/omnicoreagent](https://github.com/Abiorh001/omnicoreagent)
- **Issues**: [Report a bug or request a feature](https://github.com/Abiorh001/omnicoreagent/issues)
- **Discussions**: [Join the community](https://github.com/Abiorh001/omnicoreagent/discussions)

### Support Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community support
- **Email**: Direct contact for partnership or enterprise inquiries

---

<p align="center">
  <strong>Built with ❤️ by the OmniCoreAgent Team</strong><br>
  <em>Empowering developers to build the next generation of AI applications</em>
</p>