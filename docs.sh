#!/bin/bash

# Documentation management script for MCPOmni Connect

set -e

case "${1:-help}" in
    "serve")
        echo "🚀 Starting MkDocs development server..."
        uv run mkdocs serve --dev-addr=127.0.0.1:8080
        ;;
    "build")
        echo "🔨 Building documentation..."
        uv run mkdocs build
        echo "✅ Documentation built successfully!"
        echo "📁 Static files are in: ./site/"
        ;;
    "install")
        echo "📦 Installing documentation dependencies..."
        uv sync --group docs
        echo "✅ Documentation dependencies installed!"
        ;;
    "clean")
        echo "🧹 Cleaning build artifacts..."
        rm -rf site/
        echo "✅ Build artifacts cleaned!"
        ;;
    "deploy")
        echo "🚀 Building and deploying documentation..."
        uv run mkdocs gh-deploy --clean
        echo "✅ Documentation deployed to GitHub Pages!"
        ;;
    "help"|*)
        echo "📖 MCPOmni Connect Documentation Manager"
        echo ""
        echo "Usage: ./docs.sh [command]"
        echo ""
        echo "Commands:"
        echo "  serve    - Start development server (http://127.0.0.1:8080)"
        echo "  build    - Build static documentation"
        echo "  install  - Install documentation dependencies"
        echo "  clean    - Clean build artifacts"
        echo "  deploy   - Deploy to GitHub Pages"
        echo "  help     - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./docs.sh serve     # Start development server"
        echo "  ./docs.sh build     # Build for production"
        echo "  ./docs.sh deploy    # Deploy to GitHub Pages"
        ;;
esac 