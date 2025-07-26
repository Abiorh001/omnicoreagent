#!/usr/bin/env python3
"""
Test script to verify that memory processing is truly non-blocking
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcpomni_connect.memory_store.memory_management.vector_db import (
    fire_and_forget_memory_processing,
)
from mcpomni_connect.utils import logger


# Mock LLM connection for testing
class MockLLMConnection:
    async def llm_call(self, messages):
        # Simulate a slow LLM call (5 seconds)
        print("🤖 Simulating slow LLM call (5 seconds)...")
        await asyncio.sleep(5)
        print("✅ LLM call completed")
        return type(
            "MockResponse",
            (),
            {
                "choices": [
                    type(
                        "MockChoice",
                        (),
                        {
                            "message": type(
                                "MockMessage", (), {"content": "Mock memory summary"}
                            )()
                        },
                    )()
                ]
            },
        )()


async def test_non_blocking_memory():
    """Test that memory processing doesn't block the main process"""
    print("🧪 Testing non-blocking memory processing...")

    # Set up environment
    os.environ["QDRANT_HOST"] = "localhost"
    os.environ["QDRANT_PORT"] = "6333"

    try:
        # Create mock messages
        mock_messages = [
            type(
                "MockMessage",
                (),
                {
                    "role": "user",
                    "content": "Hello, this is a test message",
                    "timestamp": time.time(),
                },
            )(),
            type(
                "MockMessage",
                (),
                {
                    "role": "assistant",
                    "content": "Hi! This is a test response",
                    "timestamp": time.time() + 1,
                },
            )(),
        ]

        llm_connection = MockLLMConnection()
        session_id = "test_session_123"

        print("📞 Starting memory processing...")
        start_time = time.time()

        # Start memory processing (should return immediately)
        memory_thread = fire_and_forget_memory_processing(
            session_id=session_id,
            validated_messages=mock_messages,
            llm_connection=llm_connection,
        )

        processing_start_time = time.time()
        print(
            f"⏱️  Memory processing started in {processing_start_time - start_time:.3f} seconds"
        )

        # Simulate main process work
        print("🔄 Main process continuing with other work...")
        for i in range(3):
            await asyncio.sleep(1)
            print(f"   Main process step {i + 1}/3 completed")

        main_process_time = time.time() - start_time
        print(f"⏱️  Main process completed in {main_process_time:.3f} seconds")

        # Check if memory processing thread is still running
        if memory_thread.is_alive():
            print("✅ Memory processing is running in background (non-blocking)")
        else:
            print("⚠️  Memory processing thread finished")

        # Wait a bit more to see if memory processing completes
        print("⏳ Waiting 3 more seconds to see memory processing completion...")
        await asyncio.sleep(3)

        if memory_thread.is_alive():
            print(
                "⚠️  Memory processing is still running (this is expected for long operations)"
            )
        else:
            print("✅ Memory processing completed")

        total_time = time.time() - start_time
        print(f"⏱️  Total test time: {total_time:.3f} seconds")

        # The test passes if main process completes quickly (under 5 seconds)
        if main_process_time < 5:
            print("🎉 SUCCESS: Memory processing is truly non-blocking!")
            return True
        else:
            print("💥 FAILED: Memory processing is blocking the main process!")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Starting non-blocking memory processing test...")
    print("=" * 60)

    success = await test_non_blocking_memory()

    print("=" * 60)
    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Tests failed!")

    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
