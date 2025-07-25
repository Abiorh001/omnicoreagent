# OmniAgent Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    OMNIGENT FRAMEWORK                                           │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│  │   USER INTERFACE│    │   CLI INTERFACE │    │  API GATEWAY    │    │  WEB INTERFACE  │      │
│  │                 │    │                 │    │                 │    │                 │      │
│  └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘      │
│            │                      │                      │                      │              │
│            └──────────────────────┼──────────────────────┼──────────────────────┘              │
│                                   │                      │                                     │
│                                   ▼                      ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                              ORCHESTRATOR AGENT                                            │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │ │
│  │  │   Agent Router  │  │  Context Manager│  │  Tool Registry  │  │  Event Emitter  │        │ │
│  │  │                 │  │                 │  │                 │  │                 │        │ │
│  │  └─────────┬───────┘  └─────────┬───────┘  └─────────┬───────┘  └─────────┬───────┘        │ │
│  │            │                    │                    │                    │                │ │
│  └────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────┘ │
│               │                    │                    │                    │                  │
│               ▼                    ▼                    ▼                    ▼                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│  │   BASE AGENTS   │    │  MEMORY STORE   │    │   TOOL SYSTEM   │    │  EVENT SYSTEM   │      │
│  │                 │    │                 │    │                 │    │                 │      │
│  └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘      │
│            │                      │                      │                      │              │
│            ▼                      ▼                      ▼                      ▼              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│  │ • React Agent   │    │ • In-Memory     │    │ • MCP Tools     │    │ • In-Memory     │      │
│  │ • Custom Agents │    │ • Redis Memory  │    │ • Local Tools   │    │ • Redis Streams │      │
│  │ • Specialized   │    │ • Database      │    │ • Tool Discovery│    │ • Event Router  │      │
│  │   Agents        │    │ • Memory Router │    │ • Tool Cache    │    │ • Event Store   │      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘      │
│                                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                              MEMORY MANAGEMENT SYSTEM                                          │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│  │  SHORT-TERM     │    │   EPISODIC      │    │   LONG-TERM     │    │   VECTOR DB     │      │
│  │   MEMORY        │    │   MEMORY        │    │   MEMORY        │    │   (QDRANT)      │      │
│  │                 │    │                 │    │                 │    │                 │      │
│  │ • Session-based │    │ • Event-based   │    │ • Pattern-based │    │ • Semantic      │      │
│  │ • In-memory     │    │ • 30-min window │    │ • Cross-session │    │   Search        │      │
│  │ • Fast access   │    │ • LLM processed │    │ • LLM processed │    │ • Nomic         │      │
│  │ • Context       │    │ • Background    │    │ • Background    │    │   Embeddings    │      │
│  │   preservation  │    │   processing    │    │   processing    │    │ • 768-dim       │      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘      │
│                                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                              TOOL INTEGRATION SYSTEM                                           │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│  │   MCP TOOLS     │    │   LOCAL TOOLS   │    │   TOOL CACHE    │    │   TOOL SECURITY │      │
│  │                 │    │                 │    │                 │    │                 │      │
│  │ • Standardized  │    │ • Custom tools  │    │ • Performance   │    │ • Sandboxed     │      │
│  │   protocol      │    │ • Python-based  │    │   optimization  │    │   execution     │      │
│  │ • Multi-provider│    │ • Async support │    │ • Result caching│    │ • Permission    │      │
│  │ • Tool discovery│    │ • Error handling│    │ • TTL management│    │   management    │      │
│  │ • Auto-registry │    │ • Type safety   │    │ • Memory usage  │    │ • Input/output  │      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘      │
│                                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                              EVENT STREAMING SYSTEM                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│  │   EVENT TYPES   │    │   EVENT STORE   │    │   EVENT ROUTER  │    │   EVENT CLIENTS │      │
│  │                 │    │                 │    │                 │    │                 │      │
│  │ • User Message  │    │ • In-Memory     │    │ • Event routing │    │ • Real-time     │      │
│  │ • Agent Call    │    │ • Redis Streams │    │ • Filtering     │    │   monitoring    │      │
│  │ • Tool Call     │    │ • Async streams │    │ • Transformation│    │ • Logging       │      │
│  │ • Observation   │    │ • Persistence   │    │ • Aggregation   │    │ • Analytics     │      │
│  │ • Error Event   │    │ • Backpressure  │    │ • Batching      │    │ • Dashboards    │      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘      │
│                                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                              EXTERNAL INTEGRATIONS                                             │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│  │   LLM PROVIDERS │    │   VECTOR DB     │    │   CACHE/STORE   │    │   MONITORING    │      │
│  │                 │    │                 │    │                 │    │                 │      │
│  │ • OpenAI        │    │ • Qdrant        │    │ • Redis         │    │ • Prometheus    │      │
│  │ • Anthropic     │    │ • Pinecone      │    │ • PostgreSQL    │    │ • Grafana       │      │
│  │ • Local Models  │    │ • Weaviate      │    │ • MongoDB       │    │ • ELK Stack     │      │
│  │ • LiteLLM       │    │ • ChromaDB      │    │ • InfluxDB      │    │ • Custom        │      │
│  │ • Custom APIs   │    │ • Custom        │    │ • Custom        │    │   Metrics       │      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘      │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

```

## Data Flow Diagram

```
USER INPUT
    │
    ▼
┌─────────────────┐
│  ORCHESTRATOR   │ ◄─── Routes to appropriate agent
│     AGENT       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   BASE AGENT    │ ◄─── Processes with tools and memory
│                 │
└─────────┬───────┘
          │
          ├─────────────────┐
          │                 │
          ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│  TOOL SYSTEM    │  │  MEMORY STORE   │
│                 │  │                 │
│ • Execute tools │  │ • Store context │
│ • Cache results │  │ • Retrieve      │
│ • Handle errors │  │   relevant      │
└─────────┬───────┘  │   memories      │
          │          └─────────┬───────┘
          │                    │
          ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│  EVENT SYSTEM   │  │  VECTOR DB      │
│                 │  │                 │
│ • Emit events   │  │ • Store         │
│ • Stream data   │  │   embeddings    │
│ • Monitor       │  │ • Semantic      │
└─────────────────┘  │   search        │
                     └─────────────────┘
```

## Memory Processing Flow

```
CONVERSATION
    │
    ▼
┌─────────────────┐
│  MESSAGE        │ ◄─── New user/assistant message
│  HISTORY        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  TIME FILTER    │ ◄─── Check last 30 minutes
│                 │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  DUPLICATE      │ ◄─── Check existing memories
│  CHECK          │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  LLM PROCESSING │ ◄─── Construct memory with prompts
│                 │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  VECTOR STORE   │ ◄─── Store with embeddings
│                 │
└─────────────────┘
```

## Key Architectural Principles

1. **Modularity**: Each component is self-contained and replaceable
2. **Async-First**: Non-blocking operations throughout
3. **Event-Driven**: Loose coupling via event streaming
4. **Memory-Intelligent**: Multi-tier memory with semantic search
5. **Tool-Agnostic**: Flexible tool integration via MCP and local tools
6. **Scalable**: Horizontal scaling capabilities
7. **Observable**: Comprehensive logging and monitoring
8. **Extensible**: Plugin-based architecture for easy extension 