#!/usr/bin/env python3
"""
Setup script for MCP Omni Connect
"""

from setuptools import setup, find_packages
import os


# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "MCP Omni Connect - Advanced AI Agent Framework"


setup(
    name="mcpomni-connect",
    version="0.1.0",
    description="Advanced AI Agent Framework with Memory, Events, and Multi-Tool Orchestration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Abiola Adeshina",
    author_email="abiola@example.com",
    url="https://github.com/yourusername/mcpomni-connect",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "litellm>=1.0.0",
        "pydantic>=2.0.0",
        "redis>=4.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "pymysql>=1.0.0",
        "qdrant-client>=1.0.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.0.0",
        "rich>=13.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "jinja2>=3.0.0",
        "python-multipart>=0.0.6",
        "apscheduler>=3.10.0",
        "asyncio-mqtt>=0.11.0",
        "websockets>=11.0.0",
        "aiofiles>=23.0.0",
        "python-dotenv>=1.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
            "jinja2>=3.0.0",
            "python-multipart>=0.0.6",
        ],
    },
    entry_points={
        "console_scripts": [
            "omniagent=mcpomni_connect.cli:main",
            "omniagent-cli=mcpomni_connect.cli:cli_main",
            "omniagent-web=mcpomni_connect.web:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mcpomni_connect": ["*.txt", "*.md", "*.json", "*.yaml", "*.yml"],
    },
    zip_safe=False,
)
