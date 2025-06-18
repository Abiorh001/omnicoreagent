# Example of connecting Anthropic Claude model via LiteLLM integration
# This configuration works with the unified LiteLLM interface
{
    "AgentConfig": {
        "tool_call_timeout": 30,
        "max_steps": 15,
        "request_limit": 5000,
        "total_tokens_limit": 40000000,
    },
    "LLM": {
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.7,
        "max_tokens": 4000,
        "max_context_length": 200000,
        "top_p": 0.95,
    },
    "mcpServers": {
        "yahoo-finance": {"command": "uvx", "args": ["mcp-yahoo-finance"]},
        "ev_assistant": {
            "transport_type": "streamable_http",
            "url": "https://gitmcp.io/evalstate/mcp-webcam/mcp",
        },
    },
}
