import json
import inspect
from typing import Dict, List, Any, Optional
from pathlib import Path
from .local_tools_registry import ToolRegistry


class DocumentationGenerator:
    """Generate comprehensive documentation for tools"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.template_dir = Path(__file__).parent / "templates"
        self.output_dir = Path("docs/tools")
    
    def generate_markdown_docs(self, output_file: str = "tools_documentation.md") -> str:
        """Generate markdown documentation for all tools"""
        tools = self.tool_registry.list_tools()
        
        if not tools:
            return "# Tool Documentation\n\nNo tools registered."
        
        docs = self._generate_header()
        docs += self._generate_toc(tools)
        docs += self._generate_tool_details(tools)
        docs += self._generate_examples_section(tools)
        docs += self._generate_api_reference(tools)
        
        # Save to file
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / output_file
        with open(output_path, 'w') as f:
            f.write(docs)
        
        return docs
    
    def _generate_header(self) -> str:
        """Generate documentation header"""
        return """# Tool Documentation

This document provides comprehensive documentation for all available tools in the MCPOmni Connect framework.

## Overview

Tools are the building blocks that enable agents to interact with external systems, process data, and perform various tasks. Each tool has a well-defined interface with input parameters and output specifications.

## Quick Start

To use a tool in your agent:

```python
from mcpomni_connect.agents.tools.local_tools_integration import execute_local_tool

# Execute a tool
result = await execute_local_tool("tool_name", {"param1": "value1"})
```

## Tool Categories

Tools are organized into the following categories:

- **Data Processing**: Tools for data transformation and manipulation
- **File Operations**: Tools for file reading, writing, and management
- **Web Scraping**: Tools for fetching and extracting web content
- **Math Operations**: Tools for mathematical calculations and statistics
- **Custom Tools**: User-defined tools for specific use cases

