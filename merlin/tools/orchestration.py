import os
import subprocess
import sys
from .base import BaseTool

class InvokeAgent(BaseTool):
    def __init__(self, model, api_key):
        self.model = model
        self.api_key = api_key

    @property
    def name(self):
        return "invoke_agent"

    @property
    def description(self):
        return "Invokes a sub-agent to perform a specific task or investigation. Use this for complex or repetitive work."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "agent_name": {"type": "string", "description": "Name of the sub-agent (e.g., investigator, generalist)."},
                "prompt": {"type": "string", "description": "Detailed task description for the sub-agent."}
            },
            "required": ["agent_name", "prompt"]
        }

    def execute(self, agent_name, prompt):
        # In a real implementation, this would spawn a new MerlinEngine instance
        # For simplicity in this CLI, we simulate it by running the merlin.py as a subprocess
        # or recursively calling the engine.
        
        # Simulation: Run merlin.py with the sub-prompt
        # This keeps the history separate
        try:
            cmd = [sys.executable, "merlin.py", prompt, "-m", self.model]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            return {
                "agent": agent_name,
                "status": "completed" if result.returncode == 0 else "failed",
                "output": result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
            }
        except Exception as e:
            return {"error": str(e)}
