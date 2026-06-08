import os
import importlib.util
import sys
from .base import BaseTool

class CreateTool(BaseTool):
    def __init__(self, registry):
        self.registry = registry

    @property
    def name(self):
        return "create_tool"

    @property
    def description(self):
        return "Synthesizes a new Python tool and registers it into the system at runtime. Use this when you need a capability that doesn't exist."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "tool_name": {"type": "string", "description": "The class name of the tool (PascalCase)."},
                "code": {"type": "string", "description": "Full Python code for the tool class inheriting from BaseTool."},
                "file_name": {"type": "string", "description": "Filename to save the tool (e.g., custom_tool.py)."}
            },
            "required": ["tool_name", "code", "file_name"]
        }

    def execute(self, tool_name, code, file_name):
        tools_dir = os.path.join(os.getcwd(), "merlin", "tools", "dynamic")
        os.makedirs(tools_dir, exist_ok=True)
        # Ensure __init__.py exists
        init_file = os.path.join(tools_dir, "__init__.py")
        if not os.path.exists(init_file):
            open(init_file, 'a').close()

        file_path = os.path.join(tools_dir, file_name)
        
        try:
            # Wrap code with necessary imports if missing
            if "from ..base import BaseTool" not in code and "from .base import BaseTool" not in code:
                code = "from merlin.tools.base import BaseTool\n" + code
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Dynamic Import
            spec = importlib.util.spec_from_file_location(tool_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get class and instantiate
            tool_class = getattr(module, tool_name)
            tool_instance = tool_class()
            
            # Register to system
            self.registry.register(tool_instance)
            
            return {
                "status": "success",
                "message": f"Tool '{tool_instance.name}' has been synthesized and registered.",
                "path": file_path
            }
        except Exception as e:
            return {"error": f"Synthesis failed: {str(e)}"}
