import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
from .local_tools_registry import ToolRegistry


@dataclass
class ToolExecutionRecord:
    """Record of a tool execution"""
    tool_name: str
    start_time: float
    end_time: float
    success: bool
    error_message: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    result_size: Optional[int] = None
    
    @property
    def duration(self) -> float:
        """Get execution duration in seconds"""
        return self.end_time - self.start_time


@dataclass
class ToolMetrics:
    """Metrics for a specific tool"""
    tool_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    recent_durations: deque = field(default_factory=lambda: deque(maxlen=100))
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    parameter_patterns: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage"""
        if self.total_executions == 0:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100
    
    @property
    def average_duration(self) -> float:
        """Get average execution duration"""
        if self.total_executions == 0:
            return 0.0
        return self.total_duration / self.total_executions
    
    @property
    def recent_average_duration(self) -> float:
        """Get average duration of recent executions"""
        if not self.recent_durations:
            return 0.0
        return statistics.mean(self.recent_durations)
    
    def add_execution(self, record: ToolExecutionRecord):
        """Add an execution record to metrics"""
        self.total_executions += 1
        
        if record.success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
            if record.error_message:
                self.error_counts[record.error_message] += 1
        
        duration = record.duration
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
        self.recent_durations.append(duration)
        
        # Track parameter patterns (simplified)
        param_key = str(sorted(record.parameters.keys()))
        self.parameter_patterns[param_key] += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "tool_name": self.tool_name,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": self.success_rate,
            "average_duration": self.average_duration,
            "min_duration": self.min_duration if self.min_duration != float('inf') else 0.0,
            "max_duration": self.max_duration,
            "recent_average_duration": self.recent_average_duration,
            "error_counts": dict(self.error_counts),
            "parameter_patterns": dict(self.parameter_patterns)
        }


class ToolMonitor:
    """Monitor for tracking tool performance and usage"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.metrics: Dict[str, ToolMetrics] = defaultdict(lambda: ToolMetrics(""))
        self.enabled = True
        self.performance_thresholds: Dict[str, float] = {}
    
    def start_monitoring(self):
        """Enable monitoring"""
        self.enabled = True
    
    def stop_monitoring(self):
        """Disable monitoring"""
        self.enabled = False
    
    def set_performance_threshold(self, tool_name: str, threshold_seconds: float):
        """Set performance threshold for a tool"""
        self.performance_thresholds[tool_name] = threshold_seconds
    
    def record_execution(self, record: ToolExecutionRecord):
        """Record a tool execution"""
        if not self.enabled:
            return
        
        # Initialize metrics for tool if not exists
        if record.tool_name not in self.metrics:
            self.metrics[record.tool_name] = ToolMetrics(record.tool_name)
        
        # Add execution record
        self.metrics[record.tool_name].add_execution(record)
        
        # Check performance threshold
        threshold = self.performance_thresholds.get(record.tool_name)
        if threshold and record.duration > threshold:
            print(f"⚠️  Performance warning: {record.tool_name} took {record.duration:.2f}s (threshold: {threshold}s)")
    
    def get_tool_metrics(self, tool_name: str) -> Optional[ToolMetrics]:
        """Get metrics for a specific tool"""
        return self.metrics.get(tool_name)
    
    def get_all_metrics(self) -> Dict[str, ToolMetrics]:
        """Get metrics for all tools"""
        return dict(self.metrics)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        if not self.metrics:
            return {"message": "No metrics available"}
        
        total_executions = sum(m.total_executions for m in self.metrics.values())
        total_duration = sum(m.total_duration for m in self.metrics.values())
        overall_success_rate = sum(m.successful_executions for m in self.metrics.values()) / total_executions * 100 if total_executions > 0 else 0
        
        # Find slowest and most used tools
        slowest_tool = max(self.metrics.values(), key=lambda m: m.average_duration)
        most_used_tool = max(self.metrics.values(), key=lambda m: m.total_executions)
        most_failed_tool = max(self.metrics.values(), key=lambda m: m.failed_executions) if any(m.failed_executions > 0 for m in self.metrics.values()) else None
        
        return {
            "total_executions": total_executions,
            "total_duration": total_duration,
            "overall_success_rate": overall_success_rate,
            "slowest_tool": {
                "name": slowest_tool.tool_name,
                "average_duration": slowest_tool.average_duration
            },
            "most_used_tool": {
                "name": most_used_tool.tool_name,
                "executions": most_used_tool.total_executions
            },
            "most_failed_tool": {
                "name": most_failed_tool.tool_name,
                "failures": most_failed_tool.failed_executions
            } if most_failed_tool else None
        }
    
    def get_recommendations(self) -> List[str]:
        """Get performance recommendations"""
        recommendations = []
        
        for tool_name, metrics in self.metrics.items():
            # Check success rate
            if metrics.success_rate < 80:
                recommendations.append(f"🔴 {tool_name}: Low success rate ({metrics.success_rate:.1f}%)")
            
            # Check performance
            if metrics.average_duration > 5.0:
                recommendations.append(f"🐌 {tool_name}: Slow average execution ({metrics.average_duration:.2f}s)")
            
            # Check error patterns
            if metrics.error_counts:
                most_common_error = max(metrics.error_counts.items(), key=lambda x: x[1])
                recommendations.append(f"⚠️  {tool_name}: Common error - {most_common_error[0]} ({most_common_error[1]} times)")
        
        return recommendations
    
    def clear_metrics(self, tool_name: Optional[str] = None):
        """Clear metrics for a tool or all tools"""
        if tool_name:
            if tool_name in self.metrics:
                del self.metrics[tool_name]
        else:
            self.metrics.clear()


class MonitoredToolRegistry(ToolRegistry):
    """Tool registry with monitoring capabilities"""
    
    def __init__(self, monitor: ToolMonitor = None):
        super().__init__()
        self.monitor = monitor or ToolMonitor()
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool with monitoring"""
        start_time = time.time()
        success = False
        error_message = None
        result = None
        
        try:
            result = await super().execute_tool(tool_name, parameters)
            success = True
        except Exception as e:
            error_message = str(e)
            raise
        finally:
            end_time = time.time()
            
            # Create execution record
            record = ToolExecutionRecord(
                tool_name=tool_name,
                start_time=start_time,
                end_time=end_time,
                success=success,
                error_message=error_message,
                parameters=parameters,
                result_size=len(str(result)) if result else None
            )
            
            # Record the execution
            self.monitor.record_execution(record)
        
        return result
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get monitoring summary"""
        return {
            "performance_summary": self.monitor.get_performance_summary(),
            "recommendations": self.monitor.get_recommendations(),
            "tool_metrics": {name: metrics.to_dict() for name, metrics in self.monitor.get_all_metrics().items()}
        }


# Global monitored tool registry
monitored_tool_registry = MonitoredToolRegistry()


# Convenience functions for monitoring
def get_tool_performance_report() -> Dict[str, Any]:
    """Get a comprehensive tool performance report"""
    return monitored_tool_registry.get_monitoring_summary()


def set_tool_performance_alert(tool_name: str, threshold_seconds: float):
    """Set performance alert for a tool"""
    monitored_tool_registry.monitor.set_performance_threshold(tool_name, threshold_seconds)


def get_tool_usage_insights() -> List[str]:
    """Get insights about tool usage patterns"""
    insights = []
    metrics = monitored_tool_registry.monitor.get_all_metrics()
    
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