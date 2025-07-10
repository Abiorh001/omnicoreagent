# Testing

MCPOmni Connect includes comprehensive testing infrastructure to ensure reliability and quality. This guide covers running tests, writing new tests, and testing best practices.

## Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_llm.py         # LLM integration tests
│   ├── test_transport.py   # Transport layer tests
│   ├── test_memory.py      # Memory management tests
│   └── test_agents.py      # Agent system tests
├── integration/             # Integration tests
│   ├── test_mcp_servers.py # MCP server integration
│   ├── test_workflows.py   # End-to-end workflows
│   └── test_auth.py        # Authentication flows
├── performance/             # Performance tests
│   ├── test_load.py        # Load testing
│   └── test_benchmarks.py  # Benchmark tests
├── fixtures/                # Test data and fixtures
│   ├── config/             # Test configurations
│   ├── data/               # Sample data files
│   └── responses/          # Mock responses
└── conftest.py             # Pytest configuration
```

## Running Tests

### Quick Test Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_llm.py -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run only fast tests (skip slow/integration tests)
pytest tests/ -m "not slow" -v

# Run tests with detailed output
pytest tests/ -v -s --tb=short
```

### Test Categories

MCPOmni Connect tests are organized by markers:

```bash
# Unit tests only
pytest tests/ -m "not integration and not slow" -v

# Integration tests
pytest tests/ -m "integration" -v

# Performance tests
pytest tests/ -m "performance" -v

# Tests requiring external services
pytest tests/ -m "requires_redis" -v

# OpenAI API integration tests
pytest tests/ -m "OpenAIIntegration" -v
```

## Test Configuration

### Environment Setup

Create a test environment configuration:

```bash title="tests/.env.test"
# Test environment variables
LLM_API_KEY=test-api-key-mock
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=15  # Use different DB for tests
DEBUG=true
```

### Test Configuration Files

```json title="tests/fixtures/config/test_servers_config.json"
{
    "AgentConfig": {
        "tool_call_timeout": 5,
        "max_steps": 3,
        "request_limit": 10,
        "total_tokens_limit": 1000
    },
    "LLM": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.1,
        "max_tokens": 100
    },
    "mcpServers": {
        "test-server": {
            "transport_type": "stdio",
            "command": "echo",
            "args": ["test"]
        }
    }
}
```

## Unit Tests

### LLM Integration Tests

```python title="tests/unit/test_llm.py"
import pytest
from unittest.mock import Mock, patch
from mcpomni_connect.llm import LLMIntegration

class TestLLMIntegration:
    @pytest.fixture
    def llm_config(self):
        return {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    
    @pytest.fixture
    def llm_integration(self, llm_config):
        return LLMIntegration(llm_config)
    
    @patch('mcpomni_connect.llm.litellm.completion')
    def test_generate_response(self, mock_completion, llm_integration):
        # Arrange
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_completion.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        
        # Act
        response = llm_integration.generate_response(messages)
        
        # Assert
        assert response == "Test response"
        mock_completion.assert_called_once()
    
    def test_message_conversion(self, llm_integration):
        # Test Message object to dict conversion
        from pydantic import BaseModel
        
        class Message(BaseModel):
            role: str
            content: str
        
        message = Message(role="user", content="test")
        result = llm_integration._convert_message(message)
        
        assert result == {"role": "user", "content": "test"}
```

### Transport Layer Tests

```python title="tests/unit/test_transport.py"
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from mcpomni_connect.transport import StdioTransport, SSETransport

class TestStdioTransport:
    @pytest.fixture
    def stdio_config(self):
        return {
            "command": "echo",
            "args": ["hello"]
        }
    
    @pytest.mark.asyncio
    async def test_stdio_connection(self, stdio_config):
        transport = StdioTransport(stdio_config)
        
        # Test connection
        await transport.connect()
        assert transport.is_connected()
        
        # Test message sending
        response = await transport.send_message({"test": "message"})
        assert response is not None
        
        # Cleanup
        await transport.disconnect()

class TestSSETransport:
    @pytest.fixture
    def sse_config(self):
        return {
            "url": "http://localhost:3000/sse",
            "headers": {"Authorization": "Bearer test-token"}
        }
    
    @pytest.mark.asyncio
    async def test_sse_connection(self, sse_config):
        with patch('httpx.AsyncClient') as mock_client:
            transport = SSETransport(sse_config)
            
            # Mock successful connection
            mock_client.return_value.stream.return_value.__aenter__.return_value = Mock()
            
            await transport.connect()
            assert transport.is_connected()
```

### Memory Management Tests

