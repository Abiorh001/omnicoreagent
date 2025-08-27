# Embedding Connection Documentation

This document describes how to use the `EmbeddingConnection` class for generating embeddings using various AI providers through LiteLLM.

## Overview

The `EmbeddingConnection` class provides a unified interface for generating embeddings from different AI providers, allowing you to:
- Use different embedding models and providers independently from your LLM configuration
- Manage separate API keys for embeddings vs LLM services
- Support both synchronous and asynchronous embedding generation
- Handle provider-specific configurations automatically

## Supported Providers

The following embedding providers are supported:

| Provider | Models | API Key Environment Variable |
|----------|--------|------------------------------|
| OpenAI | text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002 | `OPENAI_API_KEY` |
| Cohere | embed-english-v3.0, embed-multilingual-v3.0, etc. | `COHERE_API_KEY` |
| HuggingFace | Any HF embedding model | `HUGGINGFACE_API_KEY` |
| Mistral AI | mistral-embed | `MISTRAL_API_KEY` |
| Gemini AI | text-embedding-004 | `GEMINI_API_KEY` |
| Vertex AI | textembedding-gecko, etc. | Google Cloud credentials |
| Voyage AI | voyage-01, voyage-lite-01 | `VOYAGE_API_KEY` |
| Nebius AI | BAAI/bge-en-icl, etc. | `NEBIUS_API_KEY` |
| NVIDIA NIM | nvidia/nv-embed-v1, etc. | `NVIDIA_NIM_API_KEY` |
| AWS Bedrock | amazon.titan-embed-text-v1 | AWS credentials |
| Azure OpenAI | text-embedding-3-small, etc. | `AZURE_API_KEY` |

## Configuration

### Basic Configuration Structure

The embedding configuration follows the same pattern as the LLM configuration:

```yaml
# LLM Configuration (separate from embeddings)
LLM:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.5
  max_tokens: 5000

# Embedding Configuration (separate from LLM)
EMBEDDING:
  provider: "openai"
  model: "text-embedding-3-small"
  dimensions: 1536
  encoding_format: "float"
  timeout: 600
```

**Important**: The `embedding_api_key` should be a **top-level attribute** of your config object, not inside the `EMBEDDING` section. This follows the same pattern as `llm_api_key` in the LLM configuration.

### Required Fields

- `provider`: The embedding service provider (e.g., "openai", "cohere")
- `model`: The specific model name for the provider
- `embedding_api_key`: Your API key for the embedding service (set as a top-level config attribute)

### Optional Fields

- `dimensions`: Number of dimensions for the output embeddings (OpenAI text-embedding-3 models)
- `encoding_format`: Output format ("float" or "base64"), defaults to "float"
- `timeout`: Request timeout in seconds, defaults to 600

### Provider-Specific Configurations

#### Azure OpenAI
```yaml
EMBEDDING:
  provider: "azureopenai"
  model: "text-embedding-3-small"
  embedding_api_key: "your-azure-api-key"
  azure_endpoint: "https://your-resource.openai.azure.com/"
  azure_api_version: "2024-02-01"
  azure_deployment: "your-deployment-name"
```

#### Vertex AI (Google Cloud)
```yaml
EMBEDDING:
  provider: "vertex_ai"
  model: "textembedding-gecko"
  embedding_api_key: "your-google-api-key"
  vertex_project: "your-project-id"
  vertex_location: "us-central1"
```

#### AWS Bedrock
```yaml
EMBEDDING:
  provider: "bedrock"
  model: "amazon.titan-embed-text-v1"
  embedding_api_key: "your-aws-access-key"
  aws_secret_key: "your-aws-secret-key"
  aws_region: "us-east-1"
```

#### NVIDIA NIM
```yaml
EMBEDDING:
  provider: "nvidia_nim"
  model: "nvidia/nv-embed-v1"
  embedding_api_key: "your-nvidia-key"
  nvidia_nim_api_base: "https://your-nim-endpoint"
```

## Usage

### Basic Usage

```python
from mcpomni_connect import EmbeddingConnection

# Initialize with your config
# Your config object should have embedding_api_key as a top-level attribute
config = YourConfigClass()
config.embedding_api_key = "your-embedding-api-key"  # Set this separately

embedding_conn = EmbeddingConnection(config, "config.yaml")

# Generate embeddings
texts = ["Hello world", "This is a test"]
response = await embedding_conn.embedding_call(texts)

# Or synchronously
response = embedding_conn.embedding_call_sync(texts)
```

### Advanced Usage

```python
# With additional parameters
response = await embedding_conn.embedding_call(
    input_text=["Document content", "Search query"],
    input_type="search_document",  # For Cohere v3 models
    metadata={"source": "web", "category": "tech"},
    user="user123"
)

# Get expected embedding dimensions
dimensions = embedding_conn.get_embedding_dimensions()
print(f"Expected dimensions: {dimensions}")
```

### Input Types

The `input_text` parameter accepts:
- **Single string**: `"Hello world"`
- **List of strings**: `["Text 1", "Text 2", "Text 3"]`

### Response Format

The response follows the standard OpenAI embedding format:

```python
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.1, -0.2, 0.3, ...]
    }
  ],
  "model": "text-embedding-3-small",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

## Error Handling

The class includes comprehensive error handling:

- **Configuration errors**: Logged and handled gracefully
- **API errors**: Caught and logged with detailed error messages
- **Invalid inputs**: Validated before making API calls
- **Provider-specific issues**: Handled according to provider requirements

## Best Practices

1. **Separate API Keys**: Use different API keys for embeddings vs LLM to maintain security and cost control
2. **Model Selection**: Choose models based on your use case (e.g., multilingual support, dimension requirements)
3. **Batch Processing**: Process multiple texts in a single call when possible to reduce API calls
4. **Error Handling**: Always check if the response is `None` before processing
5. **Provider Limits**: Be aware of provider-specific rate limits and token limits

## Examples

See the following example files for complete usage examples:
- `examples/embedding_config_example.yaml` - Configuration examples for all providers
- `examples/embedding_usage_example.py` - Python usage examples

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure the correct environment variable is set for your provider
2. **Model Not Found**: Verify the model name is correct for your provider
3. **Rate Limits**: Check your provider's rate limiting policies
4. **Dimension Mismatches**: Use `get_embedding_dimensions()` to verify expected output dimensions

### Debug Mode

Enable debug logging to see detailed configuration and API call information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Dependencies

- `litellm`: For embedding generation
- `python-dotenv`: For environment variable management
- Your existing configuration system

## Support

For issues or questions about the embedding functionality, please refer to:
- LiteLLM documentation: https://docs.litellm.ai/
- Provider-specific documentation for model details and limitations
