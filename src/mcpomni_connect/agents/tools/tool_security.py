import re
import hashlib
import hmac
import secrets
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum
from .local_tools_registry import ToolRegistry
import time


class SecurityLevel(Enum):
    """Security levels for tools"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityPolicy:
    """Security policy for a tool"""
    tool_name: str
    allowed_users: Set[str] = None
    allowed_roles: Set[str] = None
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    max_execution_time: Optional[float] = None
    allowed_parameters: Set[str] = None
    forbidden_parameters: Set[str] = None
    parameter_validation: Dict[str, Callable] = None
    rate_limit: Optional[int] = None  # executions per minute
    require_authentication: bool = True
    audit_logging: bool = True
    
    def __post_init__(self):
        if self.allowed_users is None:
            self.allowed_users = set()
        if self.allowed_roles is None:
            self.allowed_roles = set()
        if self.allowed_parameters is None:
            self.allowed_parameters = set()
        if self.forbidden_parameters is None:
            self.forbidden_parameters = set()
        if self.parameter_validation is None:
            self.parameter_validation = {}


class SecurityViolation(Exception):
    """Exception raised for security violations"""
    pass


class AccessDeniedException(SecurityViolation):
    """Exception raised when access is denied"""
    pass


class ParameterValidationException(SecurityViolation):
    """Exception raised when parameter validation fails"""
    pass


class RateLimitException(SecurityViolation):
    """Exception raised when rate limit is exceeded"""
    pass


class SecurityValidator:
    """Validator for security policies"""
    
    def __init__(self):
        self.common_forbidden_patterns = [
            r"\.\./",  # Directory traversal
            r"<script",  # XSS
            r"javascript:",  # JavaScript injection
            r"data:text/html",  # Data URL injection
            r"file://",  # File protocol
            r"ftp://",  # FTP protocol
            r"gopher://",  # Gopher protocol
        ]
    
    def validate_parameter(self, param_name: str, param_value: Any, policy: SecurityPolicy) -> bool:
        """Validate a parameter against security policy"""
        # Check forbidden parameters
        if param_name in policy.forbidden_parameters:
            raise ParameterValidationException(f"Parameter '{param_name}' is forbidden")
        
        # Check allowed parameters (if specified)
        if policy.allowed_parameters and param_name not in policy.allowed_parameters:
            raise ParameterValidationException(f"Parameter '{param_name}' is not allowed")
        
        # Check for forbidden patterns in string values
        if isinstance(param_value, str):
            for pattern in self.common_forbidden_patterns:
                if re.search(pattern, param_value, re.IGNORECASE):
                    raise ParameterValidationException(f"Parameter '{param_name}' contains forbidden pattern: {pattern}")
        
        # Apply custom validation
        if param_name in policy.parameter_validation:
            validator = policy.parameter_validation[param_name]
            if not validator(param_value):
                raise ParameterValidationException(f"Parameter '{param_name}' failed custom validation")
        
        return True
    
    def validate_parameters(self, parameters: Dict[str, Any], policy: SecurityPolicy) -> bool:
        """Validate all parameters against security policy"""
        for param_name, param_value in parameters.items():
            self.validate_parameter(param_name, param_value, policy)
        return True


class RateLimiter:
    """Rate limiting for tool execution"""
    
    def __init__(self):
        self.execution_times: Dict[str, List[float]] = {}
    
    def check_rate_limit(self, tool_name: str, rate_limit: int) -> bool:
        """Check if rate limit is exceeded"""
        current_time = time.time()
        
        if tool_name not in self.execution_times:
            self.execution_times[tool_name] = []
        
        # Remove executions older than 1 minute
        self.execution_times[tool_name] = [
            t for t in self.execution_times[tool_name]
            if current_time - t < 60
        ]
        
        # Check if limit exceeded
        if len(self.execution_times[tool_name]) >= rate_limit:
            return False
        
        # Add current execution
        self.execution_times[tool_name].append(current_time)
        return True


class SecurityManager:
    """Manager for tool security"""
    
    def __init__(self):
        self.policies: Dict[str, SecurityPolicy] = {}
        self.validator = SecurityValidator()
        self.rate_limiter = RateLimiter()
        self.audit_log: List[Dict[str, Any]] = []
        self.secret_key = secrets.token_hex(32)
    
    def add_policy(self, policy: SecurityPolicy):
        """Add a security policy for a tool"""
        self.policies[policy.tool_name] = policy
    
    def get_policy(self, tool_name: str) -> Optional[SecurityPolicy]:
        """Get security policy for a tool"""
        return self.policies.get(tool_name)
    
    def check_access(self, tool_name: str, user: str = None, roles: List[str] = None) -> bool:
        """Check if user has access to tool"""
        policy = self.get_policy(tool_name)
        if not policy:
            return True  # No policy means open access
        
        if not policy.require_authentication:
            return True
        
        # Check user access
        if policy.allowed_users and user not in policy.allowed_users:
            return False
        
        # Check role access
        if policy.allowed_roles and not any(role in policy.allowed_roles for role in (roles or [])):
            return False
        
        return True
    
    def validate_execution(self, tool_name: str, parameters: Dict[str, Any], user: str = None, roles: List[str] = None) -> bool:
        """Validate tool execution against security policies"""
        policy = self.get_policy(tool_name)
        if not policy:
            return True
        
        # Check access
        if not self.check_access(tool_name, user, roles):
            raise AccessDeniedException(f"Access denied to tool '{tool_name}'")
        
        # Check rate limit
        if policy.rate_limit and not self.rate_limiter.check_rate_limit(tool_name, policy.rate_limit):
            raise RateLimitException(f"Rate limit exceeded for tool '{tool_name}'")
        
        # Validate parameters
        self.validator.validate_parameters(parameters, policy)
        
        return True
    
    def log_execution(self, tool_name: str, parameters: Dict[str, Any], user: str = None, success: bool = True, error: str = None):
        """Log tool execution for audit"""
        log_entry = {
            "timestamp": time.time(),
            "tool_name": tool_name,
            "user": user,
            "parameters": parameters,
            "success": success,
            "error": error
        }
        self.audit_log.append(log_entry)
    
    def get_audit_log(self, tool_name: str = None, user: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        filtered_log = self.audit_log
        
        if tool_name:
            filtered_log = [entry for entry in filtered_log if entry["tool_name"] == tool_name]
        
        if user:
            filtered_log = [entry for entry in filtered_log if entry["user"] == user]
        
        return filtered_log[-limit:]
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate security report"""
        return {
            "total_policies": len(self.policies),
            "audit_log_entries": len(self.audit_log),
            "policies_by_level": {
                level.value: len([p for p in self.policies.values() if p.security_level == level])
                for level in SecurityLevel
            },
            "recent_violations": [
                entry for entry in self.audit_log[-10:]
                if not entry["success"]
            ]
        }


