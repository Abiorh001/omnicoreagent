import inspect
import importlib
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from .local_tools_registry import ToolRegistry


class ToolDiscovery:
    """Automatic tool discovery system"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.discovered_tools: Dict[str, Any] = {}
    
    def discover_from_module(self, module_name: str) -> List[str]:
        """Discover tools from a Python module"""
        try:
            module = importlib.import_module(module_name)
            discovered = []
            
            for name, obj in inspect.getmembers(module):
                if self._is_tool_function(obj):
                    discovered.append(name)
                    self.discovered_tools[name] = obj
            
            return discovered
        except ImportError as e:
            print(f"Warning: Could not import module {module_name}: {e}")
            return []
    
    def discover_from_directory(self, directory_path: str, pattern: str = "*.py") -> List[str]:
        """Discover tools from a directory of Python files"""
        discovered = []
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"Warning: Directory {directory_path} does not exist")
            return discovered
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                module_name = self._path_to_module_name(file_path)
                if module_name:
                    discovered.extend(self.discover_from_module(module_name))
        
        return discovered
    
    def discover_from_class(self, class_obj: type) -> List[str]:
        """Discover tools from a class (methods that could be tools)"""
        discovered = []
        
        for name, method in inspect.getmembers(class_obj, inspect.isfunction):
            if self._is_tool_method(method):
                discovered.append(name)
                self.discovered_tools[name] = method
        
        return discovered
    
    def auto_register_discovered_tools(self) -> int:
        """Automatically register all discovered tools"""
        registered_count = 0
        
        for name, tool_func in self.discovered_tools.items():
            try:
                # Use the decorator to register the tool
                self.tool_registry.register(
                    name=name,
                    description=tool_func.__doc__ or f"Tool: {name}"
                )(tool_func)
                registered_count += 1
            except Exception as e:
                print(f"Warning: Could not register tool {name}: {e}")
        
        return registered_count
    
    def _is_tool_function(self, obj: Any) -> bool:
        """Check if an object is a tool function"""
        if not inspect.isfunction(obj):
            return False
        
        # Check if it's not a built-in or special method
        if obj.__name__.startswith('_'):
            return False
        
        # Check if it has a reasonable signature (not too many parameters)
        sig = inspect.signature(obj)
        if len(sig.parameters) > 10:  # Too many parameters
            return False
        
        # Check if it's not a method (no self parameter)
        params = list(sig.parameters.keys())
        if params and params[0] == 'self':
            return False
        
        return True
    
    def _is_tool_method(self, method: Callable) -> bool:
        """Check if a method could be a tool"""
        if not inspect.isfunction(method):
            return False
        
        # Check if it's not a built-in or special method
        if method.__name__.startswith('_'):
            return False
        
        # Check if it has a reasonable signature
        sig = inspect.signature(method)
        if len(sig.parameters) > 11:  # Too many parameters (including self)
            return False
        
        return True
    
    def _path_to_module_name(self, file_path: Path) -> Optional[str]:
        """Convert a file path to a module name"""
        try:
            # Get the relative path from the current working directory
            rel_path = file_path.relative_to(Path.cwd())
            
            # Convert to module name
            module_name = str(rel_path).replace('/', '.').replace('\\', '.')
            
            # Remove .py extension
            if module_name.endswith('.py'):
                module_name = module_name[:-3]
            
            return module_name
        except ValueError:
            # File is not relative to current directory
            return None
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """Get a summary of discovered tools"""
        return {
            "total_discovered": len(self.discovered_tools),
            "tools": list(self.discovered_tools.keys()),
            "registered_count": len(self.tool_registry.tools)
        }


# Global discovery instance
tool_discovery = ToolDiscovery() 