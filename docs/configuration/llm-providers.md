# LLM Providers

MCPOmni Connect uses LiteLLM to provide unified access to 100+ AI models across all major providers. This page covers configuration for each supported provider.

## Supported Providers

| Provider | Models | API Key Required | Local/Remote |
|----------|--------|------------------|--------------|
| **OpenAI** | GPT-4, GPT-3.5, etc. | Yes | Remote |
| **Anthropic** | Claude 3.5, Claude 3 | Yes | Remote |
| **Google** | Gemini Pro, Flash | Yes | Remote |
| **Groq** | Llama, Mixtral, Gemma | Yes | Remote |
| **DeepSeek** | DeepSeek-V3, Coder | Yes | Remote |
| **Azure OpenAI** | GPT models | Yes | Remote |
| **OpenRouter** | 200+ models | Yes | Remote |
| **Ollama** | Local models | No | Local |

## OpenAI

### Configuration

```json
{
    "LLM": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 4000,
        "max_context_length": 128000,
        "top_p": 0.9
    }
}
```

### Available Models

| Model | Context Length | Use Case |
|-------|----------------|----------|
| `gpt-4o` | 128K | Most capable, latest |
| `gpt-4o-mini` | 128K | Fast, cost-effective |
| `gpt-4-turbo` | 128K | High performance |
| `gpt-4` | 8K | Standard GPT-4 |
| `gpt-3.5-turbo` | 16K | Fast, affordable |

### Environment Setup

```bash title=".env"
LLM_API_KEY=sk-your-openai-api-key-here
```

### Advanced Configuration

```json
{
    "LLM": {
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.3,
        "max_tokens": 8000,
        "max_context_length": 128000,
        "top_p": 0.8,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1,
        "stop": ["</end>"]
    }
}
```

## Anthropic (Claude)

### Configuration

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

### Available Models

| Model | Context Length | Strengths |
|-------|----------------|-----------|
| `claude-3-5-sonnet-20241022` | 200K | Best overall, coding |
| `claude-3-5-haiku-20241022` | 200K | Fast, efficient |
| `claude-3-opus-20240229` | 200K | Most capable (legacy) |
| `claude-3-sonnet-20240229` | 200K | Balanced (legacy) |
| `claude-3-haiku-20240307` | 200K | Fast (legacy) |

### Environment Setup

```bash title=".env"
LLM_API_KEY=sk-ant-your-anthropic-api-key-here
```

### Example: Code Analysis Setup

```json
{
    "LLM": {
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.1,
        "max_tokens": 8000,
        "max_context_length": 200000,
        "top_p": 0.9
    }
}
```

## Google (Gemini)

### Configuration

```json
{
    "LLM": {
        "provider": "google",
        "model": "gemini-1.5-pro",
        "temperature": 0.7,
        "max_tokens": 4000,
        "max_context_length": 1000000,
        "top_p": 0.9
    }
}
```

### Available Models

| Model | Context Length | Strengths |
|-------|----------------|-----------|
| `gemini-1.5-pro` | 1M | Largest context window |
| `gemini-1.5-flash` | 1M | Fast, efficient |
| `gemini-pro` | 32K | Standard model |

### Environment Setup

```bash title=".env"
LLM_API_KEY=your-google-api-key-here
```

### Long Context Configuration

```json
{
    "LLM": {
        "provider": "google",
        "model": "gemini-1.5-pro",
        "temperature": 0.3,
        "max_tokens": 8000,
        "max_context_length": 1000000,
        "top_p": 0.8
    }
}
```

## Groq (Fast Inference)

### Configuration

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

### Available Models

| Model | Context Length | Speed |
|-------|----------------|-------|
| `llama-3.1-8b-instant` | 8K | Very Fast |
| `llama-3.1-70b-versatile` | 8K | Fast |
| `mixtral-8x7b-32768` | 32K | Fast |
| `gemma-7b-it` | 8K | Fast |

### Environment Setup

```bash title=".env"
LLM_API_KEY=gsk_your-groq-api-key-here
```

### High-Speed Configuration

```json
{
    "LLM": {
        "provider": "groq",
        "model": "llama-3.1-8b-instant",
        "temperature": 0.1,
        "max_tokens": 1000,
        "max_context_length": 8000,
        "top_p": 0.8
    }
}
```

## DeepSeek

### Configuration

```json
{
    "LLM": {
        "provider": "deepseek",
        "model": "deepseek-chat",
        "temperature": 0.5,
        "max_tokens": 4000,
        "max_context_length": 32000,
        "top_p": 0.8
    }
}
```

### Available Models

| Model | Context Length | Specialization |
|-------|----------------|----------------|
| `deepseek-chat` | 32K | General chat |
| `deepseek-coder` | 32K | Code generation |
| `deepseek-reasoner` | 32K | Reasoning tasks |

### Environment Setup

```bash title=".env"
LLM_API_KEY=sk-your-deepseek-api-key-here
```

## Azure OpenAI

### Configuration

```json
{
    "LLM": {
        "provider": "azure",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 4000,
        "max_context_length": 8000,
        "top_p": 0.9,
        "azure_endpoint": "https://your-resource.openai.azure.com",
        "azure_api_version": "2024-02-01",
        "azure_deployment": "your-deployment-name"
    }
}
```

### Environment Setup

```bash title=".env"
LLM_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-01
```

### Enterprise Configuration

