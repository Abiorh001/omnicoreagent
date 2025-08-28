from omnicoreagent.core.llm_support import LLMToolSupport


class TestLLMToolSupport:
    def test_check_tool_support_openai(self):
        """Test tool support checking for OpenAI"""
        # Test OpenAI with all models supported
        config = {"provider": "openai", "model": "gpt-4"}
        assert LLMToolSupport.check_tool_support(config) is True

        config = {"provider": "openai", "model": "gpt-3.5-turbo"}
        assert LLMToolSupport.check_tool_support(config) is True

    def test_check_tool_support_groq(self):
        """Test tool support checking for Groq"""
        # Test Groq with all models supported
        config = {"provider": "groq", "model": "mixtral-8x7b-32768"}
        assert LLMToolSupport.check_tool_support(config) is True

        config = {"provider": "groq", "model": "llama2-70b-4096"}
        assert LLMToolSupport.check_tool_support(config) is True

    def test_check_tool_support_openrouter(self):
        """Test tool support checking for OpenRouter"""
        # Test OpenRouter with supported models
        supported_models = [
            "openai/gpt-4",
            "anthropic/claude-3-opus",
            "groq/mixtral-8x7b",
            "mistralai/mistral-7b",
            "gemini/gemini-pro",
        ]
        for model in supported_models:
            config = {"provider": "openrouter", "model": model}
            assert LLMToolSupport.check_tool_support(config) is True

        # Test OpenRouter with unsupported model
        config = {"provider": "openrouter", "model": "unsupported-model"}
        assert LLMToolSupport.check_tool_support(config) is False

    def test_check_tool_support_unsupported_provider(self):
        """Test tool support checking for unsupported provider"""
        config = {"provider": "unsupported", "model": "any-model"}
        assert LLMToolSupport.check_tool_support(config) is False

    def test_get_supported_models(self):
        """Test getting supported models for providers"""
        # Test OpenAI (all models supported)
        assert LLMToolSupport.get_supported_models("openai") is None

        # Test Groq (all models supported)
        assert LLMToolSupport.get_supported_models("groq") is None

        # Test OpenRouter (specific models supported)
        supported_models = LLMToolSupport.get_supported_models("openrouter")
        assert supported_models is not None
        assert len(supported_models) == 5
        assert all(
            model in supported_models
            for model in ["openai", "anthropic", "groq", "mistralai", "gemini"]
        )

        # Test unsupported provider
        assert LLMToolSupport.get_supported_models("unsupported") is None
