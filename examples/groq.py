# Example of connecting Groq model via LiteLLM integration
# This configuration works with the unified LiteLLM interface
{
    "AgentConfig": {
        "tool_call_timeout": 30,
        "max_steps": 15,
        "request_limit": 5000,
        "total_tokens_limit": 40000000,
    },
    "LLM": {
        "provider": "groq",
        "model": "llama-3.1-8b-instant",
        "temperature": 0.5,
        "max_tokens": 2000,
        "max_context_length": 8000,
        "top_p": 0.9,
    },
    "mcpServers": {
        "yahoo-finance": {"command": "uvx", "args": ["mcp-yahoo-finance"]},
        "ev_assistant": {
            "transport_type": "streamable_http",
            "url": "https://gitmcp.io/evalstate/mcp-webcam/mcp",
        },
    },
}
