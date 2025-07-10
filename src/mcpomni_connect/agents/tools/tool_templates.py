import json
import requests
import csv
import io
from typing import Dict, List, Any, Optional
from pathlib import Path
from .local_tools_registry import ToolRegistry


class ToolTemplate:
    """A template for a set of related tools"""
    
    def __init__(self, name: str, description: str, tools: List[Dict[str, Any]]):
        self.name = name
        self.description = description
        self.tools = tools
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tools": self.tools
        }


class ToolTemplates:
    """Pre-configured tool sets for common use cases"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.templates: Dict[str, ToolTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default tool templates"""
        
        # Data Processing Template
        data_processing_tools = [
            {
                "name": "csv_to_json",
                "description": "Convert CSV data to JSON format",
                "function": self._csv_to_json,
                "schema": {
                    "type": "object",
                    "properties": {
                        "csv_data": {"type": "string", "description": "CSV data as string"},
                        "delimiter": {"type": "string", "description": "CSV delimiter", "default": ","}
                    },
                    "required": ["csv_data"]
                }
            },
            {
                "name": "json_to_csv",
                "description": "Convert JSON data to CSV format",
                "function": self._json_to_csv,
                "schema": {
                    "type": "object",
                    "properties": {
                        "json_data": {"type": "string", "description": "JSON data as string"},
                        "delimiter": {"type": "string", "description": "CSV delimiter", "default": ","}
                    },
                    "required": ["json_data"]
                }
            },
            {
                "name": "filter_data",
                "description": "Filter data based on conditions",
                "function": self._filter_data,
                "schema": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "JSON data as string"},
                        "field": {"type": "string", "description": "Field to filter on"},
                        "value": {"type": "string", "description": "Value to filter for"},
                        "operator": {"type": "string", "description": "Filter operator (eq, gt, lt, contains)", "default": "eq"}
                    },
                    "required": ["data", "field", "value"]
                }
            }
        ]
        
        # File Operations Template
        file_operations_tools = [
            {
                "name": "read_text_file",
                "description": "Read contents of a text file",
                "function": self._read_text_file,
                "schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file"},
                        "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"}
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "write_text_file",
                "description": "Write content to a text file",
                "function": self._write_text_file,
                "schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the file"},
                        "content": {"type": "string", "description": "Content to write"},
                        "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"}
                    },
                    "required": ["file_path", "content"]
                }
            },
            {
                "name": "list_files",
                "description": "List files in a directory",
                "function": self._list_files,
                "schema": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "Directory path"},
                        "pattern": {"type": "string", "description": "File pattern (e.g., *.txt)", "default": "*"}
                    },
                    "required": ["directory"]
                }
            }
        ]
        
        # Web Scraping Template
        web_scraping_tools = [
            {
                "name": "fetch_url",
                "description": "Fetch content from a URL",
                "function": self._fetch_url,
                "schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch"},
                        "timeout": {"type": "integer", "description": "Request timeout in seconds", "default": 30}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "extract_text",
                "description": "Extract text content from HTML",
                "function": self._extract_text,
                "schema": {
                    "type": "object",
                    "properties": {
                        "html_content": {"type": "string", "description": "HTML content"},
                        "selector": {"type": "string", "description": "CSS selector for extraction"}
                    },
                    "required": ["html_content"]
                }
            }
        ]
        
        # Math Operations Template
        math_operations_tools = [
            {
                "name": "calculate",
                "description": "Perform mathematical calculations",
                "function": self._calculate,
                "schema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Mathematical expression"},
                        "variables": {"type": "object", "description": "Variables for the expression", "default": {}}
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "statistics",
                "description": "Calculate basic statistics",
                "function": self._statistics,
                "schema": {
                    "type": "object",
                    "properties": {
                        "numbers": {"type": "array", "description": "List of numbers", "items": {"type": "number"}},
                        "operation": {"type": "string", "description": "Statistical operation (mean, median, std, min, max)", "default": "mean"}
                    },
                    "required": ["numbers"]
                }
            }
        ]
        
        # Register templates
        self.templates["data_processing"] = ToolTemplate(
            "Data Processing",
            "Tools for data transformation and manipulation",
            data_processing_tools
        )
        
        self.templates["file_operations"] = ToolTemplate(
            "File Operations",
            "Tools for file reading, writing, and management",
            file_operations_tools
        )
        
        self.templates["web_scraping"] = ToolTemplate(
            "Web Scraping",
            "Tools for fetching and extracting web content",
            web_scraping_tools
        )
        
        self.templates["math_operations"] = ToolTemplate(
            "Math Operations",
            "Tools for mathematical calculations and statistics",
            math_operations_tools
        )
    
    def get_template(self, template_name: str) -> Optional[ToolTemplate]:
        """Get a specific template by name"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())
    
    def load_template(self, template_name: str) -> int:
        """Load all tools from a template into the registry"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        registered_count = 0
        for tool_config in template.tools:
            try:
                self.tool_registry.register(
                    name=tool_config["name"],
                    description=tool_config["description"],
                    inputSchema=tool_config["schema"]
                )(tool_config["function"])
                registered_count += 1
            except Exception as e:
                print(f"Warning: Could not register tool {tool_config['name']}: {e}")
        
        return registered_count
    
    def load_all_templates(self) -> Dict[str, int]:
        """Load all templates into the registry"""
        results = {}
        for template_name in self.templates:
            results[template_name] = self.load_template(template_name)
        return results
    
    # Template tool implementations
    
    def _csv_to_json(self, csv_data: str, delimiter: str = ",") -> str:
        """Convert CSV data to JSON format"""
        try:
            csv_reader = csv.DictReader(io.StringIO(csv_data), delimiter=delimiter)
            data = list(csv_reader)
            return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error converting CSV to JSON: {e}"
    
    def _json_to_csv(self, json_data: str, delimiter: str = ",") -> str:
        """Convert JSON data to CSV format"""
        try:
            data = json.loads(json_data)
            if not data:
                return ""
            
            output = io.StringIO()
            if isinstance(data, list) and len(data) > 0:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
            
            return output.getvalue()
        except Exception as e:
            return f"Error converting JSON to CSV: {e}"
    
    def _filter_data(self, data: str, field: str, value: str, operator: str = "eq") -> str:
        """Filter data based on conditions"""
        try:
            data_list = json.loads(data)
            if not isinstance(data_list, list):
                return "Error: Data must be a JSON array"
            
            filtered_data = []
            for item in data_list:
                if field not in item:
                    continue
                
                item_value = str(item[field])
                if operator == "eq" and item_value == value:
                    filtered_data.append(item)
                elif operator == "gt" and item_value > value:
                    filtered_data.append(item)
                elif operator == "lt" and item_value < value:
                    filtered_data.append(item)
                elif operator == "contains" and value in item_value:
                    filtered_data.append(item)
            
            return json.dumps(filtered_data, indent=2)
        except Exception as e:
            return f"Error filtering data: {e}"
    
    def _read_text_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """Read contents of a text file"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    
    def _write_text_file(self, file_path: str, content: str, encoding: str = "utf-8") -> str:
        """Write content to a text file"""
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to {file_path}"
        except Exception as e:
            return f"Error writing file: {e}"
    
    def _list_files(self, directory: str, pattern: str = "*") -> str:
        """List files in a directory"""
        try:
            path = Path(directory)
            if not path.exists():
                return f"Error: Directory {directory} does not exist"
            
            files = list(path.glob(pattern))
            file_list = [str(f.relative_to(path)) for f in files if f.is_file()]
            return json.dumps(file_list, indent=2)
        except Exception as e:
            return f"Error listing files: {e}"
    
    def _fetch_url(self, url: str, timeout: int = 30) -> str:
        """Fetch content from a URL"""
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Error fetching URL: {e}"
    
    def _extract_text(self, html_content: str, selector: str = None) -> str:
        """Extract text content from HTML"""
        try:
            # Simple text extraction (remove HTML tags)
            import re
            if selector:
                # For now, just return the HTML content
                # In a real implementation, you'd use BeautifulSoup or similar
                return f"Selector '{selector}' not implemented yet. Full content: {html_content[:500]}..."
            else:
                # Remove HTML tags
                clean_text = re.sub(r'<[^>]+>', '', html_content)
                return clean_text.strip()
        except Exception as e:
            return f"Error extracting text: {e}"
    
    def _calculate(self, expression: str, variables: Dict[str, float] = None) -> str:
        """Perform mathematical calculations"""
        try:
            # Simple expression evaluation (use with caution in production)
            if variables:
                for var_name, var_value in variables.items():
                    expression = expression.replace(var_name, str(var_value))
            
            # Only allow safe mathematical operations
            allowed_chars = set('0123456789+-*/(). ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Expression contains unsafe characters"
            
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error calculating expression: {e}"
    
    def _statistics(self, numbers: List[float], operation: str = "mean") -> str:
        """Calculate basic statistics"""
        try:
            if not numbers:
                return "Error: No numbers provided"
            
            if operation == "mean":
                result = sum(numbers) / len(numbers)
            elif operation == "median":
                sorted_numbers = sorted(numbers)
                n = len(sorted_numbers)
                if n % 2 == 0:
                    result = (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
                else:
                    result = sorted_numbers[n//2]
            elif operation == "std":
                mean = sum(numbers) / len(numbers)
                variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
                result = variance ** 0.5
            elif operation == "min":
                result = min(numbers)
            elif operation == "max":
                result = max(numbers)
            else:
                return f"Error: Unknown operation '{operation}'"
            
            return str(result)
        except Exception as e:
            return f"Error calculating statistics: {e}"


# Global templates instance
tool_templates = ToolTemplates() 