```python title="tests/unit/test_memory.py"
import pytest
from unittest.mock import Mock, patch
from mcpomni_connect.memory import InMemoryStore, RedisShortTermMemory

class TestInMemoryStore:
    @pytest.fixture
    def memory(self):
        return InMemoryStore(max_context_tokens=100, debug=True)
    
    @pytest.mark.asyncio
    async def test_store_and_get_messages(self, memory):
        # Test storing messages
        await memory.store_message(
            role="user",
            content="test message",
            metadata={"agent_name": "test_agent"},
            session_id="test_session"
        )
        
        # Test retrieving messages
        messages = await memory.get_messages(
            session_id="test_session",
            agent_name="test_agent"
        )
        
        assert len(messages) == 1
        assert messages[0]["content"] == "test message"
        assert messages[0]["role"] == "user"
    
    @pytest.mark.asyncio
    async def test_session_isolation(self, memory):
        # Store messages in different sessions
        await memory.store_message(
            role="user",
            content="session1 message",
            session_id="session1"
        )
        
        await memory.store_message(
            role="user", 
            content="session2 message",
            session_id="session2"
        )
        
        # Verify sessions are isolated
        session1_messages = await memory.get_messages(session_id="session1")
        session2_messages = await memory.get_messages(session_id="session2")
        
        assert len(session1_messages) == 1
        assert len(session2_messages) == 1
        assert session1_messages[0]["content"] == "session1 message"
        assert session2_messages[0]["content"] == "session2 message"
    
    @pytest.mark.asyncio
    async def test_agent_filtering(self, memory):
        # Store messages for different agents
        await memory.store_message(
            role="user",
            content="agent1 message",
            metadata={"agent_name": "agent1"},
            session_id="test_session"
        )
        
        await memory.store_message(
            role="user",
            content="agent2 message", 
            metadata={"agent_name": "agent2"},
            session_id="test_session"
        )
        
        # Test filtering by agent
        agent1_messages = await memory.get_messages(
            session_id="test_session",
            agent_name="agent1"
        )
        
        agent2_messages = await memory.get_messages(
            session_id="test_session",
            agent_name="agent2"
        )
        
        assert len(agent1_messages) == 1
        assert len(agent2_messages) == 1
        assert agent1_messages[0]["content"] == "agent1 message"
        assert agent2_messages[0]["content"] == "agent2 message"
    
    @pytest.mark.asyncio
    async def test_clear_memory(self, memory):
        # Store some messages
        await memory.store_message(
            role="user",
            content="test message",
            session_id="test_session"
        )
        
        # Clear memory
        await memory.clear_memory(session_id="test_session")
        
        # Verify memory is cleared
        messages = await memory.get_messages(session_id="test_session")
        assert len(messages) == 0
```

## Integration Tests

### MCP Server Integration

```python title="tests/integration/test_mcp_servers.py"
import pytest
import asyncio
from mcpomni_connect.core import MCPOmniConnect

class TestMCPServerIntegration:
    @pytest.fixture
    def test_config(self):
        return {
            "LLM": {
                "provider": "openai",
                "model": "gpt-3.5-turbo"
            },
            "mcpServers": {
                "filesystem": {
                    "transport_type": "stdio",
                    "command": "uvx",
                    "args": ["mcp-server-filesystem", "/tmp"]
                }
            }
        }
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_server_connection(self, test_config):
        client = MCPOmniConnect(test_config)
        
        try:
            # Test connection
            await client.connect_servers()
            
            # Test tool discovery
            tools = await client.list_tools()
            assert len(tools) > 0
            
            # Test tool execution
            result = await client.execute_tool(
                "list_directory",
                {"path": "/tmp"}
            )
            assert result is not None
            
        finally:
            await client.disconnect()
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_workflow_execution(self, test_config):
        client = MCPOmniConnect(test_config)
        
        # Test complete workflow
        result = client.execute_workflow([
            {"tool": "list_directory", "params": {"path": "/tmp"}},
            {"tool": "read_file", "params": {"path": "/tmp/test.txt"}}
        ])
        
        assert result["success"] == True
        assert len(result["steps"]) == 2
```

### Authentication Flow Tests

```python title="tests/integration/test_auth.py"
import pytest
from unittest.mock import patch, Mock
from mcpomni_connect.auth import OAuthManager, BearerTokenAuth

class TestOAuthFlow:
    @pytest.mark.integration
    @patch('webbrowser.open')
    @patch('http.server.HTTPServer')
    def test_oauth_callback_server(self, mock_server, mock_browser):
        oauth_manager = OAuthManager()
        
        # Mock OAuth callback
        mock_request = Mock()
        mock_request.path = "/callback?code=test-auth-code"
        
        # Test callback handling
        result = oauth_manager.handle_callback(mock_request)
        assert result["code"] == "test-auth-code"
        
        # Verify browser was opened
        mock_browser.assert_called_once()

class TestBearerTokenAuth:
    def test_bearer_token_headers(self):
        auth = BearerTokenAuth("test-token-123")
        headers = auth.get_headers()
        
        assert headers["Authorization"] == "Bearer test-token-123"
        assert "Content-Type" in headers
```

## Performance Tests

### Load Testing

