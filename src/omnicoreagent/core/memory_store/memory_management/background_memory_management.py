import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Dict, Any
from omnicoreagent.core.memory_store.memory_management.memory_manager import (
    MemoryManager,
)
from omnicoreagent.core.memory_store.memory_router import MemoryRouter
from omnicoreagent.core.utils import logger


_GLOBAL_THREAD_POOL = ThreadPoolExecutor(max_workers=4)


class BackgroundMemoryManager:
    def __init__(
        self,
        session_id: str,
        agent_name: str,
        llm_connection: Callable[[], Any],
        memory_store_type: str = "in_memory",
    ):
        self.session_id = session_id
        self.agent_name = agent_name
        self.llm_connection = llm_connection
        self.memory_store_type = memory_store_type
        self.memory_router = MemoryRouter(memory_store_type=self.memory_store_type)
        self._running = False

    def start(self, messages: List[Dict[str, Any]]):
        if not self._running:
            self._running = True
            _GLOBAL_THREAD_POOL.submit(self._process_both_memories, messages)

    def stop(self):
        self._running = False

    def _process_both_memories(self, messages: List[Dict[str, Any]]):
        """Create a dedicated loop inside this thread and run memory work."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self._process_memory(messages, "episodic"),
                    self._process_memory(messages, "long_term"),
                )
            )
        except Exception:
            logger.exception("Error in background memory processing")
        finally:
            try:
                loop.close()
            except Exception:
                pass

    async def _process_memory(self, messages: List[Dict[str, Any]], memory_type: str):
        memory_manager = MemoryManager(
            agent_name=self.agent_name,
            memory_type=memory_type,
            is_background=True,
            llm_connection=self.llm_connection,
        )

        if not memory_manager.vector_db or not memory_manager.vector_db.enabled:
            logger.debug(f"{memory_type} vector db not enabled, skipping")
            return

        try:
            await memory_manager.process_conversation_memory(
                messages=messages,
                session_id=self.session_id,
                add_last_processed_messages=self.memory_router.set_last_processed_messages,
                get_last_processed_messages=self.memory_router.get_last_processed_messages,
                llm_connection=self.llm_connection,
            )
        except Exception:
            logger.exception("Error while processing memory(type=%s)", memory_type)


def fire_and_forget_memory_processing(
    session_id: str,
    agent_name: str,
    messages: List[Dict[str, Any]],
    memory_store_type: str,
    llm_connection: Callable[[], Any],
):
    """Called from main loop to trigger background memory processing immediately."""
    manager = BackgroundMemoryManager(
        session_id=session_id,
        agent_name=agent_name,
        memory_store_type=memory_store_type,
        llm_connection=llm_connection,
    )

    manager.start(messages)
