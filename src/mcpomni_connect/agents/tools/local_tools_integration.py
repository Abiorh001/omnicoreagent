from typing import Dict, Any, List, Optional
from .local_tools_registry import ToolRegistry
from .tool_monitoring import MonitoredToolRegistry
from .tool_security import SecureToolRegistry


class LocalToolsIntegration:
    """Simplified integration layer for local tools with registry, monitoring, and security"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        # Initialize core registry
        self.tool_registry = tool_registry or ToolRegistry()
        
        # Initialize monitoring and security
        self.monitored_registry = MonitoredToolRegistry()
        self.secure_registry = SecureToolRegistry()
        
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
        """Execute a local tool with monitoring and security"""
        # Security check - use the secure registry's validation
        try:
            self.secure_registry.validate_execution(tool_name, parameters)
        except Exception as e:
            raise PermissionError(f"Security check failed for tool '{tool_name}': {str(e)}")
        
        # Start monitoring
        self.monitored_registry.monitor.start_tool_execution(tool_name)
        
        try:
            # Execute tool
            result = await self.tool_registry.execute_tool(tool_name, parameters)
            
            # Record success
            self.monitored_registry.monitor.record_tool_success(tool_name)
            
            return result
            
        except Exception as e:
            # Record failure
            self.monitored_registry.monitor.record_tool_failure(tool_name, str(e))
            raise
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all tool schemas for MCP integration"""
        return self.tool_registry.get_tool_schemas()
    
    def list_tool_names(self) -> List[str]:
        """Get list of registered tool names"""
        return list(self.tool_registry.tools.keys())
    
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
    
    # Convenience methods for easy setup
    def setup_basic_tool_ecosystem(self):
        """Setup basic tool ecosystem with monitoring and security"""
        print("🚀 Setting up basic tool ecosystem...")
        
        # Setup default security policies
        print("🔒 Setting up security policies...")
        from .tool_security import setup_default_security_policies
        setup_default_security_policies()
        
        # Start monitoring
        print("📊 Starting monitoring...")
        self.monitored_registry.monitor.start_monitoring()
        
        print("✅ Basic tool ecosystem setup complete!")
    
    def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get status of tool ecosystem components"""
        return {
            "tools_registered": len(self.tool_registry.tools),
            "monitoring_summary": self.get_monitoring_summary(),
            "security_report": self.get_security_report()
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
    """Setup basic tool ecosystem"""
    local_tools.setup_basic_tool_ecosystem()


def get_ecosystem_status() -> Dict[str, Any]:
    """Get tool ecosystem status"""
    return local_tools.get_ecosystem_status()


def get_tool_insights() -> List[str]:
    """Get insights about tool usage and performance"""
    return local_tools.get_tool_usage_insights() 