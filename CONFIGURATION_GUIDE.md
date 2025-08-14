# Configuration Guide

This guide explains how to configure MCPOmni Connect for different use cases.

## Environment Variables

### Core Settings

#### `ENABLE_VECTOR_DB`
- **Default**: `false`
- **Purpose**: Controls whether vector database features are enabled
- **When `true`**: 
  - Sentence transformer model loads at startup
  - Memory system initializes with vector databases
  - Background agents can use semantic memory
- **When `false`**: 
  - No sentence transformer loading
  - Memory system disabled
  - Faster startup, smaller memory footprint

#### `OMNI_MEMORY_PROVIDER`
- **Default**: `chroma-local`
- **Purpose**: Specifies which vector database to use
- **Options**:
  - `chroma-local`: ChromaDB running locally (default)
  - `chroma-remote`: ChromaDB running on remote server
  - `qdrant-remote`: Qdrant running on remote server

## Configuration Examples

### Minimal Setup (No Vector DB)
```bash
export ENABLE_VECTOR_DB=false
# No additional configuration needed
```

### Local Development with Vector DB
```bash
export ENABLE_VECTOR_DB=true
export OMNI_MEMORY_PROVIDER=chroma-local
```

### Production with Remote Vector DB
```bash
export ENABLE_VECTOR_DB=true
export OMNI_MEMORY_PROVIDER=qdrant-remote
```

## Performance Impact

### Startup Time
- **Vector DB disabled**: ~1-2 seconds
- **Vector DB enabled**: ~30-60 seconds (includes model loading)

### Runtime Performance
- **Vector DB disabled**: No memory operations, faster response
- **Vector DB enabled**: Full memory capabilities, slight overhead

### Memory Usage
- **Vector DB disabled**: ~100-200MB
- **Vector DB enabled**: ~2-4GB (includes sentence transformer model)

## Troubleshooting

### Common Issues

1. **"sentence_transformers not available"**
   - Install: `uv add sentence-transformers`

2. **"Vector database connection failed"**
   - Check network connectivity
   - Verify database credentials
   - Ensure database service is running

3. **"Embedding model not loaded"**
   - Verify `ENABLE_VECTOR_DB=true`
   - Check logs for initialization errors
   - Ensure sufficient memory for model loading

### Log Levels

Use these log levels for debugging:
- **INFO**: General operation status
- **DEBUG**: Detailed initialization steps
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures

## Best Practices

1. **Development**: Start with `ENABLE_VECTOR_DB=false` for faster iteration
2. **Testing**: Use `ENABLE_VECTOR_DB=true` to test full functionality
3. **Production**: Choose appropriate vector database provider based on scale
4. **Monitoring**: Watch startup logs for initialization timing
