import os
from .base import BaseTool

class Plan(BaseTool):
    @property
    def name(self): return "plan"
    
    @property
    def category(self): return "planning"
    
    @property
    def description(self): return "Writes a detailed implementation plan to a file."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the plan."},
                "content": {"type": "string", "description": "Detailed steps and strategy."}
            },
            "required": ["title", "content"]
        }

    def execute(self, title, content):
        path = "PLAN.md"
        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n# Plan: {title}\n{content}\n")
            return {"status": "success", "message": f"Plan '{title}' saved to PLAN.md"}
        except Exception as e:
            return {"error": str(e)}
