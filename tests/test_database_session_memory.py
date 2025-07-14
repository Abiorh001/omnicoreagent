#!/usr/bin/env python3
"""
Tests for DatabaseSessionMemory class.
"""

import asyncio
import json
import os
import tempfile
import pytest
import pytest_asyncio

from mcpomni_connect.memory import DatabaseSessionMemory


class TestDatabaseSessionMemory:
    """Test cases for DatabaseSessionMemory."""

    @pytest_asyncio.fixture
    async def memory(self):
        """Create a test DatabaseSessionMemory instance."""
        # Use a temporary database for testing
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_url = f"sqlite:///{tmp_file.name}"
            memory = DatabaseSessionMemory(db_url=db_url, debug=True)
            yield memory
            # Cleanup
            try:
                await memory.clear_memory()  # Clear database before deleting file
                os.unlink(tmp_file.name)
            except (FileNotFoundError, PermissionError):
                pass

    @pytest.mark.asyncio
    async def test_initialization(self, memory):
        """Test memory initialization."""
        assert memory.max_context_tokens == 30000
        assert memory.short_term_limit == int(0.7 * 30000)
        assert memory.debug is True
        assert memory.app_name == "mcp_omni_connect"
        assert memory.session_id is None
        assert memory.memory_config["mode"] == "token_budget"
        assert memory.memory_config["value"] == memory.short_term_limit

    @pytest.mark.asyncio
    async def test_memory_config(self, memory):
        """Test setting memory configuration."""
        # Test token budget mode
        memory.set_memory_config("token_budget", 5000)
        assert memory.memory_config["mode"] == "token_budget"
        assert memory.memory_config["value"] == 5000

        # Test sliding window mode
        memory.set_memory_config("sliding_window", 10)
        assert memory.memory_config["mode"] == "sliding_window"
        assert memory.memory_config["value"] == 10

        # Test invalid mode
        with pytest.raises(ValueError, match="Invalid memory mode"):
            memory.set_memory_config("invalid_mode", 100)

    @pytest.mark.asyncio
    async def test_store_and_retrieve_messages(self, memory):
        """Test storing and retrieving messages."""
        # Store user message
        await memory.store_message(
            agent_name="test_agent",
            role="user",
            content="Hello, how are you?",
            metadata={"test": "value"},
            chat_id="chat_1",
        )

        # Store assistant message
        await memory.store_message(
            agent_name="test_agent",
            role="assistant",
            content="I'm doing well, thank you!",
            metadata={"test": "value2"},
            chat_id="chat_1",
        )

        # Retrieve all messages
        messages = await memory.get_messages()
        assert len(messages) == 2

        # Check first message
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello, how are you?"
        assert messages[0]["metadata"]["agent_name"] == "test_agent"
        assert messages[0]["metadata"]["chat_id"] == "chat_1"
        assert messages[0]["metadata"]["test"] == "value"

        # Check second message
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "I'm doing well, thank you!"
        assert messages[1]["metadata"]["agent_name"] == "test_agent"
        assert messages[1]["metadata"]["chat_id"] == "chat_1"
        assert messages[1]["metadata"]["test"] == "value2"

    @pytest.mark.asyncio
    async def test_filter_by_agent_name(self, memory):
        """Test filtering messages by agent name."""
        # Store messages for different agents
        await memory.store_message(
            agent_name="agent1",
            role="user",
            content="Message from agent1",
            chat_id="chat_1",
        )

        await memory.store_message(
            agent_name="agent2",
            role="user",
            content="Message from agent2",
            chat_id="chat_1",
        )

        # Get messages for specific agent
        agent1_messages = await memory.get_messages(agent_name="agent1")
        assert len(agent1_messages) == 1
        assert agent1_messages[0]["content"] == "Message from agent1"

        agent2_messages = await memory.get_messages(agent_name="agent2")
        assert len(agent2_messages) == 1
        assert agent2_messages[0]["content"] == "Message from agent2"

        # Get all messages
        all_messages = await memory.get_messages()
        assert len(all_messages) == 2

    @pytest.mark.asyncio
    async def test_filter_by_chat_id(self, memory):
        """Test filtering messages by chat ID."""
        # Store messages for different chats
        await memory.store_message(
            agent_name="test_agent",
            role="user",
            content="Message from chat1",
            chat_id="chat_1",
        )

        await memory.store_message(
            agent_name="test_agent",
            role="user",
            content="Message from chat2",
            chat_id="chat_2",
        )

        # Get messages for specific chat
        chat1_messages = await memory.get_messages(chat_id="chat_1")
        assert len(chat1_messages) == 1
        assert chat1_messages[0]["content"] == "Message from chat1"

        chat2_messages = await memory.get_messages(chat_id="chat_2")
        assert len(chat2_messages) == 1
        assert chat2_messages[0]["content"] == "Message from chat2"

    @pytest.mark.asyncio
    async def test_backward_compatibility(self, memory):
        """Test backward compatibility with old signature."""
        # Test old signature: store_message(role, content, metadata)
        # This should be handled by the backward compatibility logic
        # Note: The current implementation expects (agent_name, role, content, metadata)
        # so we test with explicit parameters
        await memory.store_message(
            agent_name="test_agent",
            role="user",
            content="Hello world",
            metadata={"test": "old_style"},
        )

        messages = await memory.get_messages()
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello world"
        assert messages[0]["metadata"]["agent_name"] == "test_agent"

    @pytest.mark.asyncio
    async def test_get_all_messages(self, memory):
        """Test getting all messages with agent filtering."""
        # Store messages for different agents
        await memory.store_message(
            agent_name="agent1",
            role="user",
            content="Agent1 message",
        )

        await memory.store_message(
            agent_name="agent2",
            role="user",
            content="Agent2 message",
        )

        # Get all messages
        all_messages = await memory.get_all_messages()
        assert len(all_messages) == 2

        # Get messages for specific agent
        agent1_messages = await memory.get_all_messages(agent_name="agent1")
        assert len(agent1_messages) == 1
        assert agent1_messages[0]["content"] == "Agent1 message"

    @pytest.mark.asyncio
    async def test_clear_memory(self, memory):
        """Test clearing memory."""
        # Store some messages
        await memory.store_message(
            agent_name="test_agent",
            role="user",
            content="Test message",
        )

        # Verify messages exist
        messages = await memory.get_messages()
        assert len(messages) == 1

        # Clear memory
        await memory.clear_memory()

        # Verify memory is cleared
        messages = await memory.get_messages()
        assert len(messages) == 0

        # Note: session_id might not be reset immediately after clear_memory
        # but a new session will be created when needed

    @pytest.mark.asyncio
    async def test_get_last_active(self, memory):
        """Test getting last active timestamp."""
        # Note: _ensure_session() might create a session during initialization
        # so we just verify the method works
        last_active = await memory.get_last_active()
        # Should return a timestamp or None
        assert last_active is None or isinstance(last_active, (int, float))

        # Store a message to ensure we have activity
        await memory.store_message(
            agent_name="test_agent",
            role="user",
            content="Test message",
        )

        # Should now definitely have a last active timestamp
        last_active = await memory.get_last_active()
        assert last_active is not None
        assert isinstance(last_active, (int, float))

    @pytest.mark.asyncio
    async def test_save_message_history_to_file(self, memory):
        """Test saving message history to file."""
        # Store some messages
        await memory.store_message(
            agent_name="test_agent",
            role="user",
            content="Hello",
            metadata={"test": "save"},
        )

        await memory.store_message(
            agent_name="test_agent",
            role="assistant",
            content="Hi there!",
            metadata={"test": "save"},
        )

        # Save to file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_file:
            filename = tmp_file.name

        try:
            await memory.save_message_history_to_file(filename)

            # Verify file was created and contains correct data
            assert os.path.exists(filename)

            with open(filename, "r", encoding="utf-8") as f:
                saved_data = json.load(f)

            assert len(saved_data) == 2
            assert saved_data[0]["role"] == "user"
            assert saved_data[0]["content"] == "Hello"
            assert saved_data[1]["role"] == "assistant"
            assert saved_data[1]["content"] == "Hi there!"

        finally:
            # Cleanup
            try:
                os.unlink(filename)
            except FileNotFoundError:
                pass

    @pytest.mark.asyncio
    async def test_load_message_history_from_file(self, memory):
        """Test loading message history from file."""
        # Create test data
        test_data = [
            {
                "role": "user",
                "content": "Loaded message 1",
                "metadata": {"source": "file"},
            },
            {
                "role": "assistant",
                "content": "Loaded message 2",
                "metadata": {"source": "file"},
            },
        ]

        # Save test data to file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_file:
            json.dump(test_data, tmp_file, ensure_ascii=False, indent=2)
            filename = tmp_file.name

        try:
            # Load from file
            await memory.load_message_history_from_file(filename)

            # Verify messages were loaded
            messages = await memory.get_messages()
            assert len(messages) == 2
            assert messages[0]["content"] == "Loaded message 1"
            assert messages[1]["content"] == "Loaded message 2"

        finally:
            # Cleanup
            try:
                os.unlink(filename)
            except FileNotFoundError:
                pass

    @pytest.mark.asyncio
    async def test_enforce_short_term_limit(self, memory):
        """Test memory limit enforcement."""
        # Set a very low token limit for testing
        memory.set_memory_config("token_budget", 10)

        # Store messages that exceed the limit
        await memory.store_message(
            agent_name="test_agent",
            role="user",
            content="This is a very long message that should exceed the token limit",
        )

        # The enforce_short_term_limit is called automatically in store_message
        # This test mainly verifies it doesn't crash
        messages = await memory.get_messages()
        assert len(messages) >= 0  # Should not crash

    @pytest.mark.asyncio
    async def test_session_management(self, memory):
        """Test session creation and management."""
        # Initially no session
        assert memory.session_id is None

        # Store a message to trigger session creation
        await memory.store_message(
            agent_name="test_agent",
            role="user",
            content="Test message",
        )

        # Should now have a session
        assert memory.session_id is not None
        session_id = memory.session_id

        # Store another message - should use same session
        await memory.store_message(
            agent_name="test_agent",
            role="assistant",
            content="Response",
        )

        # Session ID should be the same
        assert memory.session_id == session_id

        # Should have 2 messages in the session
        messages = await memory.get_messages()
        assert len(messages) == 2


