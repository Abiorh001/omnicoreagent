import asyncio
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from .local_tools_registry import ToolRegistry


@dataclass
class ToolStep:
    """A single step in a tool composition"""
    tool_name: str
    parameters: Dict[str, Any]
    output_key: Optional[str] = None
    condition: Optional[str] = None
    retry_count: int = 0
    timeout: Optional[float] = None


@dataclass
class CompositionResult:
    """Result of a tool composition execution"""
    success: bool
    outputs: Dict[str, Any]
    errors: List[str]
    execution_time: float
    steps_executed: List[str]


class ToolComposition:
    """Tool composition for chaining multiple tools together"""
    
    def __init__(self, name: str, tool_registry: ToolRegistry = None):
        self.name = name
        self.tool_registry = tool_registry or ToolRegistry()
        self.steps: List[ToolStep] = []
        self.variables: Dict[str, Any] = {}
    
    def add_step(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        output_key: Optional[str] = None,
        condition: Optional[str] = None,
        retry_count: int = 0,
        timeout: Optional[float] = None
    ) -> 'ToolComposition':
        """Add a step to the composition"""
        step = ToolStep(
            tool_name=tool_name,
            parameters=parameters,
            output_key=output_key,
            condition=condition,
            retry_count=retry_count,
            timeout=timeout
        )
        self.steps.append(step)
        return self
    
    def set_variable(self, name: str, value: Any) -> 'ToolComposition':
        """Set a variable for use in the composition"""
        self.variables[name] = value
        return self
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition string"""
        try:
            # Simple condition evaluation (use with caution in production)
            # Replace variables with their values
            for var_name, var_value in context.items():
                condition = condition.replace(f"${var_name}", str(var_value))
            
            # Only allow safe operations
            allowed_chars = set('0123456789+-*/().<>!=&|"\' ')
            if not all(c in allowed_chars for c in condition):
                return False
            
            return eval(condition)
        except Exception:
            return False
    
    def _resolve_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameter values using context variables"""
        resolved = {}
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith('$'):
                var_name = value[1:]
                resolved[key] = context.get(var_name, value)
            else:
                resolved[key] = value
        return resolved
    
    async def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> CompositionResult:
        """Execute the tool composition"""
        import time
        start_time = time.time()
        
        context = {**self.variables}
        if initial_context:
            context.update(initial_context)
        
        outputs = {}
        errors = []
        steps_executed = []
        
        for i, step in enumerate(self.steps):
            try:
                # Check condition if present
                if step.condition and not self._evaluate_condition(step.condition, context):
                    continue
                
                # Resolve parameters
                resolved_params = self._resolve_parameters(step.parameters, context)
                
                # Execute tool with retry logic
                result = None
                last_error = None
                
                for attempt in range(step.retry_count + 1):
                    try:
                        if step.timeout:
                            result = await asyncio.wait_for(
                                self.tool_registry.execute_tool(step.tool_name, resolved_params),
                                timeout=step.timeout
                            )
                        else:
                            result = await self.tool_registry.execute_tool(step.tool_name, resolved_params)
                        break
                    except Exception as e:
                        last_error = str(e)
                        if attempt < step.retry_count:
                            await asyncio.sleep(1)  # Wait before retry
                        else:
                            raise e
                
                # Store output
                if step.output_key:
                    outputs[step.output_key] = result
                    context[step.output_key] = result
                
                steps_executed.append(f"Step {i+1}: {step.tool_name}")
                
            except Exception as e:
                error_msg = f"Step {i+1} ({step.tool_name}) failed: {str(e)}"
                errors.append(error_msg)
                # Continue with next step unless it's critical
        
        execution_time = time.time() - start_time
        
        return CompositionResult(
            success=len(errors) == 0,
            outputs=outputs,
            errors=errors,
            execution_time=execution_time,
            steps_executed=steps_executed
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert composition to dictionary"""
        return {
            "name": self.name,
            "steps": [
                {
                    "tool_name": step.tool_name,
                    "parameters": step.parameters,
                    "output_key": step.output_key,
                    "condition": step.condition,
                    "retry_count": step.retry_count,
                    "timeout": step.timeout
                }
                for step in self.steps
            ],
            "variables": self.variables
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], tool_registry: ToolRegistry = None) -> 'ToolComposition':
        """Create composition from dictionary"""
        composition = cls(data["name"], tool_registry)
        
        for step_data in data["steps"]:
            composition.add_step(
                tool_name=step_data["tool_name"],
                parameters=step_data["parameters"],
                output_key=step_data.get("output_key"),
                condition=step_data.get("condition"),
                retry_count=step_data.get("retry_count", 0),
                timeout=step_data.get("timeout")
            )
        
        if "variables" in data:
            composition.variables = data["variables"]
        
        return composition


class ToolCompositionManager:
    """Manager for tool compositions"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.compositions: Dict[str, ToolComposition] = {}
    
    def create_composition(self, name: str) -> ToolComposition:
        """Create a new composition"""
        composition = ToolComposition(name, self.tool_registry)
        self.compositions[name] = composition
        return composition
    
    def get_composition(self, name: str) -> Optional[ToolComposition]:
        """Get a composition by name"""
        return self.compositions.get(name)
    
    def list_compositions(self) -> List[str]:
        """List all composition names"""
        return list(self.compositions.keys())
    
    def save_composition(self, name: str, file_path: str):
        """Save a composition to a file"""
        composition = self.get_composition(name)
        if not composition:
            raise ValueError(f"Composition '{name}' not found")
        
        with open(file_path, 'w') as f:
            json.dump(composition.to_dict(), f, indent=2)
    
    def load_composition(self, file_path: str) -> ToolComposition:
        """Load a composition from a file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        composition = ToolComposition.from_dict(data, self.tool_registry)
        self.compositions[composition.name] = composition
        return composition
    
    def register_composition_as_tool(self, composition_name: str, tool_name: str = None) -> str:
        """Register a composition as a tool in the registry"""
        composition = self.get_composition(composition_name)
        if not composition:
            raise ValueError(f"Composition '{composition_name}' not found")
        
        tool_name = tool_name or f"compose_{composition_name}"
        
        async def composition_tool(parameters: Dict[str, Any]) -> str:
            result = await composition.execute(parameters)
            return json.dumps({
                "success": result.success,
                "outputs": result.outputs,
                "errors": result.errors,
                "execution_time": result.execution_time,
                "steps_executed": result.steps_executed
            }, indent=2)
        
        # Register the composition as a tool
        self.tool_registry.register(
            name=tool_name,
            description=f"Execute composition: {composition.name}",
            inputSchema={
                "type": "object",
                "properties": {
                    "initial_context": {
                        "type": "object",
                        "description": "Initial context variables for the composition"
                    }
                },
                "additionalProperties": True
            }
        )(composition_tool)
        
        return tool_name


# Global composition manager
composition_manager = ToolCompositionManager()


# Convenience functions for common compositions
def create_data_processing_pipeline() -> ToolComposition:
    """Create a common data processing pipeline"""
    composition = composition_manager.create_composition("data_processing_pipeline")
    
    composition.add_step(
        tool_name="csv_to_json",
        parameters={"csv_data": "$input_data"},
        output_key="json_data"
    ).add_step(
        tool_name="filter_data",
        parameters={
            "data": "$json_data",
            "field": "$filter_field",
            "value": "$filter_value"
        },
        output_key="filtered_data"
    ).add_step(
        tool_name="json_to_csv",
        parameters={"json_data": "$filtered_data"},
        output_key="output_csv"
    )
    
    return composition


def create_file_processing_pipeline() -> ToolComposition:
    """Create a common file processing pipeline"""
    composition = composition_manager.create_composition("file_processing_pipeline")
    
    composition.add_step(
        tool_name="read_text_file",
        parameters={"file_path": "$input_file"},
        output_key="file_content"
    ).add_step(
        tool_name="write_text_file",
        parameters={
            "file_path": "$output_file",
            "content": "$file_content"
        }
    )
    
    return composition 