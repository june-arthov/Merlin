import json
from abc import ABC, abstractmethod

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def parameters(self):
        """Returns JSON schema of parameters."""
        pass

    @abstractmethod
    def execute(self, **kwargs):
        pass

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool

    def get_tool(self, name):
        return self.tools.get(name)

    def get_definitions(self):
        """Returns tool definitions for LLM system prompt."""
        defs = []
        for name, tool in self.tools.items():
            defs.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            })
        return defs
