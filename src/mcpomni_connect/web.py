#!/usr/bin/env python3
"""
OmniAgent Web Interface Entry Point
Provides web interface for OmniAgent.
"""

import uvicorn
import sys
from pathlib import Path

# Add the examples directory to the path for the web server
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "examples"))


def main():
    """Main entry point for web interface."""
    try:
        from web_server import OmniAgentWebServer

        server = OmniAgentWebServer()
        server.run()
    except ImportError as e:
        print(f"❌ Error importing web server: {e}")
        print("💡 Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Web server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