class SecureToolRegistry(ToolRegistry):
    """Tool registry with security features"""
    
    def __init__(self, security_manager: SecurityManager = None):
        super().__init__()
        self.security_manager = security_manager or SecurityManager()
        self.current_user = None
        self.current_roles = []
    
    def set_user_context(self, user: str, roles: List[str] = None):
        """Set current user context for security checks"""
        self.current_user = user
        self.current_roles = roles or []
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool with security validation"""
        # Validate execution
        self.security_manager.validate_execution(
            tool_name, parameters, self.current_user, self.current_roles
        )
        
        success = False
        error = None
        
        try:
            # Execute tool
            result = await super().execute_tool(tool_name, parameters)
            success = True
            return result
        except Exception as e:
            error = str(e)
            raise
        finally:
            # Log execution
            self.security_manager.log_execution(
                tool_name, parameters, self.current_user, success, error
            )
    
    def add_security_policy(self, policy: SecurityPolicy):
        """Add security policy for a tool"""
        self.security_manager.add_policy(policy)
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get security report"""
        return self.security_manager.generate_security_report()


# Global secure tool registry
secure_tool_registry = SecureToolRegistry()


# Predefined security policies
def setup_default_security_policies():
    """Setup default security policies for common tools"""
    
    # File operations - high security
    file_policy = SecurityPolicy(
        tool_name="read_text_file",
        security_level=SecurityLevel.HIGH,
        allowed_parameters={"file_path", "encoding"},
        parameter_validation={
            "file_path": lambda path: not path.startswith("/") and ".." not in path
        },
        rate_limit=10,
        require_authentication=True,
        audit_logging=True
    )
    secure_tool_registry.add_security_policy(file_policy)
    
    # Web operations - medium security
    web_policy = SecurityPolicy(
        tool_name="fetch_url",
        security_level=SecurityLevel.MEDIUM,
        allowed_parameters={"url", "timeout"},
        parameter_validation={
            "url": lambda url: url.startswith(("http://", "https://"))
        },
        rate_limit=30,
        require_authentication=False,
        audit_logging=True
    )
    secure_tool_registry.add_security_policy(web_policy)
    
    # Math operations - low security
    math_policy = SecurityPolicy(
        tool_name="calculate",
        security_level=SecurityLevel.LOW,
        allowed_parameters={"expression", "variables"},
        parameter_validation={
            "expression": lambda expr: all(c in "0123456789+-*/(). " for c in expr)
        },
        rate_limit=100,
        require_authentication=False,
        audit_logging=False
    )
    secure_tool_registry.add_security_policy(math_policy)


# Security decorators
def require_authentication(func: Callable) -> Callable:
    """Decorator to require authentication for a tool"""
    def wrapper(*args, **kwargs):
        if not secure_tool_registry.current_user:
            raise AccessDeniedException("Authentication required")
        return func(*args, **kwargs)
    return wrapper


def require_role(role: str):
    """Decorator to require a specific role"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            if role not in secure_tool_registry.current_roles:
                raise AccessDeniedException(f"Role '{role}' required")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limited(calls_per_minute: int):
    """Decorator to rate limit a function"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            if not secure_tool_registry.rate_limiter.check_rate_limit(func.__name__, calls_per_minute):
                raise RateLimitException(f"Rate limit exceeded for {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator 