# Contributing

Thank you for your interest in contributing to MCPOmni Connect! This project thrives on community contributions.

## Quick Links

- **Main Contributing Guide**: See [CONTRIBUTING.md](../../CONTRIBUTING.md) in the project root for complete guidelines
- **Issue Tracker**: [GitHub Issues](https://github.com/Abiorh001/mcp_omni_connect/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Abiorh001/mcp_omni_connect/discussions)

## Ways to Contribute

### 🐛 Bug Reports
Found a bug? Help us fix it:

1. Check [existing issues](https://github.com/Abiorh001/mcp_omni_connect/issues) first
2. Create a [new issue](https://github.com/Abiorh001/mcp_omni_connect/issues/new) with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### 💡 Feature Requests
Have an idea for improvement?

1. Check [discussions](https://github.com/Abiorh001/mcp_omni_connect/discussions) for similar ideas
2. Open a new discussion or issue describing:
   - The problem your feature would solve
   - Proposed solution
   - Alternative solutions considered

### 📝 Documentation
Help improve our documentation:

- Fix typos or unclear instructions
- Add examples or use cases
- Improve API documentation
- Translate documentation (future)

### 🔧 Code Contributions
Ready to code? Follow the [development setup guide](../../CONTRIBUTING.md#development-setup).

## Documentation Contributions

### Working with MkDocs

This documentation site uses MkDocs with Material theme:

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

### Documentation Structure

```
docs/
├── index.md              # Homepage
├── getting-started/       # Installation and quick start
├── configuration/         # Configuration guides
├── user-guide/           # Usage instructions
├── features/             # Feature deep-dives
├── advanced/             # Advanced topics
└── development/          # Development guides
```

### Writing Guidelines

!!! tip "Documentation Style"
    - Use clear, concise language
    - Include practical examples
    - Add code snippets where helpful
    - Use admonitions (tips, warnings, etc.) for important information
    - Test all code examples before committing

## Development Process

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/mcp_omni_connect.git
cd mcp_omni_connect
```

### 2. Set Up Development Environment

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install pre-commit hooks
pre-commit install
```

### 3. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Make Changes

- Write code following the project style
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 5. Submit Pull Request

1. Push your branch to your fork
2. Create a pull request with:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if UI changes)

## Code Standards

### Python Code
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for public functions
- Add unit tests for new features

### Documentation
- Use Markdown formatting
- Follow the existing structure
- Include code examples
- Test all examples before committing

## Testing

### Run Tests Locally

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_specific.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### Documentation Testing

```bash
# Test documentation build
mkdocs build --strict

# Serve and test locally
mkdocs serve
```

## Getting Help

Need help contributing?

- **Technical Questions**: [GitHub Discussions](https://github.com/Abiorh001/mcp_omni_connect/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/Abiorh001/mcp_omni_connect/issues)
- **Email**: abiolaadedayo1993@gmail.com

## Recognition

Contributors are recognized in:

- [CHANGELOG.md](../changelog.md) for their contributions
- GitHub contributors page
- Special thanks in release notes

Thank you for helping make MCPOmni Connect better! 🚀 