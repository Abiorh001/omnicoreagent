from typing import Dict, Any, List, Optional
from .local_tools_registry import ToolRegistry
from .tool_discovery import ToolDiscovery
from .tool_templates import ToolTemplates
from .tool_composition import ToolCompositionManager
from .tool_caching import CachedToolRegistry
from .tool_monitoring import MonitoredToolRegistry
from .tool_security import SecureToolRegistry
from .tool_sdk import ToolBuilder
from .tool_testing import ToolTestSuite, ToolPerformanceTester, ToolIntegrationTester
from .tool_documentation import DocumentationGenerator


class LocalToolsIntegration:
    """Comprehensive integration layer for local tools with all Phase 2 features"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        # Initialize core registry
        self.tool_registry = tool_registry or ToolRegistry()
        
        # Initialize all Phase 2 components
        self.discovery = ToolDiscovery(self.tool_registry)
        self.templates = ToolTemplates(self.tool_registry)
        self.composition_manager = ToolCompositionManager(self.tool_registry)
        self.cached_registry = CachedToolRegistry()
        self.monitored_registry = MonitoredToolRegistry()
        self.secure_registry = SecureToolRegistry()
        self.tool_builder = ToolBuilder(self.tool_registry)
        self.test_suite = ToolTestSuite(self.tool_registry)
        self.performance_tester = ToolPerformanceTester(self.tool_registry)
        self.integration_tester = ToolIntegrationTester(self.tool_registry)
        self.doc_generator = DocumentationGenerator(self.tool_registry)
        
        self._registered_tools: Dict[str, Any] = {}
    
    # Core tool registration
    def register_tool(self, tool_name: str, tool_function: callable, description: str = None, schema: Dict[str, Any] = None):
        """Register a tool with the local tools system"""
        self.tool_registry.register(
            name=tool_name,
            description=description,
            inputSchema=schema
        )(tool_function)
        self._registered_tools[tool_name] = tool_function
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for OmniAgent"""
        tools = []
        for tool in self.tool_registry.list_tools():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
                "type": "local"
            })
        return tools
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a local tool"""
        return await self.tool_registry.execute_tool(tool_name, parameters)
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all tool schemas for MCP integration"""
        return self.tool_registry.get_tool_schemas()
    
    def list_tool_names(self) -> List[str]:
        """Get list of registered tool names"""
        return list(self.tool_registry.tools.keys())
    
    # Tool Discovery
    def discover_tools_from_module(self, module_name: str) -> List[str]:
        """Discover tools from a Python module"""
        return self.discovery.discover_from_module(module_name)
    
    def discover_tools_from_directory(self, directory_path: str, pattern: str = "*.py") -> List[str]:
        """Discover tools from a directory of Python files"""
        return self.discovery.discover_from_directory(directory_path, pattern)
    
    def auto_register_discovered_tools(self) -> int:
        """Automatically register all discovered tools"""
        return self.discovery.auto_register_discovered_tools()
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """Get a summary of discovered tools"""
        return self.discovery.get_discovery_summary()
    
    # Tool Templates
    def load_template(self, template_name: str) -> int:
        """Load all tools from a template into the registry"""
        return self.templates.load_template(template_name)
    
    def load_all_templates(self) -> Dict[str, int]:
        """Load all templates into the registry"""
        return self.templates.load_all_templates()
    
    def list_templates(self) -> List[str]:
        """List all available template names"""
        return self.templates.list_templates()
    
    def get_template(self, template_name: str):
        """Get a specific template by name"""
        return self.templates.get_template(template_name)
    
    # Tool Composition
    def create_composition(self, name: str):
        """Create a new tool composition"""
        return self.composition_manager.create_composition(name)
    
    def get_composition(self, name: str):
        """Get a composition by name"""
        return self.composition_manager.get_composition(name)
    
    def list_compositions(self) -> List[str]:
        """List all composition names"""
        return self.composition_manager.list_compositions()
    
    def register_composition_as_tool(self, composition_name: str, tool_name: str = None) -> str:
        """Register a composition as a tool in the registry"""
        return self.composition_manager.register_composition_as_tool(composition_name, tool_name)
    
    # Tool Caching
    def set_tool_ttl(self, tool_name: str, ttl: Optional[float]) -> None:
        """Set TTL for a specific tool"""
        self.cached_registry.set_tool_ttl(tool_name, ttl)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cached_registry.get_cache_stats()
    
    def clear_cache(self) -> None:
        """Clear the tool cache"""
        self.cached_registry.clear_cache()
    
    # Tool Monitoring
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get monitoring summary"""
        return self.monitored_registry.get_monitoring_summary()
    
    def set_performance_alert(self, tool_name: str, threshold_seconds: float):
        """Set performance alert for a tool"""
        self.monitored_registry.monitor.set_performance_threshold(tool_name, threshold_seconds)
    
    def get_tool_usage_insights(self) -> List[str]:
        """Get insights about tool usage patterns"""
        insights = []
        metrics = self.monitored_registry.monitor.get_all_metrics()
        
        if not metrics:
            return ["No tool usage data available"]
        
        # Most used tools
        most_used = sorted(metrics.values(), key=lambda m: m.total_executions, reverse=True)[:3]
        insights.append("🔝 Most Used Tools:")
        for tool in most_used:
            insights.append(f"  • {tool.tool_name}: {tool.total_executions} executions")
        
        # Performance insights
        slow_tools = [m for m in metrics.values() if m.average_duration > 2.0]
        if slow_tools:
            insights.append("🐌 Slow Tools (avg > 2s):")
            for tool in slow_tools:
                insights.append(f"  • {tool.tool_name}: {tool.average_duration:.2f}s avg")
        
        # Reliability insights
        unreliable_tools = [m for m in metrics.values() if m.success_rate < 90]
        if unreliable_tools:
            insights.append("⚠️  Unreliable Tools (success rate < 90%):")
            for tool in unreliable_tools:
                insights.append(f"  • {tool.tool_name}: {tool.success_rate:.1f}% success rate")
        
        return insights
    
    # Tool Security
    def add_security_policy(self, policy):
        """Add security policy for a tool"""
        self.secure_registry.add_security_policy(policy)
    
    def set_user_context(self, user: str, roles: List[str] = None):
        """Set current user context for security checks"""
        self.secure_registry.set_user_context(user, roles or [])
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get security report"""
        return self.secure_registry.get_security_report()
    
    # Tool SDK
    def get_tool_metadata(self, tool_name: str):
        """Get metadata for a tool"""
        return self.tool_builder.get_tool_metadata(tool_name)
    
    def list_tools_with_metadata(self) -> Dict[str, Any]:
        """List all tools with their metadata"""
        return self.tool_builder.list_tools_with_metadata()
    
    # Tool Testing
    async def run_basic_tests(self) -> Dict[str, Any]:
        """Run basic tests for all registered tools"""
        return await self.test_suite.run_all_tests()
    
    async def benchmark_all_tools(self, iterations: int = 50) -> Dict[str, Any]:
        """Benchmark all registered tools"""
        return await self.performance_tester.compare_tools([], iterations)
    
    def generate_test_report(self) -> str:
        """Generate a test report in markdown format"""
        return self.test_suite.get_test_summary()
    
    # Tool Documentation
    def generate_markdown_docs(self, output_file: str = "tools_documentation.md") -> str:
        """Generate markdown documentation for all tools"""
        return self.doc_generator.generate_markdown_docs(output_file)
    
    def generate_json_schema(self, output_file: str = "tools_schema.json") -> str:
        """Generate JSON schema for all tools"""
        return self.doc_generator.generate_json_schema(output_file)
    
    def generate_all_documentation(self) -> Dict[str, str]:
        """Generate all documentation formats"""
        return self.doc_generator.generate_all_documentation()
    
    # Convenience methods for easy setup
    def setup_complete_tool_ecosystem(self):
        """Setup a complete tool ecosystem with all features"""
        print("🚀 Setting up complete tool ecosystem...")
        
        # Load all templates
        print("📦 Loading tool templates...")
        template_results = self.load_all_templates()
        for template, count in template_results.items():
            print(f"  • {template}: {count} tools loaded")
        
        # Setup default security policies
        print("🔒 Setting up security policies...")
        from .tool_security import setup_default_security_policies
        setup_default_security_policies()
        
        # Configure caching
        print("⚡ Configuring caching...")
        from .tool_caching import configure_tool_caching
        configure_tool_caching()
        
        # Start monitoring
        print("📊 Starting monitoring...")
        self.monitored_registry.monitor.start_monitoring()
        
        print("✅ Tool ecosystem setup complete!")
    
    def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get status of all tool ecosystem components"""
        return {
            "tools_registered": len(self.tool_registry.tools),
            "templates_available": len(self.templates.templates),
            "compositions_available": len(self.composition_manager.compositions),
            "cache_stats": self.get_cache_stats(),
            "monitoring_summary": self.get_monitoring_summary(),
            "security_report": self.get_security_report(),
            "discovery_summary": self.get_discovery_summary()
        }


# Global instance for easy access
local_tools = LocalToolsIntegration()


# Convenience functions for easy tool registration
def register_local_tool(name: str, description: str = None, schema: Dict[str, Any] = None):
    """Decorator to register a local tool"""
    def decorator(func):
        local_tools.register_tool(name, func, description, schema)
        return func
    return decorator


def get_local_tools() -> List[Dict[str, Any]]:
    """Get all registered local tools"""
    return local_tools.get_available_tools()


async def execute_local_tool(tool_name: str, parameters: Dict[str, Any]) -> Any:
    """Execute a local tool by name"""
    return await local_tools.execute_tool(tool_name, parameters)


# High-level convenience functions
def setup_tool_ecosystem():
    """Setup complete tool ecosystem"""
    local_tools.setup_complete_tool_ecosystem()


def get_ecosystem_status() -> Dict[str, Any]:
    """Get tool ecosystem status"""
    return local_tools.get_ecosystem_status()


async def run_tool_tests() -> Dict[str, Any]:
    """Run comprehensive tool tests"""
    return await local_tools.run_basic_tests()


def generate_tool_docs() -> str:
    """Generate comprehensive tool documentation"""
    return local_tools.generate_markdown_docs()


def get_tool_insights() -> List[str]:
    """Get insights about tool usage and performance"""
    return local_tools.get_tool_usage_insights() 