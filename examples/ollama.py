# Example of connecting Ollama local model via LiteLLM integration
# This configuration works with the unified LiteLLM interface
{
    "AgentConfig": {
        "tool_call_timeout": 30,
        "max_steps": 15,
        "request_limit": 5000,
        "total_tokens_limit": 40000000,
    },
    "LLM": {
        "provider": "ollama",
        "model": "qwen2.5:3b",
        "ollama_host": "http://ollama_host:ollama_port",
        "temperature": 0.5,
        "max_tokens": 5000,
        "max_context_length": 100000,
        "top_p": 0.7,
        "top_k": "N/A",
    },
    "mcpServers": {
        "yahoo-finance": {"command": "uvx", "args": ["mcp-yahoo-finance"]},
        "ev_assistant": {
            "transport_type": "streamable_http",
            "url": "https://gitmcp.io/evalstate/mcp-webcam/mcp",
        },
    },
}
