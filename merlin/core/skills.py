import os
import importlib.util
from ..tools.base import BaseTool

class SkillLoader:
    def __init__(self, registry):
        self.registry = registry
        self.available_skills = {}

    def load_skills(self, skills_dir):
        if not os.path.exists(skills_dir):
            return

        for item in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, item)
            if os.path.isdir(skill_path):
                self.available_skills[item] = {"path": skill_path}
                
                # Look for SKILL.md for instructions
                skill_md = os.path.join(skill_path, "SKILL.md")
                if os.path.exists(skill_md):
                    with open(skill_md, 'r', encoding='utf-8') as f:
                        self.available_skills[item]["instructions"] = f.read()

                # Look for a .py file that defines tools
                for file in os.listdir(skill_path):
                    if file.endswith("_tool.py"):
                        self._load_from_file(os.path.join(skill_path, file))

    def get_skill_info(self, skill_name):
        return self.available_skills.get(skill_name)

    def _load_from_file(self, file_path):
        spec = importlib.util.spec_from_file_location("skill_module", file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for register_tools function
            if hasattr(module, "register_tools"):
                tools = module.register_tools()
                for tool in tools:
                    self.registry.register(tool)
