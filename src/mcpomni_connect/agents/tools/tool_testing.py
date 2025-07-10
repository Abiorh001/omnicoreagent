import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from unittest.mock import Mock, patch
from .local_tools_registry import ToolRegistry


@dataclass
class TestCase:
    """A test case for a tool"""
    name: str
    tool_name: str
    parameters: Dict[str, Any]
    expected_result: Any = None
    expected_error: str = None
    timeout: float = 30.0
    description: str = ""
    
    def __post_init__(self):
        if self.expected_result is not None and self.expected_error is not None:
            raise ValueError("Cannot specify both expected_result and expected_error")


@dataclass
class TestResult:
    """Result of a test case execution"""
    test_case: TestCase
    success: bool
    actual_result: Any = None
    error_message: str = ""
    execution_time: float = 0.0
    memory_usage: Optional[float] = None


class ToolTestSuite:
    """Test suite for tools"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []
    
    def add_test_case(self, test_case: TestCase):
        """Add a test case to the suite"""
        self.test_cases.append(test_case)
    
    def add_test_cases(self, test_cases: List[TestCase]):
        """Add multiple test cases to the suite"""
        self.test_cases.extend(test_cases)
    
    async def run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case"""
        start_time = time.time()
        success = False
        actual_result = None
        error_message = ""
        
        try:
            # Execute tool with timeout
            actual_result = await asyncio.wait_for(
                self.tool_registry.execute_tool(test_case.tool_name, test_case.parameters),
                timeout=test_case.timeout
            )
            
            # Check expected result
            if test_case.expected_result is not None:
                if actual_result != test_case.expected_result:
                    error_message = f"Expected {test_case.expected_result}, got {actual_result}"
                else:
                    success = True
            elif test_case.expected_error is not None:
                error_message = f"Expected error '{test_case.expected_error}' but got success"
            else:
                success = True
                
        except asyncio.TimeoutError:
            error_message = f"Test timed out after {test_case.timeout} seconds"
        except Exception as e:
            error_message = str(e)
            if test_case.expected_error and test_case.expected_error in error_message:
                success = True
            elif test_case.expected_error is None:
                success = False
        
        execution_time = time.time() - start_time
        
        return TestResult(
            test_case=test_case,
            success=success,
            actual_result=actual_result,
            error_message=error_message,
            execution_time=execution_time
        )
    
    async def run_all_tests(self) -> List[TestResult]:
        """Run all test cases"""
        self.results = []
        
        for test_case in self.test_cases:
            result = await self.run_test_case(test_case)
            self.results.append(result)
        
        return self.results
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test results"""
        if not self.results:
            return {"message": "No tests run"}
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_time = sum(r.execution_time for r in self.results)
        avg_time = total_time / total_tests if total_tests > 0 else 0
        
        failed_cases = [r for r in self.results if not r.success]
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_execution_time": total_time,
            "average_execution_time": avg_time,
            "failed_cases": [
                {
                    "name": r.test_case.name,
                    "tool": r.test_case.tool_name,
                    "error": r.error_message
                }
                for r in failed_cases
            ]
        }


class ToolPerformanceTester:
    """Performance testing for tools"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.tool_registry = tool_registry or ToolRegistry()
    
    async def benchmark_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        iterations: int = 100,
        warmup_iterations: int = 10
    ) -> Dict[str, Any]:
        """Benchmark a tool's performance"""
        
        # Warmup
        for _ in range(warmup_iterations):
            try:
                await self.tool_registry.execute_tool(tool_name, parameters)
            except Exception:
                pass
        
        # Actual benchmark
        times = []
        errors = 0
        
        for _ in range(iterations):
            start_time = time.time()
            try:
                await self.tool_registry.execute_tool(tool_name, parameters)
                times.append(time.time() - start_time)
            except Exception:
                errors += 1
        
        if not times:
            return {
                "tool_name": tool_name,
                "iterations": iterations,
                "errors": errors,
                "success_rate": 0,
                "message": "All iterations failed"
            }
        
        # Calculate statistics
        import statistics
        return {
            "tool_name": tool_name,
            "iterations": iterations,
            "successful_iterations": len(times),
            "errors": errors,
            "success_rate": (len(times) / iterations) * 100,
            "min_time": min(times),
            "max_time": max(times),
            "mean_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "total_time": sum(times)
        }
    
    async def compare_tools(
        self,
        tool_configs: List[Dict[str, Any]],
        iterations: int = 50
    ) -> Dict[str, Any]:
        """Compare performance of multiple tools"""
        results = {}
        
        for config in tool_configs:
            tool_name = config["tool_name"]
            parameters = config["parameters"]
            
            result = await self.benchmark_tool(tool_name, parameters, iterations)
            results[tool_name] = result
        
        # Find fastest and slowest tools
        successful_results = {k: v for k, v in results.items() if v["success_rate"] > 0}
        
        if successful_results:
            fastest_tool = min(successful_results.items(), key=lambda x: x[1]["mean_time"])
            slowest_tool = max(successful_results.items(), key=lambda x: x[1]["mean_time"])
            
            comparison = {
                "fastest_tool": {
                    "name": fastest_tool[0],
                    "mean_time": fastest_tool[1]["mean_time"]
                },
                "slowest_tool": {
                    "name": slowest_tool[0],
                    "mean_time": slowest_tool[1]["mean_time"]
                },
                "performance_ratio": slowest_tool[1]["mean_time"] / fastest_tool[1]["mean_time"]
            }
        else:
            comparison = {"message": "No successful tool executions"}
        
        return {
            "results": results,
            "comparison": comparison
        }