```python title="tests/performance/test_load.py"
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from mcpomni_connect.core import MCPOmniConnect

class TestPerformance:
    @pytest.mark.performance
    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        client = MCPOmniConnect(test_config)
        
        def make_request():
            return client.execute_tool("list_directory", {"path": "/tmp"})
        
        # Test 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
            
            end_time = time.time()
        
        # Assert all requests succeeded
        assert all(result is not None for result in results)
        
        # Assert reasonable performance (< 5 seconds for 10 requests)
        assert end_time - start_time < 5.0
    
    @pytest.mark.performance
    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        client = MCPOmniConnect(test_config)
        
        # Execute many operations
        for _ in range(100):
            client.execute_tool("list_directory", {"path": "/tmp"})
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Assert memory growth is reasonable (< 50MB)
        assert memory_growth < 50 * 1024 * 1024
```

### Benchmark Tests

```python title="tests/performance/test_benchmarks.py"
import pytest
import time
from mcpomni_connect.core import MCPOmniConnect

class TestBenchmarks:
    @pytest.mark.performance
    def test_tool_execution_speed(self):
        """Benchmark tool execution speed."""
        client = MCPOmniConnect(test_config)
        
        # Warm up
        for _ in range(5):
            client.execute_tool("list_directory", {"path": "/tmp"})
        
        # Benchmark
        iterations = 20
        start_time = time.time()
        
        for _ in range(iterations):
            client.execute_tool("list_directory", {"path": "/tmp"})
        
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations
        
        # Assert average execution time is reasonable
        assert avg_time < 0.5  # Less than 500ms per execution
        
        print(f"Average tool execution time: {avg_time:.3f}s")
```

## Test Utilities and Fixtures

### Common Fixtures

```python title="tests/conftest.py"
import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory."""
    return Path(__file__).parent / "fixtures" / "data"

@pytest.fixture
def temp_dir():
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Test response from mock LLM",
                    "role": "assistant"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 8,
            "total_tokens": 18
        }
    }

@pytest.fixture
def sample_conversation():
    """Sample conversation for testing memory features."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"}
    ]
```

### Mock Servers

```python title="tests/fixtures/mock_server.py"
import asyncio
import json
from aiohttp import web

class MockMCPServer:
    """Mock MCP server for testing."""
    
    def __init__(self, port=8899):
        self.port = port
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        self.app.router.add_post('/mcp', self.handle_mcp_request)
    
    async def handle_mcp_request(self, request):
        data = await request.json()
        
        # Mock responses based on method
        if data.get('method') == 'tools/list':
            return web.json_response({
                "tools": [
                    {
                        "name": "mock_tool",
                        "description": "A mock tool for testing",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "input": {"type": "string"}
                            }
                        }
                    }
                ]
            })
        
        return web.json_response({"result": "mock response"})
    
    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        return runner
```

## Testing Best Practices

### Writing Good Tests

!!! tip "Test Writing Guidelines"
    1. **Descriptive Names**: Use clear, descriptive test names
    2. **Arrange-Act-Assert**: Structure tests clearly
    3. **Single Responsibility**: One assertion per test when possible
    4. **Fast Execution**: Keep unit tests fast (< 100ms)
    5. **Isolated**: Tests shouldn't depend on each other
    6. **Deterministic**: Tests should always produce same results

### Test Organization

```python
class TestFeatureName:
    """Test class for specific feature."""
    
    @pytest.fixture
    def feature_setup(self):
        """Setup specific to this feature."""
        pass
    
    def test_normal_case(self, feature_setup):
        """Test the normal/happy path."""
        pass
    
    def test_edge_case(self, feature_setup):
        """Test edge cases."""
        pass
    
    def test_error_handling(self, feature_setup):
        """Test error conditions."""
        pass
```

### Mock Usage

```python
# Good: Mock external dependencies
@patch('mcpomni_connect.external_api.requests.get')
def test_api_call(self, mock_get):
    mock_get.return_value.json.return_value = {"status": "ok"}
    result = my_function()
    assert result["status"] == "ok"

# Avoid: Mocking internal logic
# This makes tests brittle and less valuable
```

## Continuous Integration

### GitHub Actions Configuration

```yaml title=".github/workflows/test.yml"
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install UV
      run: pip install uv
    
    - name: Install dependencies
      run: uv sync
    
    - name: Run tests
      run: |
        uv run pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Data Management

### Sample Data Files

```json title="tests/fixtures/data/sample_config.json"
{
    "LLM": {
        "provider": "openai",
        "model": "gpt-3.5-turbo"
    },
    "mcpServers": {
        "test-server": {
            "transport_type": "stdio",
            "command": "echo",
            "args": ["test"]
        }
    }
}
```

### Test Database

For integration tests requiring database:

```python title="tests/fixtures/test_db.py"
import sqlite3
import tempfile
from pathlib import Path

@pytest.fixture
def test_database():
    """Create temporary test database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Create test schema
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    ''')
    conn.execute('''
        INSERT INTO users (name, email) VALUES 
        ('Test User', 'test@example.com'),
        ('Another User', 'another@example.com')
    ''')
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink()
```

---

This comprehensive testing guide ensures MCPOmni Connect maintains high quality and reliability across all its components and features.

**Next**: [Contributing →](contributing.md) 