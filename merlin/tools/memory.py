import os
from .base import BaseTool

class UpdateMemory(BaseTool):
    @property
    def name(self): return "update_memory"
    
    @property
    def category(self): return "memory"
    
    @property
    def description(self): return "Updates the private MEMORY.md file with new information."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "fact": {"type": "string", "description": "The fact or note to save."},
                "category": {"type": "string", "description": "Category (e.g., preference, project_setup)."}
            },
            "required": ["fact"]
        }

    def execute(self, fact, category="general"):
        path = os.path.expanduser("~/.merlin/MEMORY.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(f"\n- [{category}] {fact}")
            return {"status": "success", "path": path}
        except Exception as e:
            return {"error": str(e)}

class UpdateProjectInstructions(BaseTool):
    @property
    def name(self): return "update_project_instructions"
    
    @property
    def category(self): return "memory"
    
    @property
    def description(self): return "Updates the MERLIN.md file with repo-wide rules."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "rule": {"type": "string", "description": "The rule or instruction to add."}
            },
            "required": ["rule"]
        }

    def execute(self, rule):
        path = "MERLIN.md"
        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(f"\n- {rule}")
            return {"status": "success", "path": path}
        except Exception as e:
            return {"error": str(e)}
