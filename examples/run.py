#!/usr/bin/env python3
import asyncio

# TOP-LEVEL IMPORTS (Recommended for most use cases)
from omnicoreagent import main, logger

# LOW-LEVEL IMPORTS (Alternative approach for advanced users)
# from omnicoreagent.mcp_omni_connect.main import main
# from omnicoreagent.core.utils import logger

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Error in main: {e}")
