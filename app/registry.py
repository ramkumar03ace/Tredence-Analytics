from typing import Callable, Dict, Any

class ToolRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance.tools: Dict[str, Callable] = {}
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, name: str, func: Callable):
        self.tools[name] = func
        return func

    def get_tool(self, name: str) -> Callable:
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.keys())

# Global instance
registry = ToolRegistry()

def register_tool(name: str = None):
    """Decorator to register a function as a tool."""
    def decorator(func):
        tool_name = name if name else func.__name__
        registry.register(tool_name, func)
        return func
    return decorator
