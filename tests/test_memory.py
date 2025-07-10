import os
import tempfile

import pytest

from mcpomni_connect.memory import (
    InMemoryStore,
    RedisShortTermMemory,
)


@pytest.mark.asyncio
class TestInMemoryStore:
    @pytest.fixture
    def memory(self):
        return InMemoryStore(max_context_tokens=100, debug=True)

    async def test_store_and_get_messages(self, memory):
        await memory.store_message("agent1", "user", "Hello")
        await memory.store_message("agent1", "assistant", "Hi")

        messages = await memory.get_messages("agent1")
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

    async def test_get_empty_messages(self, memory):
        messages = await memory.get_messages("unknown_agent")
        assert messages == []

    async def test_truncate_message_history(self, memory):
        long_message = "word " * 50  # ~50 tokens
        for _ in range(5):
            await memory.store_message("agent1", "user", long_message)

        messages = await memory.get_messages("agent1")
        total_tokens = sum(len(msg["content"].split()) for msg in messages)
        assert total_tokens <= memory.short_term_limit

    async def test_clear_memory_specific_agent(self, memory):
        await memory.store_message("agent1", "user", "Hello")
        await memory.store_message("agent2", "user", "Hi")

        await memory.clear_memory("agent1")
        assert await memory.get_messages("agent1") == []
        assert len(await memory.get_messages("agent2")) == 1

    async def test_clear_memory_all(self, memory):
        await memory.store_message("agent1", "user", "Hello")
        await memory.store_message("agent2", "user", "Hi")

        await memory.clear_memory()
        assert await memory.get_messages("agent1") == []
        assert await memory.get_messages("agent2") == []

    async def test_get_all_messages(self, memory):
        await memory.store_message("agent1", "user", "Hello")
        await memory.store_message("agent2", "assistant", "Hi")

        all_msgs = await memory.get_all_messages()
        assert "agent1" in all_msgs
        assert "agent2" in all_msgs
        assert len(all_msgs["agent1"]) == 1
        assert len(all_msgs["agent2"]) == 1

    async def test_save_and_load_message_history_from_file(self, memory):
        await memory.store_message("agent1", "user", "Message 1")
        await memory.store_message("agent1", "assistant", "Message 2")

        with tempfile.NamedTemporaryFile(delete=False) as tf:
            temp_file = tf.name

        await memory.save_message_history_to_file(temp_file)

        # Clear memory and reload from file
        await memory.clear_memory("agent1")
        assert await memory.get_messages("agent1") == []

        await memory.load_message_history_from_file(temp_file)
        messages = await memory.get_messages("agent1")
        assert len(messages) == 2
        assert messages[0]["content"] == "Message 1"

        os.remove(temp_file)

    async def test_save_message_history_appends(self, memory):
        await memory.store_message("agent1", "user", "Initial message")

        with tempfile.NamedTemporaryFile(delete=False) as tf:
            temp_file = tf.name

        await memory.save_message_history_to_file(temp_file)
        await memory.store_message("agent1", "assistant", "New message")
        await memory.save_message_history_to_file(temp_file)

        with open(temp_file) as f:
            contents = f.read()

        assert "Initial message" in contents
        assert "New message" in contents

        os.remove(temp_file)


# TODO The redis memory needs to be updated to match the in-memory storage
# @pytest.mark.asyncio
# class TestRedisShortTermMemory:
#     @pytest.fixture
#     def mock_redis(self):
#         redis_mock = AsyncMock()
#         redis_mock.zadd = AsyncMock()
#         redis_mock.set = AsyncMock()
#         redis_mock.zrange = AsyncMock(return_value=[])
#         redis_mock.delete = AsyncMock()
#         redis_mock.get = AsyncMock(return_value="1680000000.0")
#         redis_mock.zrem = AsyncMock()
#         return redis_mock

#     async def test_store_message(self, mock_redis):
#         memory = RedisShortTermMemory(redis_client=mock_redis)
#         await memory.store_message("user", "hello", metadata={"intent": "greeting"})

#         assert mock_redis.zadd.called
#         assert mock_redis.set.called

#     async def test_get_messages(self, mock_redis):
#         stored_msg = json.dumps(
#             {
#                 "role": "user",
#                 "content": "Hello from Redis!",
#                 "metadata": json.dumps({"intent": "greet"}),
#                 "timestamp": 1680000000.0,
#             }
#         )
#         mock_redis.zrange.return_value = [stored_msg]
#         memory = RedisShortTermMemory(redis_client=mock_redis)
#         messages = await memory.get_messages()

#         assert isinstance(messages, list)
#         assert messages[0]["role"] == "user"
#         assert messages[0]["metadata"]["intent"] == "greet"

#     async def test_get_last_active(self, mock_redis):
#         memory = RedisShortTermMemory(redis_client=mock_redis)
#         last_active = await memory.get_last_active()
#         assert isinstance(last_active, float)
#         assert last_active == 1680000000.0

#     async def test_clear_memory(self, mock_redis):
#         memory = RedisShortTermMemory(redis_client=mock_redis)
#         await memory.clear_memory()
#         mock_redis.delete.assert_called_once()

#     async def test_enforce_short_term_limit(self, mock_redis):
#         messages = [
#             (
#                 json.dumps({"role": "user", "content": "word " * 200}),
#                 1680000000.0,
#             ),
#             (
#                 json.dumps({"role": "assistant", "content": "another " * 200}),
#                 1680000001.0,
#             ),
#         ]
#         mock_redis.zrange.return_value = messages
#         memory = RedisShortTermMemory(redis_client=mock_redis, max_context_tokens=100)
#         await memory.enforce_short_term_limit()
#         assert mock_redis.zrem.called
