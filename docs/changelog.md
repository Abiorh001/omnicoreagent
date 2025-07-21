# Changelog

All notable changes to MCPOmni Connect will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive MkDocs documentation site
- Enhanced configuration guides with visual examples
- Interactive command reference

### Improved
- Documentation structure and navigation
- Code examples and usage patterns
- Troubleshooting guides


## [0.1.17] - 2025-05-28

### Added
- OAuth Authentication Support:
  - Added OAuth 2.0 authentication flow for MCP servers
  - Support for multiple authentication methods:
    - OAuth 2.0
    - Bearer token
    - Custom headers
  - Flexible authentication configuration in server settings
  - Secure credential management
- Enhanced Server Configuration:
  - Updated server configuration format to support OAuth
  - Added authentication method specification
  - Improved server connection security
  - Better error handling for authentication failures

### Changed
- Updated server configuration examples to include OAuth support
- Enhanced documentation for authentication methods
- Improved security section in README
- Updated server management commands documentation

### Fixed
- Improved authentication error handling
- Enhanced security documentation
- Updated configuration validation for authentication methods

## [0.1.16] - 2025-05-16

### Added
- New Streamable HTTP Transport:
  - Added support for streamable HTTP transport protocol
  - Efficient data streaming capabilities
  - Configurable timeout and read timeout settings
  - Header support for authentication and custom configurations
- Dynamic Server Management:
  - New `/add_servers:<config.json>` command to add one or more servers
  - New `/remove_server:<server_name>` command to remove servers
  - Support for adding multiple servers from a single configuration file
  - Real-time server capability updates after adding/removing servers
- Enhanced Server Configuration:
  - Added streamable HTTP server configuration examples
  - Updated documentation for new transport type
  - Improved server management commands documentation

### Changed
- Updated README with new server management commands
- Enhanced server configuration examples to include streamable HTTP
- Improved documentation for transport protocols
- Updated interactive commands section with new server management features

### Fixed
- Improved server connection handling
- Enhanced error messages for server management commands
- Updated documentation formatting for consistency

## [0.1.15] - 2025-05-05

### Added
- Token & Usage Management:
  - `/api_stats` command to view total tokens used, total requests, response tokens, and number of requests
  - Ability to set limits for total requests and total token usage; agent will automatically stop when limits are reached
  - Configurable tool call timeout and max steps; agent will terminate if these thresholds are exceeded
- Developer Integration Enhancements:
  - Expanded documentation and examples for using MCPOmni Connect as a backend Python library
  - FastAPI example for building custom API servers with support for both ReAct Agent and Orchestrator Agent modes
  - Minimal code snippets for custom MCP client integration in Python projects
- FastAPI API Documentation:
  - Documented `/chat/agent_chat` endpoint with request/response examples
  - Added web client usage instructions for `examples/index.html`
- Environment Variables Reference:
  - Added table of supported environment variables and their descriptions in the README
- Typos and Documentation Improvements:
  - Fixed typos and improved clarity throughout the README
  - Clarified configuration options and usage instructions

### Changed
- Updated server configuration examples to clarify usage of `tool_call_timeout`, `max_steps`, `request_limit`, and `total_tokens_limit`
- Improved README structure with new "Examples", "Developer Integration", "Token & Usage Management", and "FastAPI API Endpoints" sections
- Enhanced error handling and documentation for agent termination on reaching usage limits

### Fixed
- Corrected typos in documentation and configuration comments
- Improved consistency in code examples and documentation formatting

## [0.1.14] - 2025-04-18

### Added
- DeepSeek model integration with full support for tool execution
- New Orchestrator Agent Mode:
  - Advanced planning for complex multi-step tasks
  - Strategic delegation across multiple MCP servers
  - Intelligent agent coordination and communication
  - Parallel task execution capabilities
  - Dynamic resource allocation
  - Sophisticated workflow management
  - Real-time progress monitoring
  - Adaptive task prioritization
- Client-Side Sampling Support:
  - Dynamic sampling configuration from client
  - Flexible LLM response generation
  - Customizable sampling parameters
  - Real-time sampling adjustments
- Chat History File Storage:
  - Save complete chat conversations to files
  - Load previous conversations from saved files
  - Continue conversations from where you left off
  - File-based backup and restoration
  - Persistent chat history across sessions

