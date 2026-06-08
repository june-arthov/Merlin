import os
from .base import BaseTool

class ActivateSkill(BaseTool):
    def __init__(self, skill_loader):
        self.skill_loader = skill_loader

    @property
    def name(self):
        return "activate_skill"

    @property
    def description(self):
        return "Activates a specialized skill and injects its instructions into the context."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "skill_name": {"type": "string", "description": "Name of the skill to activate."}
            },
            "required": ["skill_name"]
        }

    def execute(self, skill_name):
        skill_info = self.skill_loader.get_skill_info(skill_name)
        if not skill_info:
            return {"error": f"Skill '{skill_name}' not found."}
        
        # In a real scenario, this would notify the engine to inject prompt
        # For this implementation, we return the instructions to be added to history
        return {
            "status": "activated",
            "skill": skill_name,
            "instructions": skill_info.get("instructions", "No specific instructions.")
        }
