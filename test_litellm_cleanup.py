#!/usr/bin/env python3
"""
Test script to verify LiteLLM cleanup fix
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcpomni_connect.llm import LLMConnection
from mcpomni_connect.client import Configuration
from mcpomni_connect.utils import logger


async def test_litellm_cleanup():
    """Test that LiteLLM cleanup works properly"""
    print("🧪 Testing LiteLLM cleanup...")

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

        # Perform cleanup
        print("🧹 Performing cleanup...")
        await llm_connection.cleanup()

        # Check for pending tasks after cleanup
        pending_after = [
            task
            for task in asyncio.all_tasks()
            if not task.done() and task != asyncio.current_task()
        ]
        print(f"📊 Pending tasks after cleanup: {len(pending_after)}")

        if len(pending_after) == 0:
            print("✅ Cleanup successful - no pending tasks remaining")
        else:
            print(f"⚠️  Some tasks still pending: {len(pending_after)}")
            for task in pending_after:
                print(f"   - {task}")

        return len(pending_after) == 0

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Starting LiteLLM cleanup test...")

    success = await test_litellm_cleanup()

    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed!")

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
