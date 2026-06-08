from merlin.tools.base import BaseTool

class HelloTool(BaseTool):
    @property
    def name(self):
        return "hello_world"

    @property
    def description(self):
        return "Says hello to the world."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name to greet."}
            }
        }

    def execute(self, name="World"):
        return {"message": f"Hello, {name}! Merlin-CLI Tier-3 is alive."}

def register_tools():
    return [HelloTool()]
