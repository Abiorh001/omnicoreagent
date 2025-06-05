from unittest.mock import Mock, patch, AsyncMock
import pytest
from mcpomni_connect.llm import LLMConnection

# Mock configuration
MOCK_CONFIG = {
    "llm_api_key": "test-api-key",
    "load_config": Mock(
        return_value={
            "LLM": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 0.9,
            }
        }
    ),
}


@pytest.fixture
def mock_llm_connection():
    """Create a mock LLM connection"""
    with patch("mcpomni_connect.llm.litellm") as mock_litellm:
        mock_litellm.acompletion = Mock()
        connection = LLMConnection(Mock(**MOCK_CONFIG))
        return connection


class TestLLMConnection:
    def test_init(self, mock_llm_connection):
        """Test LLMConnection initialization"""
        assert mock_llm_connection.config is not None
        assert mock_llm_connection.llm_config is not None
        assert mock_llm_connection.llm_config["provider"] == "openai"
        assert mock_llm_connection.llm_config["model"] == "gpt-4"

    def test_llm_configuration(self, mock_llm_connection):
        """Test LLM configuration loading"""
        config = mock_llm_connection.llm_configuration()
        assert config["provider"] == "openai"
        assert config["model"] == "gpt-4"  # Should remain as base model name for OpenAI
        assert config["temperature"] == 0.7
        assert config["max_tokens"] == 1000
        assert config["top_p"] == 0.9

    @pytest.mark.asyncio
    async def test_llm_call_openai(self):
        """Test LLM call with OpenAI using LiteLLM"""
        with patch("mcpomni_connect.llm.litellm") as mock_litellm:
            messages = [{"role": "user", "content": "Hello"}]
            tools = [{"name": "test_tool", "description": "Test tool"}]
            mock_response = Mock()
            mock_litellm.acompletion = AsyncMock(return_value=mock_response)
            
            connection = LLMConnection(Mock(**MOCK_CONFIG))
            response = await connection.llm_call(messages, tools)
            
            assert response == mock_response
            mock_litellm.acompletion.assert_called_once_with(
                model="gpt-4",  # OpenAI uses base model name
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                tools=tools,
                tool_choice="auto"
            )

    @pytest.mark.asyncio
    async def test_llm_call_groq(self):
        """Test LLM call with Groq using LiteLLM"""
        groq_config = MOCK_CONFIG.copy()
        groq_config["load_config"] = Mock(
            return_value={
                "LLM": {
                    "provider": "groq",
                    "model": "llama-3.1-70b-versatile",
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "top_p": 0.9,
                }
            }
        )
        
        with patch("mcpomni_connect.llm.litellm") as mock_litellm:
            messages = [{"role": "user", "content": "Hello"}]
            tools = [{"name": "test_tool", "description": "Test tool"}]
            mock_response = Mock()
            mock_litellm.acompletion = AsyncMock(return_value=mock_response)
            
            connection = LLMConnection(Mock(**groq_config))
            response = await connection.llm_call(messages, tools)
            
            assert response == mock_response
            mock_litellm.acompletion.assert_called_once_with(
                model="groq/llama-3.1-70b-versatile",  # Groq uses prefixed model name
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                tools=tools,
                tool_choice="auto"
            )

    @pytest.mark.asyncio
    async def test_llm_call_openrouter(self):
        """Test LLM call with OpenRouter using LiteLLM"""
        openrouter_config = MOCK_CONFIG.copy()
        openrouter_config["load_config"] = Mock(
            return_value={
                "LLM": {
                    "provider": "openrouter",
                    "model": "anthropic/claude-3-sonnet",
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "top_p": 0.9,
                }
            }
        )
        
        with patch("mcpomni_connect.llm.litellm") as mock_litellm:
            messages = [{"role": "user", "content": "Hello"}]
            tools = [{"name": "test_tool", "description": "Test tool"}]
            mock_response = Mock()
            mock_litellm.acompletion = AsyncMock(return_value=mock_response)
            
            connection = LLMConnection(Mock(**openrouter_config))
            response = await connection.llm_call(messages, tools)
            
            assert response == mock_response
            mock_litellm.acompletion.assert_called_once_with(
                model="openrouter/anthropic/claude-3-sonnet",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                tools=tools,
                tool_choice="auto"
            )

    @pytest.mark.asyncio
    async def test_llm_call_gemini(self):
        """Test LLM call with Gemini using LiteLLM"""
        gemini_config = MOCK_CONFIG.copy()
        gemini_config["load_config"] = Mock(
            return_value={
                "LLM": {
                    "provider": "gemini",
                    "model": "gemini-pro",
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "top_p": 0.9,
                }
            }
        )
        
        with patch("mcpomni_connect.llm.litellm") as mock_litellm:
            messages = [{"role": "user", "content": "Hello"}]
            tools = [{"name": "test_tool", "description": "Test tool"}]
            mock_response = Mock()
            mock_litellm.acompletion = AsyncMock(return_value=mock_response)
            
            connection = LLMConnection(Mock(**gemini_config))
            response = await connection.llm_call(messages, tools)
            
            assert response == mock_response
            mock_litellm.acompletion.assert_called_once_with(
                model="gemini/gemini-pro",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                tools=tools,
                tool_choice="auto"
            )

    @pytest.mark.asyncio
    async def test_llm_call_without_tools(self):
        """Test LLM call without tools"""
        with patch("mcpomni_connect.llm.litellm") as mock_litellm:
            messages = [{"role": "user", "content": "Hello"}]
            mock_response = Mock()
            mock_litellm.acompletion = AsyncMock(return_value=mock_response)
            
            connection = LLMConnection(Mock(**MOCK_CONFIG))
            response = await connection.llm_call(messages)
            
            assert response == mock_response
            mock_litellm.acompletion.assert_called_once_with(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9
            )

    @pytest.mark.asyncio
    async def test_llm_call_error_handling(self):
        """Test LLM call error handling"""
        with patch("mcpomni_connect.llm.litellm") as mock_litellm:
            mock_litellm.acompletion = AsyncMock(side_effect=Exception("API Error"))
            
            connection = LLMConnection(Mock(**MOCK_CONFIG))
            messages = [{"role": "user", "content": "Hello"}]
            
            response = await connection.llm_call(messages)
            assert response is None

    def test_truncate_messages_for_groq(self, mock_llm_connection):
        """Test that truncate_messages_for_groq method was removed"""
        # This method should no longer exist since LiteLLM handles token management
        assert not hasattr(mock_llm_connection, 'truncate_messages_for_groq')