# MCPOmni Connect Documentation

This directory contains the MkDocs-based documentation for MCPOmni Connect.

## 🚀 Quick Start

### View Documentation Locally

```bash
# Install dependencies
./docs.sh install

# Start development server
./docs.sh serve
```

Visit: http://127.0.0.1:8080

### Build Documentation

```bash
# Build static site
./docs.sh build

# Output will be in ./site/
```

## 📁 Documentation Structure

```
docs/
├── index.md                    # Homepage
├── getting-started/            # Installation & Quick Start
│   ├── installation.md
│   └── quick-start.md
├── configuration/              # Configuration Guides
│   ├── configuration-guide.md
│   ├── transport-types.md
│   ├── authentication.md
│   ├── llm-providers.md
│   └── troubleshooting.md
├── user-guide/                 # Usage Instructions
│   ├── basic-usage.md
│   ├── operation-modes.md
│   ├── commands.md
│   ├── memory-management.md
│   └── prompt-management.md
├── features/                   # Feature Deep-dives
│   ├── agent-system.md
│   ├── tool-orchestration.md
│   ├── resource-management.md
│   └── token-management.md
├── advanced/                   # Advanced Topics
│   ├── architecture.md
│   ├── api-reference.md
│   └── examples.md
├── development/                # Development Guides
│   ├── contributing.md
│   └── testing.md
└── changelog.md               # Version History
```

## ✨ Features

- **Material Design**: Modern, responsive theme
- **Search**: Full-text search across all documentation
- **Code Highlighting**: Syntax highlighting for all languages
- **Mermaid Diagrams**: Architecture and workflow diagrams
- **Tabbed Content**: Organized content with tabs
- **Admonitions**: Tips, warnings, and info boxes
- **Git Integration**: Last modified dates from git history

## 🛠️ Available Commands

Use the `docs.sh` script for common tasks:

```bash
./docs.sh serve     # Start development server
./docs.sh build     # Build static documentation
./docs.sh install   # Install dependencies
./docs.sh clean     # Clean build artifacts
./docs.sh deploy    # Deploy to GitHub Pages
./docs.sh help      # Show help
```

## 📝 Writing Documentation

### Markdown Guidelines

- Use clear, concise language
- Include practical examples
- Add code snippets where helpful
- Use proper heading hierarchy (H1 → H2 → H3)
- Include cross-references with relative links

### Code Examples

Use fenced code blocks with language specification:

```bash
# Shell commands
mcpomni_connect --help
```

```json
{
    "LLM": {
        "provider": "openai",
        "model": "gpt-4o-mini"
    }
}
```

```python
# Python code
import mcpomni_connect
```

### Admonitions

Use admonitions for important information:

```markdown
!!! tip "Helpful Tip"
    This is a helpful tip for users.

!!! warning "Important Warning"
    This is something users should be careful about.

!!! failure "Common Error"
    This describes a common error and its solution.
```

### Tabbed Content

Organize related content with tabs:

```markdown
=== "Option A"
    Content for option A

=== "Option B"
    Content for option B
```

## 🎯 Content Guidelines

### Target Audience

- **Beginners**: Clear installation and setup instructions
- **Intermediate Users**: Comprehensive configuration guides
- **Advanced Users**: Deep technical details and architecture
- **Developers**: Contributing guidelines and API reference

### Content Principles

1. **Clarity**: Write for understanding, not to impress
2. **Examples**: Every concept should have a practical example
3. **Completeness**: Cover edge cases and gotchas
4. **Currency**: Keep information up-to-date with releases
5. **Accessibility**: Use inclusive language and clear structure

## 🔄 Deployment

### GitHub Pages (Automated)

Documentation automatically deploys to GitHub Pages on:
- Push to `main` branch
- Manual trigger via GitHub Actions

### Manual Deployment

```bash
# Deploy to GitHub Pages
./docs.sh deploy
```

### Local Preview

Always preview changes locally before committing:

```bash
./docs.sh serve
# Visit http://127.0.0.1:8080
```

## 🐛 Troubleshooting

### Build Errors

```bash
# Check for broken links
./docs.sh build

# Common issues:
# - Missing referenced files
# - Broken internal links
# - Invalid Markdown syntax
```

### Missing Dependencies

```bash
# Reinstall documentation dependencies
./docs.sh install

# Or manually:
uv sync --group docs
```

### Port Conflicts

If port 8080 is busy:

```bash
# Use different port
uv run mkdocs serve --dev-addr=127.0.0.1:8090
```

## 📚 Resources

- **MkDocs**: [Official Documentation](https://www.mkdocs.org/)
- **Material Theme**: [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- **Markdown Guide**: [CommonMark Spec](https://commonmark.org/)
- **Mermaid Diagrams**: [Mermaid Documentation](https://mermaid.js.org/)

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Write** your documentation
4. **Test** locally with `./docs.sh serve`
5. **Submit** a pull request

See [Contributing Guide](development/contributing.md) for detailed instructions.

---

**Questions?** Open an issue or start a discussion on GitHub! 