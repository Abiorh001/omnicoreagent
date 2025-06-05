# Example of connecting Azure OpenAI model via LiteLLM integration
# This configuration works with the unified LiteLLM interface
{
    "AgentConfig": {
        "tool_call_timeout": 30,
        "max_steps": 15,
        "request_limit": 5000,
        "total_tokens_limit": 40000000,
    },
    "LLM": {
        "provider": "azureopenai",
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 0.95,
        "azure_endpoint": "https://[name].openai.azure.com",
        "azure_api_version": "2024-02-01",
        "azure_deployment": "[deployment name]",
        "max_context_length": 100000,
    },
    "mcpServers": {
        "yahoo-finance": {"command": "uvx", "args": ["mcp-yahoo-finance"]},
        "ev_assistant": {
            "transport_type": "streamable_http",
            "url": "https://gitmcp.io/evalstate/mcp-webcam/mcp",
        },
    },
}
