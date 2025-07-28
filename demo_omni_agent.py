#!/usr/bin/env python3
"""
OmniAgent Interface Demo
Demonstrates both CLI and Web modes with examples
"""

import sys
import os
import argparse
import subprocess
import time


def print_banner():
    """Print a beautiful banner."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           🤖 OMNIGENT INTERFACE DEMO                        ║
║                                                                              ║
║  CLI Mode:  Interactive terminal interface with real-time chat              ║
║  Web Mode:  Modern FastAPI interface with streaming responses               ║
║                                                                              ║
║  Features:                                                                   ║
║  • Mathematical tools (area, perimeter, number analysis)                   ║
║  • Text processing (formatting, word count)                                ║
║  • System information and file system tools                                ║
║  • Memory management and session persistence                                ║
║  • Real-time event streaming                                               ║
║  • Backend switching (memory/event stores)                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


def demo_cli_mode():
    """Demonstrate CLI mode with example interactions."""
    print("\n🎯 CLI MODE DEMONSTRATION")
    print("=" * 50)

    print("""
Example CLI interactions:

1. Start the CLI interface:
   python run_omni_agent.py --mode cli

2. Available commands:
   /help              - Show help and commands
   /tools             - List available tools
   /memory            - Show memory information
   /events            - Show event information
   /history           - Show conversation history
   /clear             - Clear conversation history
   /save chat.json    - Save conversation to file
   /load chat.json    - Load conversation from file
   /switch memory:redis - Switch memory backend
   /quit              - Exit the interface

3. Example conversation:
   👤 You: Calculate the area of a rectangle with length 10 and width 5
   🤖 Agent: I'll calculate the area for you...
   ✅ Response: The area of the rectangle is 50 square units.

   👤 You: Format the result in uppercase
   🤖 Agent: Using the format_text tool...
   ✅ Response: THE AREA OF THE RECTANGLE IS 50 SQUARE UNITS.

   👤 You: /tools
   🔧 Available Tools:
   • calculate_area: Calculate the area of a rectangle.
   • calculate_perimeter: Calculate the perimeter of a rectangle.
   • format_text: Format text in different styles.
   • word_count: Count words in text.
   • system_info: Get basic system information.
   • analyze_numbers: Analyze a list of numbers.
   • list_directory: List contents of a directory.
""")


def demo_web_mode():
    """Demonstrate web mode with features."""
    print("\n🌐 WEB MODE DEMONSTRATION")
    print("=" * 50)

    print("""
Web Interface Features:

1. Start the web interface:
   python run_omni_agent.py --mode web

2. Access the interface:
   🌐 Main Interface: http://localhost:8000
   📚 API Docs: http://localhost:8000/docs
   🔧 Interactive API: http://localhost:8000/redoc

3. Web Interface Features:
   💬 Real-time streaming chat responses
   🔧 Interactive tool management panel
   📜 Conversation history viewer
   ⚙️ Backend configuration panel
   📊 Agent information display
   🎨 Modern responsive UI
   📡 Server-Sent Events for streaming

4. Example API Endpoints:
   POST /chat              - Send message with streaming response
   GET  /tools             - Get available tools
   GET  /history/{session} - Get conversation history
   POST /clear-history/{session} - Clear history
   GET  /agent-info        - Get agent information
   POST /switch-backend    - Switch memory/event backends

5. Real-time Features:
   • Streaming responses as they're generated
   • Live typing indicators
   • Real-time tool execution
   • Session management
   • Event monitoring
""")


def check_dependencies():
    """Check if all dependencies are installed."""
    print("\n🔍 Checking Dependencies...")

    # Check basic dependencies
    try:
        import mcpomni_connect

        print("✅ OmniAgent core dependencies")
    except ImportError:
        print("❌ OmniAgent core dependencies missing")
        return False

    # Check web dependencies
    try:
        import fastapi
        import uvicorn
        import jinja2

        print("✅ FastAPI web dependencies")
    except ImportError:
        print("⚠️  FastAPI dependencies not installed (web mode will not work)")
        print("   Install with: pip install fastapi uvicorn jinja2")

    return True


def install_web_dependencies():
    """Install web dependencies."""
    print("\n📦 Installing Web Dependencies...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "fastapi",
                "uvicorn[standard]",
                "jinja2",
                "python-multipart",
            ],
            check=True,
        )
        print("✅ Web dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install web dependencies")
        return False


def run_quick_test():
    """Run a quick test to ensure everything works."""
    print("\n🧪 Running Quick Test...")

    try:
        # Test CLI mode import
        from omni_agent_interface import OmniAgentInterface

        print("✅ OmniAgent Interface imports successfully")

        # Test web mode import
        import fastapi

        print("✅ FastAPI imports successfully")

        print("✅ All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="OmniAgent Interface Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_omni_agent.py                    # Show demo information
  python demo_omni_agent.py --test             # Run quick test
  python demo_omni_agent.py --install-web      # Install web dependencies
  python demo_omni_agent.py --cli              # Start CLI demo
  python demo_omni_agent.py --web              # Start web demo
        """,
    )

    parser.add_argument("--test", action="store_true", help="Run quick test")
    parser.add_argument(
        "--install-web", action="store_true", help="Install web dependencies"
    )
    parser.add_argument("--cli", action="store_true", help="Start CLI demo")
    parser.add_argument("--web", action="store_true", help="Start web demo")

    args = parser.parse_args()

    print_banner()

    if args.install_web:
        install_web_dependencies()
        return

    if args.test:
        if not check_dependencies():
            print("❌ Dependency check failed")
            return
        run_quick_test()
        return

    if args.cli:
        print("🚀 Starting CLI Demo...")
        subprocess.run([sys.executable, "run_omni_agent.py", "--mode", "cli"])
        return

    if args.web:
        print("🚀 Starting Web Demo...")
        subprocess.run([sys.executable, "run_omni_agent.py", "--mode", "web"])
        return

    # Show demo information
    print("📋 Available Demo Options:")
    print("  --test         - Run quick dependency test")
    print("  --install-web  - Install web dependencies")
    print("  --cli          - Start CLI mode demo")
    print("  --web          - Start web mode demo")
    print()

    demo_cli_mode()
    demo_web_mode()

    print("\n🎯 To get started:")
    print("  1. Run: python demo_omni_agent.py --test")
    print("  2. For CLI: python demo_omni_agent.py --cli")
    print("  3. For Web: python demo_omni_agent.py --web")
    print("  4. Install web deps: python demo_omni_agent.py --install-web")


if __name__ == "__main__":
    main()
