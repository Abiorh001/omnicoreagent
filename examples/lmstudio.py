# Example of connecting LMStudio local model via LiteLLM integration  
# This configuration works with the unified LiteLLM interface
{
    "AgentConfig": {
        "tool_call_timeout": 30,
        "max_steps": 15,
        "request_limit": 1000,
        "total_tokens_limit": 1000000
    },
    "LLM": {
        "provider": "lmstudio",
        "model": "gemma-3-27b-it-qat",
        "lmstudio_host": "http://localhost:1234/v1",
        "lmstudio_api_key": "",
        "temperature": 0.25,
        "max_tokens": 5000,
        "max_context_length": 32000,
        "top_p": 0.5
    },
    "mcpServers": {
        "yahoo-finance": {
            "command": "uvx",
            "args": ["mcp-yahoo-finance"]
        },
        "ev_assistant": {
            "transport_type": "streamable_http",
            "url": "https://gitmcp.io/evalstate/mcp-webcam/mcp"
        }
    }
}