```json
{
    "LLM": {
        "provider": "azure",
        "model": "gpt-4-turbo",
        "temperature": 0.3,
        "max_tokens": 8000,
        "max_context_length": 128000,
        "top_p": 0.8,
        "azure_endpoint": "${AZURE_OPENAI_ENDPOINT}",
        "azure_api_version": "${AZURE_OPENAI_API_VERSION}",
        "azure_deployment": "gpt-4-turbo-deployment"
    }
}
```

## OpenRouter

Access to 200+ models through a single API.

### Configuration

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

### Popular Models

| Model | Provider | Strengths |
|-------|----------|-----------|
| `anthropic/claude-3.5-sonnet` | Anthropic | Best overall |
| `openai/gpt-4o` | OpenAI | Latest GPT-4 |
| `google/gemini-pro-1.5` | Google | Large context |
| `meta-llama/llama-3.1-8b-instruct` | Meta | Open source |
| `mistralai/mixtral-8x7b-instruct` | Mistral | Efficient |

### Environment Setup

```bash title=".env"
LLM_API_KEY=sk-or-your-openrouter-api-key-here
```

## Ollama (Local Models)

Run models locally for privacy and offline usage.

### Configuration

```json
{
    "LLM": {
        "provider": "ollama",
        "model": "llama3.1:8b",
        "temperature": 0.7,
        "max_tokens": 4000,
        "max_context_length": 8000,
        "top_p": 0.9,
        "ollama_host": "http://localhost:11434"
    }
}
```

### Popular Local Models

| Model | Size | Use Case |
|-------|------|----------|
| `llama3.1:8b` | 4.7GB | General purpose |
| `llama3.1:13b` | 7.3GB | Better quality |
| `codellama:7b` | 3.8GB | Code generation |
| `mistral:7b` | 4.1GB | Efficient |
| `qwen2:7b` | 4.4GB | Multilingual |

### Setup Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.1:8b

# Start Ollama service
ollama serve
```

### No API Key Required

```json
{
    "LLM": {
        "provider": "ollama",
        "model": "llama3.1:8b",
        "temperature": 0.5,
        "max_tokens": 2000,
        "ollama_host": "http://localhost:11434"
    }
}
```

## Configuration Parameters

### Common Parameters

| Parameter | Description | Typical Range | Default |
|-----------|-------------|---------------|---------|
| `temperature` | Response creativity | 0.0 - 2.0 | 0.7 |
| `max_tokens` | Response length limit | 1 - 8000 | 1000 |
| `top_p` | Nucleus sampling | 0.1 - 1.0 | 1.0 |
| `frequency_penalty` | Repetition penalty | -2.0 - 2.0 | 0.0 |
| `presence_penalty` | Topic diversity | -2.0 - 2.0 | 0.0 |

### Provider-Specific Parameters

=== "OpenAI"
    ```json
    {
        "stop": ["</end>", "\n\n"],
        "logit_bias": {"-1": -100},
        "user": "user-123"
    }
    ```

=== "Anthropic"
    ```json
    {
        "top_k": 40,
        "stop_sequences": ["</thinking>"]
    }
    ```

=== "Google"
    ```json
    {
        "candidate_count": 1,
        "safety_settings": []
    }
    ```

## Model Selection Guide

### By Use Case

| Use Case | Recommended Models |
|----------|-------------------|
| **General Chat** | GPT-4o-mini, Claude 3.5 Sonnet |
| **Code Generation** | Claude 3.5 Sonnet, DeepSeek Coder |
| **Long Documents** | Gemini 1.5 Pro, Claude 3.5 Sonnet |
| **Fast Responses** | Groq Llama 3.1, GPT-3.5 Turbo |
| **Cost Effective** | GPT-4o-mini, Groq models |
| **Privacy/Local** | Ollama Llama 3.1, Mistral |

### By Performance

| Priority | Models | Trade-offs |
|----------|--------|------------|
| **Quality** | Claude 3.5 Sonnet, GPT-4o | Higher cost |
| **Speed** | Groq models, GPT-3.5 | Lower accuracy |
| **Context** | Gemini 1.5 Pro | Google ecosystem |
| **Cost** | GPT-4o-mini, DeepSeek | Some capability limits |

## Switching Between Providers

You can switch providers dynamically:

```bash
# Update configuration and restart
vim servers_config.json

# Or use environment variables
export LLM_PROVIDER=anthropic
export LLM_MODEL=claude-3-5-sonnet-20241022
```

## Cost Optimization

### Token Usage Monitoring

```bash
# Check current usage
/api_stats

# Set usage limits in configuration
{
    "AgentConfig": {
        "total_tokens_limit": 50000,
        "request_limit": 1000
    }
}
```

### Cost-Effective Models

```json
{
    "LLM": {
        "provider": "openai",
        "model": "gpt-4o-mini",  // Most cost-effective GPT-4 class
        "max_tokens": 1000,     // Limit response length
        "temperature": 0.3      // More focused responses
    }
}
```

## Troubleshooting

### Common Issues

!!! failure "Invalid API Key"
    **Error**: `Authentication failed`
    
    **Solutions**:
    - Verify API key in `.env` file
    - Check key has proper permissions
    - Ensure key is for correct provider

!!! failure "Model Not Found"
    **Error**: `Model not available`
    
    **Solutions**:
    - Check model name spelling
    - Verify model availability for your account
    - Try alternative model

!!! failure "Rate Limit"
    **Error**: `Rate limit exceeded`
    
    **Solutions**:
    - Reduce request frequency
    - Upgrade API plan
    - Switch to different provider

### Testing Configuration

```bash
# Test with simple query
> Hello, can you respond?

# Check model info
/api_stats

# Enable debug for detailed logs
/debug
```

---

**Next**: [Troubleshooting →](troubleshooting.md) 