"""
    
    def _generate_toc(self, tools: List[Any]) -> str:
        """Generate table of contents"""
        toc = "## Table of Contents\n\n"
        
        # Group tools by category
        categories = self._categorize_tools(tools)
        
        for category, category_tools in categories.items():
            toc += f"### {category}\n"
            for tool in category_tools:
                toc += f"- [{tool.name}](#{tool.name.lower().replace(' ', '-')})\n"
            toc += "\n"
        
        return toc
    
    def _categorize_tools(self, tools: List[Any]) -> Dict[str, List[Any]]:
        """Categorize tools based on their names and descriptions"""
        categories = {
            "Data Processing": [],
            "File Operations": [],
            "Web Scraping": [],
            "Math Operations": [],
            "Custom Tools": []
        }
        
        for tool in tools:
            tool_name = tool.name.lower()
            tool_desc = tool.description.lower()
            
            if any(keyword in tool_name or keyword in tool_desc for keyword in ["csv", "json", "filter", "data"]):
                categories["Data Processing"].append(tool)
            elif any(keyword in tool_name or keyword in tool_desc for keyword in ["file", "read", "write", "list"]):
                categories["File Operations"].append(tool)
            elif any(keyword in tool_name or keyword in tool_desc for keyword in ["url", "fetch", "web", "http"]):
                categories["Web Scraping"].append(tool)
            elif any(keyword in tool_name or keyword in tool_desc for keyword in ["add", "multiply", "calculate", "statistics", "math"]):
                categories["Math Operations"].append(tool)
            else:
                categories["Custom Tools"].append(tool)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _generate_tool_details(self, tools: List[Any]) -> str:
        """Generate detailed documentation for each tool"""
        docs = "## Tool Details\n\n"
        
        categories = self._categorize_tools(tools)
        
        for category, category_tools in categories.items():
            docs += f"### {category}\n\n"
            
            for tool in category_tools:
                docs += self._generate_tool_section(tool)
                docs += "\n"
        
        return docs
    
    def _generate_tool_section(self, tool: Any) -> str:
        """Generate documentation section for a single tool"""
        section = f"#### {tool.name}\n\n"
        section += f"{tool.description}\n\n"
        
        # Function signature
        if hasattr(tool, 'function') and tool.function:
            sig = inspect.signature(tool.function)
            section += "**Signature:**\n"
            section += f"```python\n{tool.name}{sig}\n```\n\n"
        
        # Parameters
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            section += "**Parameters:**\n\n"
            section += "| Parameter | Type | Required | Description |\n"
            section += "|-----------|------|----------|-------------|\n"
            
            schema = tool.inputSchema
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            for param_name, param_info in properties.items():
                param_type = param_info.get('type', 'any')
                is_required = param_name in required
                description = param_info.get('description', 'No description available')
                
                section += f"| `{param_name}` | `{param_type}` | {'Yes' if is_required else 'No'} | {description} |\n"
            
            section += "\n"
        
        # Return value
        section += "**Returns:**\n"
        section += "The result of the tool execution.\n\n"
        
        # Example usage
        section += "**Example:**\n"
        section += "```python\n"
        section += f"# Execute {tool.name}\n"
        
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            properties = tool.inputSchema.get('properties', {})
            example_params = {}
            
            for param_name, param_info in properties.items():
                param_type = param_info.get('type', 'string')
                if param_type == 'string':
                    example_params[param_name] = f'"{param_name}_value"'
                elif param_type == 'number':
                    example_params[param_name] = '42'
                elif param_type == 'integer':
                    example_params[param_name] = '42'
                elif param_type == 'boolean':
                    example_params[param_name] = 'True'
                else:
                    example_params[param_name] = 'None'
            
            section += f"result = await execute_local_tool('{tool.name}', {json.dumps(example_params, indent=2)})\n"
        else:
            section += f"result = await execute_local_tool('{tool.name}', {{}})\n"
        
        section += "print(result)\n"
        section += "```\n\n"
        
        return section
    
    def _generate_examples_section(self, tools: List[Any]) -> str:
        """Generate examples section with common use cases"""
        examples = "## Common Use Cases\n\n"
        
        # Data processing example
        examples += "### Data Processing Pipeline\n\n"
        examples += "```python\n"
        examples += "# Convert CSV to JSON, filter data, and convert back\n"
        examples += "csv_data = 'name,age\\nJohn,30\\nJane,25\\nBob,35'\n\n"
        examples += "# Step 1: Convert to JSON\n"
        examples += "json_data = await execute_local_tool('csv_to_json', {\n"
        examples += '    "csv_data": csv_data\n'
        examples += "})\n\n"
        examples += "# Step 2: Filter data\n"
        examples += "filtered_data = await execute_local_tool('filter_data', {\n"
        examples += '    "data": json_data,\n'
        examples += '    "field": "age",\n'
        examples += '    "value": "30",\n'
        examples += '    "operator": "gt"\n'
        examples += "})\n\n"
        examples += "# Step 3: Convert back to CSV\n"
        examples += "result_csv = await execute_local_tool('json_to_csv', {\n"
        examples += '    "json_data": filtered_data\n'
        examples += "})\n"
        examples += "```\n\n"
        
        # File operations example
        examples += "### File Processing\n\n"
        examples += "```python\n"
        examples += "# Read a file, process content, and write to new file\n"
        examples += "content = await execute_local_tool('read_text_file', {\n"
        examples += '    "file_path": "input.txt"\n'
        examples += "})\n\n"
        examples += "# Process the content (example: convert to uppercase)\n"
        examples += "processed_content = content.upper()\n\n"
        examples += "# Write to new file\n"
        examples += "await execute_local_tool('write_text_file', {\n"
        examples += '    "file_path": "output.txt",\n'
        examples += '    "content": processed_content\n'
        examples += "})\n"
        examples += "```\n\n"
        
        # Web scraping example
        examples += "### Web Scraping\n\n"
        examples += "```python\n"
        examples += "# Fetch web content and extract text\n"
        examples += "html_content = await execute_local_tool('fetch_url', {\n"
        examples += '    "url": "https://example.com"\n'
        examples += "})\n\n"
        examples += "# Extract text from HTML\n"
        examples += "text_content = await execute_local_tool('extract_text', {\n"
        examples += '    "html_content": html_content\n'
        examples += "})\n"
        examples += "```\n\n"
        
        return examples
    
    def _generate_api_reference(self, tools: List[Any]) -> str:
        """Generate API reference section"""
        api_ref = "## API Reference\n\n"
        
        api_ref += "### Tool Registry\n\n"
        api_ref += "The tool registry provides methods to manage and execute tools:\n\n"
        api_ref += "```python\n"
        api_ref += "from mcpomni_connect.agents.tools.local_tools_registry import ToolRegistry\n\n"
        api_ref += "# Create registry\n"
        api_ref += "registry = ToolRegistry()\n\n"
        api_ref += "# Register a tool\n"
        api_ref += "@registry.register(name='my_tool', description='My custom tool')\n"
        api_ref += "def my_tool(param1: str, param2: int) -> str:\n"
        api_ref += '    return f"Processed: {param1} and {param2}"\n\n'
        api_ref += "# Execute a tool\n"
        api_ref += "result = await registry.execute_tool('my_tool', {'param1': 'test', 'param2': 42})\n\n"
        api_ref += "# List all tools\n"
        api_ref += "tools = registry.list_tools()\n"
        api_ref += "```\n\n"
        
        api_ref += "### Tool Integration\n\n"
        api_ref += "```python\n"
        api_ref += "from mcpomni_connect.agents.tools.local_tools_integration import LocalToolsIntegration\n\n"
        api_ref += "# Create integration\n"
        api_ref += "integration = LocalToolsIntegration()\n\n"
        api_ref += "# Get available tools\n"
        api_ref += "tools = integration.get_available_tools()\n\n"
        api_ref += "# Execute a tool\n"
        api_ref += "result = await integration.execute_tool('tool_name', {'param': 'value'})\n"
        api_ref += "```\n\n"
        
        return api_ref
    
    def generate_json_schema(self, output_file: str = "tools_schema.json") -> str:
        """Generate JSON schema for all tools"""
        tools = self.tool_registry.list_tools()
        
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Tool Schema",
            "description": "JSON schema for all available tools",
            "type": "object",
            "properties": {},
            "definitions": {}
        }
        
        for tool in tools:
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema["properties"][tool.name] = {
                    "type": "object",
                    "description": tool.description,
                    "properties": tool.inputSchema.get('properties', {}),
                    "required": tool.inputSchema.get('required', []),
                    "additionalProperties": tool.inputSchema.get('additionalProperties', True)
                }
        
        # Save to file
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / output_file
        with open(output_path, 'w') as f:
            json.dump(schema, f, indent=2)
        
        return json.dumps(schema, indent=2)
    
    def generate_openapi_spec(self, output_file: str = "tools_openapi.yaml") -> str:
        """Generate OpenAPI specification for tools"""
        tools = self.tool_registry.list_tools()
        
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "MCPOmni Connect Tools API",
                "version": "1.0.0",
                "description": "API specification for all available tools"
            },
            "paths": {},
            "components": {
                "schemas": {}
            }
        }
        
        for tool in tools:
            path = f"/tools/{tool.name}"
            
            # Request body schema
            request_schema = {
                "type": "object",
                "properties": {
                    "parameters": {
                        "type": "object",
                        "description": f"Parameters for {tool.name}",
                        "properties": tool.inputSchema.get('properties', {}) if hasattr(tool, 'inputSchema') else {},
                        "required": tool.inputSchema.get('required', []) if hasattr(tool, 'inputSchema') else []
                    }
                },
                "required": ["parameters"]
            }
            
            # Response schema
            response_schema = {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "string",
                        "description": "Tool execution result"
                    },
                    "success": {
                        "type": "boolean",
                        "description": "Whether the tool executed successfully"
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message if execution failed"
                    }
                }
            }
            
            openapi_spec["paths"][path] = {
                "post": {
                    "summary": tool.description,
                    "description": tool.description,
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": request_schema
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Tool executed successfully",
                            "content": {
                                "application/json": {
                                    "schema": response_schema
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid parameters",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        
        # Save to file
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / output_file
        
        import yaml
        with open(output_path, 'w') as f:
            yaml.dump(openapi_spec, f, default_flow_style=False)
        
        return yaml.dump(openapi_spec, default_flow_style=False)
    
    def generate_all_documentation(self) -> Dict[str, str]:
        """Generate all types of documentation"""
        results = {}
        
        # Generate markdown docs
        results['markdown'] = self.generate_markdown_docs()
        
        # Generate JSON schema
        results['json_schema'] = self.generate_json_schema()
        
        # Generate OpenAPI spec
        results['openapi'] = self.generate_openapi_spec()
        
        return results


# Global documentation generator
doc_generator = DocumentationGenerator()


# Convenience functions
def generate_tool_docs() -> str:
    """Generate markdown documentation for all tools"""
    return doc_generator.generate_markdown_docs()


def generate_tool_schema() -> str:
    """Generate JSON schema for all tools"""
    return doc_generator.generate_json_schema()


def generate_all_docs() -> Dict[str, str]:
    """Generate all documentation formats"""
    return doc_generator.generate_all_documentation() 