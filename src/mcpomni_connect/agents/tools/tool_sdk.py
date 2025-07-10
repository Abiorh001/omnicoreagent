import inspect
import functools
from typing import Dict, Any, Optional, Callable, Union, List
from dataclasses import dataclass
from enum import Enum
from .local_tools_registry import ToolRegistry
import re
import asyncio
import json


class ToolType(Enum):
    """Types of tools"""
    FUNCTION = "function"
    ASYNC_FUNCTION = "async_function"
    CLASS_METHOD = "class_method"
    GENERATOR = "generator"


@dataclass
class ToolMetadata:
    """Metadata for a tool"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    tags: List[str] = None
    examples: List[Dict[str, Any]] = None
    dependencies: List[str] = None
    timeout: Optional[float] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.examples is None:
            self.examples = []
        if self.dependencies is None:
            self.dependencies = []


class ToolBuilder:
    """Builder for creating tools with metadata"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.metadata: Dict[str, ToolMetadata] = {}
    
    def tool(
        self,
        name: str = None,
        description: str = "",
        version: str = "1.0.0",
        author: str = "",
        tags: List[str] = None,
        examples: List[Dict[str, Any]] = None,
        dependencies: List[str] = None,
        timeout: Optional[float] = None,
        retry_count: int = 0,
        input_schema: Dict[str, Any] = None
    ):
        """Decorator to create a tool with metadata"""
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            
            # Create metadata
            metadata = ToolMetadata(
                name=tool_name,
                description=description or func.__doc__ or "",
                version=version,
                author=author,
                tags=tags or [],
                examples=examples or [],
                dependencies=dependencies or [],
                timeout=timeout,
                retry_count=retry_count
            )
            
            # Store metadata
            self.metadata[tool_name] = metadata
            
            # Register tool
            self.tool_registry.register(
                name=tool_name,
                description=metadata.description,
                inputSchema=input_schema
            )(func)
            
            # Add metadata to function
            func.tool_metadata = metadata
            
            return func
        return decorator
    
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a tool"""
        return self.metadata.get(tool_name)
    
    def list_tools_with_metadata(self) -> Dict[str, ToolMetadata]:
        """List all tools with their metadata"""
        return self.metadata.copy()


# Global tool builder
tool_builder = ToolBuilder()


class ToolValidator:
    """Validator for tool parameters and results"""
    
    @staticmethod
    def validate_string_param(value: str, min_length: int = 0, max_length: int = None, pattern: str = None) -> bool:
        """Validate string parameter"""
        if not isinstance(value, str):
            return False
        
        if len(value) < min_length:
            return False
        
        if max_length and len(value) > max_length:
            return False
        
        if pattern and not re.match(pattern, value):
            return False
        
        return True
    
    @staticmethod
    def validate_number_param(value: Union[int, float], min_value: float = None, max_value: float = None) -> bool:
        """Validate number parameter"""
        if not isinstance(value, (int, float)):
            return False
        
        if min_value is not None and value < min_value:
            return False
        
        if max_value is not None and value > max_value:
            return False
        
        return True
    
    @staticmethod
    def validate_list_param(value: List, min_items: int = 0, max_items: int = None) -> bool:
        """Validate list parameter"""
        if not isinstance(value, list):
            return False
        
        if len(value) < min_items:
            return False
        
        if max_items and len(value) > max_items:
            return False
        
        return True


def validate_params(**validations):
    """Decorator to validate tool parameters"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Validate parameters
            for param_name, validation in validations.items():
                if param_name in kwargs:
                    if not validation(kwargs[param_name]):
                        raise ValueError(f"Parameter '{param_name}' failed validation")
            
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Validate parameters
            for param_name, validation in validations.items():
                if param_name in kwargs:
                    if not validation(kwargs[param_name]):
                        raise ValueError(f"Parameter '{param_name}' failed validation")
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def with_error_handling(error_message: str = "Tool execution failed"):
    """Decorator to add error handling to tools"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                return f"{error_message}: {str(e)}"
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return f"{error_message}: {str(e)}"
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def with_logging(logger_name: str = None):
    """Decorator to add logging to tools"""
    def decorator(func: Callable) -> Callable:
        import logging
        logger = logging.getLogger(logger_name or func.__name__)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.info(f"Executing {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed: {e}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger.info(f"Executing {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed: {e}")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Example tool creation with the SDK
@tool_builder.tool(
    name="advanced_calculator",
    description="Advanced calculator with validation and error handling",
    version="2.0.0",
    author="Tool SDK Example",
    tags=["math", "calculation", "advanced"],
    examples=[
        {
            "expression": "2 + 2 * 3",
            "variables": {"x": 5, "y": 10},
            "expected_result": "16"
        }
    ],
    dependencies=["math"],
    timeout=30.0,
    retry_count=2
)
@validate_params(
    expression=lambda x: ToolValidator.validate_string_param(x, min_length=1, max_length=1000),
    variables=lambda x: ToolValidator.validate_list_param(x, max_items=100)
)
@with_error_handling("Calculation failed")
@with_logging("calculator")
async def advanced_calculator(expression: str, variables: Dict[str, float] = None) -> str:
    """
    Advanced calculator with variable support and validation.
    
    Args:
        expression: Mathematical expression to evaluate
        variables: Dictionary of variables for the expression
    
    Returns:
        Result of the calculation as string
    """
    if variables:
        for var_name, var_value in variables.items():
            expression = expression.replace(var_name, str(var_value))
    
    # Safe evaluation (in production, use a proper math parser)
    allowed_chars = set('0123456789+-*/(). ')
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Expression contains unsafe characters")
    
    result = eval(expression)
    return str(result)


# Tool template generator
class ToolTemplateGenerator:
    """Generate tool templates for common patterns"""
    
    @staticmethod
    def create_data_processing_tool(name: str, description: str) -> str:
        """Generate a data processing tool template"""
        return f'''
@tool_builder.tool(
    name="{name}",
    description="{description}",
    tags=["data", "processing"],
    version="1.0.0"
)
@with_error_handling("Data processing failed")
async def {name}(data: str, **kwargs) -> str:
    """
    {description}
    
    Args:
        data: Input data to process
        **kwargs: Additional processing parameters
    
    Returns:
        Processed data as string
    """
    # TODO: Implement data processing logic
    processed_data = data  # Placeholder
    
    return processed_data
'''
    
    @staticmethod
    def create_api_tool(name: str, description: str, endpoint: str) -> str:
        """Generate an API tool template"""
        return f'''
@tool_builder.tool(
    name="{name}",
    description="{description}",
    tags=["api", "http"],
    version="1.0.0"
)
@with_error_handling("API call failed")
async def {name}(**params) -> str:
    """
    {description}
    
    Args:
        **params: Parameters for the API call
    
    Returns:
        API response as string
    """
    import requests
    
    url = "{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.text
'''
    
    @staticmethod
    def create_file_tool(name: str, description: str, operation: str) -> str:
        """Generate a file operation tool template"""
        return f'''
@tool_builder.tool(
    name="{name}",
    description="{description}",
    tags=["file", "{operation}"],
    version="1.0.0"
)
@with_error_handling("File operation failed")
async def {name}(file_path: str, **kwargs) -> str:
    """
    {description}
    
    Args:
        file_path: Path to the file
        **kwargs: Additional parameters
    
    Returns:
        Operation result as string
    """
    # TODO: Implement file {operation} logic
    return f"File {operation} completed for {{file_path}}"
'''


# Tool documentation generator
class ToolDocumentationGenerator:
    """Generate documentation for tools"""
    
    def __init__(self, tool_builder: ToolBuilder):
        self.tool_builder = tool_builder
    
    def generate_markdown_docs(self) -> str:
        """Generate markdown documentation for all tools"""
        docs = "# Tool Documentation\n\n"
        
        for tool_name, metadata in self.tool_builder.list_tools_with_metadata().items():
            docs += f"## {metadata.name}\n\n"
            docs += f"**Version:** {metadata.version}\n\n"
            docs += f"**Author:** {metadata.author}\n\n"
            docs += f"**Description:** {metadata.description}\n\n"
            
            if metadata.tags:
                docs += f"**Tags:** {', '.join(metadata.tags)}\n\n"
            
            if metadata.examples:
                docs += "**Examples:**\n\n"
                for example in metadata.examples:
                    docs += "```json\n"
                    docs += json.dumps(example, indent=2)
                    docs += "\n```\n\n"
            
            if metadata.dependencies:
                docs += f"**Dependencies:** {', '.join(metadata.dependencies)}\n\n"
            
            docs += "---\n\n"
        
        return docs
    
    def generate_api_docs(self) -> Dict[str, Any]:
        """Generate API documentation for tools"""
        api_docs = {
            "openapi": "3.0.0",
            "info": {
                "title": "Tool API",
                "version": "1.0.0",
                "description": "API documentation for available tools"
            },
            "paths": {}
        }
        
        for tool_name, metadata in self.tool_builder.list_tools_with_metadata().items():
            api_docs["paths"][f"/tools/{tool_name}"] = {
                "post": {
                    "summary": metadata.description,
                    "description": metadata.description,
                    "tags": metadata.tags,
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "parameters": {
                                            "type": "object",
                                            "description": "Tool parameters"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Tool executed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "result": {
                                                "type": "string",
                                                "description": "Tool result"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        
        return api_docs


# Global documentation generator
doc_generator = ToolDocumentationGenerator(tool_builder) 