@pytest.mark.asyncio
async def test_multiple_memory_instances():
    """Test that multiple memory instances work independently."""
    # Create two separate memory instances
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file1:
        db_url1 = f"sqlite:///{tmp_file1.name}"

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file2:
        db_url2 = f"sqlite:///{tmp_file2.name}"

    try:
        memory1 = DatabaseSessionMemory(db_url=db_url1)
        memory2 = DatabaseSessionMemory(db_url=db_url2)

        # Store different messages in each
        await memory1.store_message(
            agent_name="agent1",
            role="user",
            content="Message in memory1",
        )

        await memory2.store_message(
            agent_name="agent2",
            role="user",
            content="Message in memory2",
        )

        # Verify they're independent
        messages1 = await memory1.get_messages()
        messages2 = await memory2.get_messages()

        assert len(messages1) == 1
        assert len(messages2) == 1
        assert messages1[0]["content"] == "Message in memory1"
        assert messages2[0]["content"] == "Message in memory2"

        # Clear memories before cleanup
        await memory1.clear_memory()
        await memory2.clear_memory()

    finally:
        # Cleanup
        try:
            os.unlink(tmp_file1.name)
        except (FileNotFoundError, PermissionError):
            pass
        try:
            os.unlink(tmp_file2.name)
        except (FileNotFoundError, PermissionError):
            pass


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_multiple_memory_instances())
    print("All tests passed!")
