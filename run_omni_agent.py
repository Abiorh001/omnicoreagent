#!/usr/bin/env python3
"""
OmniAgent Interface Runner
Simple script to run the OmniAgent interface in CLI or Web mode
"""

import sys
import os
import argparse
import subprocess

# Add examples to path
sys.path.append(os.path.join(os.path.dirname(__file__), "examples"))


def check_dependencies(mode):
    """Check if required dependencies are installed."""
    if mode == "web":
        try:
            import fastapi
            import uvicorn
            import jinja2

            print("✅ FastAPI dependencies found")
        except ImportError as e:
            print("❌ Missing FastAPI dependencies")
            print("Install with: pip install fastapi uvicorn jinja2")
            return False
    return True


def run_web_mode():
    """Run web mode using the separate web server."""
    web_server_path = os.path.join("examples", "web_server.py")

    if not os.path.exists(web_server_path):
        print(f"❌ Web server file not found: {web_server_path}")
        return False

    print("🌐 Starting FastAPI web interface...")
    print("📱 Web interface will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔄 Starting web server...")

    try:
        subprocess.run([sys.executable, web_server_path], check=True)
        return True
    except KeyboardInterrupt:
        print("\n👋 Web server stopped")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Web server error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="OmniAgent Interface Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_omni_agent.py                    # Run in CLI mode (default)
  python run_omni_agent.py --mode cli         # Run in CLI mode
  python run_omni_agent.py --mode web         # Run in Web mode with FastAPI
  python run_omni_agent.py --help             # Show this help

Web Mode Features:
  🌐 Modern FastAPI backend
  📡 Real-time streaming responses
  🎨 Beautiful responsive UI
  🔧 Interactive tool management
  📊 Real-time event monitoring
  💾 Session management
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["cli", "web"],
        default="cli",
        help="Interface mode: cli (terminal) or web (FastAPI browser interface)",
    )

    args = parser.parse_args()

    print("🚀 Starting OmniAgent Interface...")
    print(f"📱 Mode: {args.mode.upper()}")

    if args.mode == "web":
        if not check_dependencies("web"):
            sys.exit(1)

        if not run_web_mode():
            sys.exit(1)
        return

    # CLI mode
    try:
        from omni_agent_interface import OmniAgentInterface
        import asyncio

        interface = OmniAgentInterface(mode=args.mode)
        asyncio.run(interface.run())

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(
            "💡 Make sure you're in the correct directory and all dependencies are installed"
        )
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    main()