class ToolIntegrationTester:
    """Integration testing for tool workflows"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.tool_registry = tool_registry or ToolRegistry()
    
    async def test_tool_chain(
        self,
        tool_chain: List[Dict[str, Any]],
        expected_final_result: Any = None
    ) -> Dict[str, Any]:
        """Test a chain of tools working together"""
        results = []
        current_context = {}
        
        for i, step in enumerate(tool_chain):
            tool_name = step["tool_name"]
            parameters = step["parameters"]
            
            # Resolve parameters using context
            resolved_params = {}
            for key, value in parameters.items():
                if isinstance(value, str) and value.startswith("$"):
                    var_name = value[1:]
                    resolved_params[key] = current_context.get(var_name, value)
                else:
                    resolved_params[key] = value
            
            try:
                result = await self.tool_registry.execute_tool(tool_name, resolved_params)
                
                # Store result in context if output_key specified
                if "output_key" in step:
                    current_context[step["output_key"]] = result
                
                results.append({
                    "step": i + 1,
                    "tool_name": tool_name,
                    "parameters": resolved_params,
                    "result": result,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "step": i + 1,
                    "tool_name": tool_name,
                    "parameters": resolved_params,
                    "error": str(e),
                    "success": False
                })
                break
        
        # Check final result
        final_success = False
        if expected_final_result is not None and results:
            last_result = results[-1]
            if last_result["success"]:
                final_success = last_result["result"] == expected_final_result
        
        return {
            "success": all(r["success"] for r in results),
            "final_success": final_success,
            "steps": results,
            "final_context": current_context
        }


# Predefined test cases for common tools
def create_math_tool_tests() -> List[TestCase]:
    """Create test cases for math tools"""
    return [
        TestCase(
            name="Basic addition",
            tool_name="add",
            parameters={"a": 2, "b": 3},
            expected_result=5,
            description="Test basic addition"
        ),
        TestCase(
            name="Negative numbers",
            tool_name="add",
            parameters={"a": -1, "b": 1},
            expected_result=0,
            description="Test addition with negative numbers"
        ),
        TestCase(
            name="Multiplication test",
            tool_name="multiply",
            parameters={"a": 4, "b": 5},
            expected_result=20,
            description="Test multiplication"
        ),
        TestCase(
            name="Division by zero",
            tool_name="divide",
            parameters={"a": 10, "b": 0},
            expected_error="division by zero",
            description="Test division by zero error"
        )
    ]


def create_file_tool_tests() -> List[TestCase]:
    """Create test cases for file tools"""
    return [
        TestCase(
            name="Read existing file",
            tool_name="read_text_file",
            parameters={"file_path": "test_file.txt"},
            description="Test reading an existing file"
        ),
        TestCase(
            name="Read non-existent file",
            tool_name="read_text_file",
            parameters={"file_path": "non_existent.txt"},
            expected_error="No such file",
            description="Test reading non-existent file"
        ),
        TestCase(
            name="Write file",
            tool_name="write_text_file",
            parameters={"file_path": "test_output.txt", "content": "Hello World"},
            description="Test writing to file"
        )
    ]


def create_data_processing_tests() -> List[TestCase]:
    """Create test cases for data processing tools"""
    csv_data = "name,age\nJohn,30\nJane,25"
    json_data = '[{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]'
    
    return [
        TestCase(
            name="CSV to JSON conversion",
            tool_name="csv_to_json",
            parameters={"csv_data": csv_data},
            description="Test CSV to JSON conversion"
        ),
        TestCase(
            name="JSON to CSV conversion",
            tool_name="json_to_csv",
            parameters={"json_data": json_data},
            description="Test JSON to CSV conversion"
        ),
        TestCase(
            name="Data filtering",
            tool_name="filter_data",
            parameters={
                "data": json_data,
                "field": "age",
                "value": "30",
                "operator": "eq"
            },
            description="Test data filtering"
        )
    ]


# Global test suite
test_suite = ToolTestSuite()
performance_tester = ToolPerformanceTester()
integration_tester = ToolIntegrationTester()


# Convenience functions for testing
async def run_basic_tests() -> Dict[str, Any]:
    """Run basic tests for all registered tools"""
    # Add common test cases
    test_suite.add_test_cases(create_math_tool_tests())
    test_suite.add_test_cases(create_file_tool_tests())
    test_suite.add_test_cases(create_data_processing_tests())
    
    # Run tests
    results = await test_suite.run_all_tests()
    
    return test_suite.get_test_summary()


async def benchmark_all_tools(iterations: int = 50) -> Dict[str, Any]:
    """Benchmark all registered tools"""
    tool_configs = []
    
    for tool in test_suite.tool_registry.list_tools():
        # Create simple test parameters based on tool schema
        parameters = {}
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            schema = tool.inputSchema
            if 'properties' in schema:
                for param_name, param_info in schema['properties'].items():
                    param_type = param_info.get('type', 'string')
                    if param_type == 'string':
                        parameters[param_name] = "test_value"
                    elif param_type == 'number':
                        parameters[param_name] = 42
                    elif param_type == 'integer':
                        parameters[param_name] = 42
                    elif param_type == 'boolean':
                        parameters[param_name] = True
        
        tool_configs.append({
            "tool_name": tool.name,
            "parameters": parameters
        })
    
    return await performance_tester.compare_tools(tool_configs, iterations)


def generate_test_report() -> str:
    """Generate a test report in markdown format"""
    summary = test_suite.get_test_summary()
    
    report = "# Tool Test Report\n\n"
    report += f"## Summary\n\n"
    report += f"- **Total Tests:** {summary['total_tests']}\n"
    report += f"- **Passed:** {summary['passed_tests']}\n"
    report += f"- **Failed:** {summary['failed_tests']}\n"
    report += f"- **Success Rate:** {summary['success_rate']:.1f}%\n"
    report += f"- **Total Time:** {summary['total_execution_time']:.2f}s\n"
    report += f"- **Average Time:** {summary['average_execution_time']:.2f}s\n\n"
    
    if summary['failed_cases']:
        report += "## Failed Tests\n\n"
        for case in summary['failed_cases']:
            report += f"- **{case['name']}** ({case['tool']}): {case['error']}\n"
    
    return report 