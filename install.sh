#!/bin/bash

# OmniAgent Installation Script
# This script installs the MCP Omni Connect package and makes CLI/web interfaces available

set -e

echo "🚀 Installing OmniAgent (MCP Omni Connect)..."
echo "================================================"

# Check if Python 3.8+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not available. Please install pip first."
    exit 1
fi

echo "✅ pip3 is available"

# Install the package in development mode
echo "📦 Installing package in development mode..."
pip3 install -e .

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Package installed successfully!"
else
    echo "❌ Installation failed!"
    exit 1
fi

# Test if the CLI commands are available
echo "🧪 Testing CLI commands..."

if command -v omniagent &> /dev/null; then
    echo "✅ 'omniagent' command is available"
else
    echo "❌ 'omniagent' command not found"
fi

if command -v omniagent-cli &> /dev/null; then
    echo "✅ 'omniagent-cli' command is available"
else
    echo "❌ 'omniagent-cli' command not found"
fi

if command -v omniagent-web &> /dev/null; then
    echo "✅ 'omniagent-web' command is available"
else
    echo "❌ 'omniagent-web' command not found"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo "================================================"
echo ""
echo "📋 Available Commands:"
echo "  omniagent --mode cli    - Start CLI interface"
echo "  omniagent --mode web    - Start web interface"
echo "  omniagent-cli           - Start CLI interface directly"
echo "  omniagent-web           - Start web interface directly"
echo ""
echo "💡 Quick Start:"
echo "  1. Run: omniagent-cli"
echo "  2. Type: /help"
echo "  3. Start chatting with the agent!"
echo ""
echo "🌐 Web Interface:"
echo "  1. Run: omniagent-web"
echo "  2. Open: http://localhost:8000"
echo "  3. Start chatting in the web interface!"
echo ""
echo "📚 Documentation:"
echo "  - README.md: Project overview and features"
echo "  - examples/: Example scripts and usage"
echo "  - docs/: Detailed documentation"
echo ""
echo "🔧 Development:"
echo "  - Install dev dependencies: pip install -e .[dev]"
echo "  - Run tests: pytest"
echo "  - Format code: black src/"
echo ""
echo "Happy coding! 🤖" 