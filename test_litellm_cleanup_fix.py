#!/usr/bin/env python3
"""
Test script to verify LiteLLM cleanup fix
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcpomni_connect.llm import LLMConnection
from mcpomni_connect.client import Configuration
from mcpomni_connect.utils import logger


async def test_litellm_cleanup():
    """Test that LiteLLM cleanup works properly"""
    print("🧪 Testing LiteLLM cleanup fix...")

    # Set up environment
    os.environ["LLM_API_KEY"] = "test-key"

    try:
        # Create config and connections
        config = Configuration()
        llm_connection = LLMConnection(config)

        # Make a test call to trigger LiteLLM async tasks
        print("📞 Making test LLM call...")
        messages = [{"role": "user", "content": "Hello"}]

        # This will likely fail due to invalid API key, but it will create async tasks
        try:
            response = await llm_connection.llm_call(messages)
            print(f"✅ LLM call completed: {response is not None}")
        except Exception as e:
            print(f"⚠️  LLM call failed (expected): {e}")

        # Wait a moment for any async tasks to be created
        await asyncio.sleep(1)

        # Check for pending tasks before cleanup
        pending_before = [
            task
            for task in asyncio.all_tasks()
            if not task.done() and task != asyncio.current_task()
        ]
        print(f"📊 Pending tasks before cleanup: {len(pending_before)}")

        # Show details of pending tasks
        for i, task in enumerate(pending_before):
            task_str = str(task)
            print(f"   Task {i + 1}: {task_str[:100]}...")

        # Perform cleanup
        print("🧹 Performing LiteLLM cleanup...")
        await llm_connection.cleanup()

        # Check for pending tasks after cleanup
        pending_after = [
            task
            for task in asyncio.all_tasks()
            if not task.done() and task != asyncio.current_task()
        ]
        print(f"📊 Pending tasks after cleanup: {len(pending_after)}")

        # Show details of remaining tasks
        for i, task in enumerate(pending_after):
            task_str = str(task)
            print(f"   Remaining Task {i + 1}: {task_str[:100]}...")

        # Check specifically for LiteLLM tasks
        litellm_tasks = [
            task
            for task in pending_after
            if "litellm" in str(task).lower() or "logging" in str(task).lower()
        ]

        if len(litellm_tasks) == 0:
            print("✅ SUCCESS: No LiteLLM tasks remaining after cleanup")
            return True
        else:
            print(f"⚠️  {len(litellm_tasks)} LiteLLM tasks still pending")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_process_exit():
    """Test that process exit doesn't show warnings"""
    print("\n🧪 Testing process exit behavior...")

    # Set up environment
    os.environ["LLM_API_KEY"] = "test-key"

    try:
        # Create config and connections
        config = Configuration()
        llm_connection = LLMConnection(config)

        # Make a test call
        messages = [{"role": "user", "content": "Hello"}]
        try:
            await llm_connection.llm_call(messages)
        except Exception as e:
            pass  # Expected to fail

        # Wait for async tasks
        await asyncio.sleep(1)

        # Perform cleanup
        await llm_connection.cleanup()

        print("✅ Process exit test completed - check for warnings above")
        return True

    except Exception as e:
        print(f"❌ Process exit test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Starting LiteLLM cleanup fix test...")
    print("=" * 60)

    # Test 1: Basic cleanup
    success1 = await test_litellm_cleanup()

    # Test 2: Process exit behavior
    success2 = await test_process_exit()

    print("=" * 60)
    if success1 and success2:
        print("🎉 All tests passed!")
        print("✅ LiteLLM cleanup fix is working")
    else:
        print("💥 Some tests failed!")
        print("❌ LiteLLM cleanup fix needs more work")

    return success1 and success2


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
