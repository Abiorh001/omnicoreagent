#!/usr/bin/env python3
import asyncio

from mcpomni_connect.main import main
from mcpomni_connect.utils import logger

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Error in main: {e}")
