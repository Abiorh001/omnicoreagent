from typing import Any

from groq import Groq
from openai import OpenAI
from langchain_ollama import ChatOllama
from mcpomni_connect.utils import logger


class LLMConnection:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.llm_config = None
        self.openai = OpenAI(api_key=self.config.llm_api_key)
        self.groq = Groq(api_key=self.config.llm_api_key)
        self.openrouter = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.config.llm_api_key,
        )
        self.ollama = ChatOllama(
            base_url="http://localhost:11434",
        )
        self.gemini = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.config.llm_api_key,
        )
        self.deepseek = OpenAI(
            base_url="https://api.deepseek.com",
            api_key=self.config.llm_api_key,
        )
        if not self.llm_config:
            logger.info("updating llm configuration")
            self.llm_configuration()
            logger.info(f"LLM configuration: {self.llm_config}")

    def llm_configuration(self):
        """Load the LLM configuration"""
        llm_config = self.config.load_config("servers_config.json")["LLM"]
        try:
            provider = llm_config.get("provider", "openai")
            model = llm_config.get("model", "gpt-4o-mini")
            temperature = llm_config.get("temperature", 0.5)
            max_tokens = llm_config.get("max_tokens", 5000)
            top_p = llm_config.get("top_p", 0)
            self.llm_config = {
                "provider": provider,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }
            return self.llm_config
        except Exception as e:
            logger.error(f"Error loading LLM configuration: {e}")
            return None

    async def llm_call(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] = None,
    ):
        """Call the LLM"""
        try:
            if self.llm_config["provider"].lower() == "openai":
                if tools:
                    response = self.openai.chat.completions.create(
                        model=self.llm_config["model"],
                        max_tokens=self.llm_config["max_tokens"],
                        temperature=self.llm_config["temperature"],
                        top_p=self.llm_config["top_p"],
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                    )
                else:
                    response = self.openai.chat.completions.create(
                        model=self.llm_config["model"],
                        max_tokens=self.llm_config["max_tokens"],
                        temperature=self.llm_config["temperature"],
                        top_p=self.llm_config["top_p"],
                        messages=messages,
                    )
                return response
            elif self.llm_config["provider"].lower() == "groq":
                # messages = self.truncate_messages_for_groq(messages)
                if tools:
                    response = self.groq.chat.completions.create(
                        model=self.llm_config["model"],
                        max_tokens=self.llm_config["max_tokens"],
                        temperature=self.llm_config["temperature"],
                        top_p=self.llm_config["top_p"],
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                    )
                else:
                    response = self.groq.chat.completions.create(
                        model=self.llm_config["model"],
                        max_tokens=self.llm_config["max_tokens"],
                        temperature=self.llm_config["temperature"],
                        top_p=self.llm_config["top_p"],
                        messages=messages,
                    )
                return response
            elif self.llm_config["provider"].lower() == "openrouter":
                if tools:
                    response = self.openrouter.chat.completions.create(
                        extra_body={
                            "order": ["openai", "anthropic", "groq"],
                            "allow_fallback": True,
                            "require_provider": True,
                        },
                        model=self.llm_config["model"],
                        max_tokens=self.llm_config["max_tokens"],
                        temperature=self.llm_config["temperature"],
                        top_p=self.llm_config["top_p"],
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                    )
                else:
                    response = self.openrouter.chat.completions.create(
                        extra_body={
                            "order": ["Mistral", "Openai", "Groq", "Gemini"],
                            "allow_fallback": True,
                            "require_provider": True,
                        },
                        model=self.llm_config["model"],
                        max_tokens=self.llm_config["max_tokens"],
                        temperature=self.llm_config["temperature"],
                        top_p=self.llm_config["top_p"],
                        messages=messages,
                        stop=["\n\nObservation:"],
                    )
                return response
            elif self.llm_config["provider"].lower() == "gemini":
                if tools:
                    response = self.gemini.chat.completions.create(
                        model=self.llm_config["model"],
                        max_tokens=self.llm_config["max_tokens"],
                        temperature=self.llm_config["temperature"],
                        top_p=self.llm_config["top_p"],
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                    )
                else:
                    response = self.gemini.chat.completions.create(
                        model=self.llm_config["model"],
                        max_tokens=self.llm_config["max_tokens"],
                        temperature=self.llm_config["temperature"],
                        top_p=self.llm_config["top_p"],
                        messages=messages,
                    )
                return response
            elif self.llm_config["provider"].lower() == "deepseek":
                if tools:
                    response = self.deepseek.chat.completions.create(
                        model=self.llm_config["model"],
                        max_tokens=self.llm_config["max_tokens"],
                        temperature=self.llm_config["temperature"],
                        top_p=self.llm_config["top_p"],
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                    )
                else:
                    response = self.deepseek.chat.completions.create(
                        model=self.llm_config["model"],
                        max_tokens=self.llm_config["max_tokens"],
                        temperature=self.llm_config["temperature"],
                        top_p=self.llm_config["top_p"],
                        messages=messages,
                    )
                return response
            elif self.llm_config["provider"].lower() == "ollama":
                # Use langchain_ollama's ChatOllama for response
                response = self.ollama.invoke(
                    messages,
                    model=self.llm_config["model"],
                    temperature=self.llm_config["temperature"],
                    max_tokens=self.llm_config["max_tokens"],
                )
                return response
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return None

    def truncate_messages_for_groq(self, messages):
        """Truncate messages to stay within Groq's token limits (5000 total)."""
        if not messages:
            return messages

        truncated_messages = []
        total_tokens = 0
        SYSTEM_PROMPT_LIMIT = 1000  # Max tokens for system prompt
        MESSAGE_LIMIT = 500  # Max tokens per message
        TOTAL_LIMIT = 10000  # Total token limit

        # Handle system prompt first
        system_msg = messages[0]
        if len(system_msg["content"]) > SYSTEM_PROMPT_LIMIT:
            logger.info("Truncating system prompt to 1000 tokens")
            system_msg["content"] = system_msg["content"][:SYSTEM_PROMPT_LIMIT]
        truncated_messages.append(system_msg)
        total_tokens += len(system_msg["content"])

        # Process remaining messages, ensuring recent messages are prioritized
        remaining_budget = TOTAL_LIMIT - total_tokens
        for i, msg in enumerate(messages[1:]):
            if total_tokens >= TOTAL_LIMIT:
                break

            msg_length = len(msg["content"])

            # Keep first 10 messages as they are
            if i < 10:
                truncated_messages.append(msg)
                total_tokens += msg_length
                continue

            # Truncate only if message exceeds 500 characters
            if msg_length > MESSAGE_LIMIT:
                logger.info(f"Truncating message to {MESSAGE_LIMIT} tokens")
                msg["content"] = msg["content"][:MESSAGE_LIMIT]
                msg_length = MESSAGE_LIMIT

            # Ensure messages are added even if total budget is exceeded
            if total_tokens + msg_length > TOTAL_LIMIT:
                msg["content"] = msg["content"][
                    : max(0, TOTAL_LIMIT - total_tokens)
                ]
                if msg["content"]:  # Only add if there's remaining content
                    truncated_messages.append(msg)
                    total_tokens += len(msg["content"])
                break
            else:
                truncated_messages.append(msg)
                total_tokens += msg_length

        logger.info(
            f"Final message count: {len(truncated_messages)}, Total tokens: {total_tokens}"
        )
        logger.info(f"Truncated messages: {truncated_messages}")
        return truncated_messages