### Changed
- Enhanced Mode System with three distinct modes:
  - Chat Mode (Default)
  - Autonomous Mode
  - Orchestrator Mode
- Updated AI model integration documentation
- Improved chat history management system
- Enhanced server configuration options for new features

### Fixed
- Improved mode switching reliability
- Enhanced chat history persistence
- Optimized orchestrator mode performance

## [0.1.13] - 2025-04-14

### Added
- Gemini model integration with full support for tool execution
- Redis-powered memory persistence:
  - Conversation history tracking
  - State management across sessions
  - Configurable memory retention
  - Efficient data serialization and retrieval
  - Multi-server memory synchronization
- Agentic Mode capabilities:
  - Autonomous task execution without human intervention
  - Advanced reasoning and decision-making
  - Complex task decomposition and handling
  - Self-guided tool selection and execution
- Advanced prompt features:
  - Dynamic prompt discovery across servers
  - JSON and key-value format support
  - Nested argument structures
  - Automatic type conversion and validation
- Comprehensive troubleshooting guide with:
  - Common issues and solutions
  - Debug mode instructions
  - Support workflow
- Detailed architecture documentation with component breakdown
- Advanced server configuration examples for:
  - Multiple transport protocols
  - Various LLM providers
  - Docker integration

### Changed
- Enhanced installation process with UV package manager
- Improved development quick start guide
- Updated server configuration format to support multiple LLM providers
- Expanded model support documentation for all providers
- Enhanced security documentation with explicit user control details
- Restructured README with clearer sections and examples

### Fixed
- Standardized command formatting in documentation
- Improved code block consistency
- Enhanced example clarity and completeness

## [0.1.1] - 2025-03-27

### Added
- Comprehensive Security & Privacy section with detailed subsections:
  - Explicit User Control
  - Data Protection
  - Privacy-First Approach
  - Secure Communication
- Detailed Model Support section covering:
  - OpenAI Models
  - OpenRouter Models
  - Groq Models
  - Universal Model Support through ReAct Agent
- Structured Testing section with:
  - Multiple test running options
  - Test directory structure
  - Coverage reporting instructions
- Support for additional LLM providers:
  - OpenRouter integration
  - Groq integration
  - Universal model support through ReAct Agent

### Changed
- Improved AI-Powered Intelligence section:
  - Added support for multiple LLM providers (OpenAI, OpenRouter, Groq)
  - Added detailed ReAct Agent capabilities for models without function calling
  - Fixed typos in "seamless"
- Enhanced Server Configuration Examples:
  - Added support for multiple LLM providers
  - Updated model examples
  - Added comments for supported providers
- Updated Prerequisites:
  - Changed Python version requirement from 3.12+ to 3.10+
  - Updated API key requirements to support multiple providers
- Improved environment variable setup:
  - Changed from OPENAI_API_KEY to LLM_API_KEY for broader provider support
  - Added support for multiple API keys in .env file

### Fixed
- Typos in model integration descriptions
- Formatting issues in various sections
- Inconsistent capitalization in headers
- Fixed typo in "client" command (was "cient")
- Improved code block formatting and consistency

### Removed
- Redundant security information
- Simplified test section
- Removed specific OpenAI model references in favor of provider-agnostic examples
- Removed redundant prompt examples in favor of more structured documentation

## [0.1.0] - 2025-03-21
- Initial release
- Basic MCP server integration
- OpenAI model support
- Core CLI functionality


---

## Release Process

MCPOmni Connect follows these practices for releases:

1. **Semantic Versioning**: We use [SemVer](https://semver.org/) for version numbers
2. **Regular Releases**: New features are released regularly with proper testing
3. **Backwards Compatibility**: We maintain backwards compatibility within major versions
4. **Security Updates**: Security fixes are released immediately as patch versions

## Getting Updates

To update to the latest version:

```bash
# Using UV (recommended)
uv sync --upgrade

# Using pip
pip install --upgrade mcpomni-connect

# Check your version
mcpomni_connect --version
```

## Contributing to Releases

We welcome contributions! See our [Contributing Guide](development/contributing.md) for:

- How to submit bug reports
- Feature request process
- Development setup
- Testing requirements
- Release criteria
