import re
import json
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from ..tools import ToolRegistry

class MerlinEngine:
    def __init__(self, model, api_key, system_prompt):
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/june-arthov/Merlin",
                "X-Title": "MERLIN-CLI-TIER3"
            }
        )
        self.system_prompt = system_prompt
        self.registry = ToolRegistry()
        self.messages = []
        self.console = Console()

    def register_tool(self, tool):
        self.registry.register(tool)

    def _parse_tool_calls(self, text):
        calls = []
        # Support both <tool_name /> and <tool_name>...</tool_name>
        # Simple regex for XML-like tags
        pattern = r'<(p?)(?P<name>\w+)(?P<attrs>[^/>]*)(?:/>|>(?P<content>.*?)</(?P=name)>)'
        
        for match in re.finditer(pattern, text, re.DOTALL):
            tool_name = match.group('name')
            attrs_str = match.group('attrs')
            content = match.group('content').strip() if match.group('content') else ""
            
            if tool_name not in self.registry.tools and tool_name != "done":
                continue

            # Parse attributes
            params = {}
            attr_pattern = r'(\w+)="([^"]*)"'
            for attr_match in re.finditer(attr_pattern, attrs_str):
                params[attr_match.group(1)] = attr_match.group(2)
            
            # Map content to parameter
            if content:
                if tool_name == "write_file":
                    params["content"] = content
                elif tool_name == "run_shell_command" and not params.get("command"):
                    params["command"] = content
            
            calls.append((tool_name, params))
            
        return calls

    def run(self, task, max_loops=10):
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        self.console.print(Panel(f"[bold green]TASK:[/bold green] {task}", title="MERLIN TIER-3"))

        for i in range(max_loops):
            self.console.print(f"\n[bold blue]Loop {i+1}/{max_loops}[/bold blue] - Consulting Oracle...")
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages
                )
                content = response.choices[0].message.content or ""
                self.messages.append({"role": "assistant", "content": content})
                
                # Print reasoning using Markdown
                reasoning = re.sub(r'<[^>]+>.*?</[^>]+>', '', content, flags=re.DOTALL).strip()
                if reasoning:
                    self.console.print(Markdown(reasoning))

                calls = self._parse_tool_calls(content)
                if not calls:
                    self.console.print("[yellow]No tool calls found.[/yellow]")
                    break

                feedback = []
                tool_failures = 0
                for tool_name, params in calls:
                    if tool_name == "done":
                        self.console.print(Panel(f"[bold green]DONE:[/bold green] {params.get('summary', 'Task complete.')}", border_style="green"))
                        return True
                    
                    self.console.print(f"[bold cyan]EXEC:[/bold cyan] [italic]{tool_name}[/italic]({params if len(str(params)) < 100 else '...'})")
                    tool = self.registry.get_tool(tool_name)
                    if tool:
                        result = tool.execute(**params)
                        
                        if "error" in result:
                            tool_failures += 1
                        
                        # Special handling for activate_skill to inject instructions immediately
                        if tool_name == "activate_skill" and "instructions" in result:
                            instr = result["instructions"]
                            self.messages.append({
                                "role": "system",
                                "content": f"<activated_skill name=\"{params['skill_name']}\">\n{instr}\n</activated_skill>"
                            })
                            self.console.print(f"[bold magenta]SKILL ACTIVATED:[/bold magenta] {params['skill_name']}")

                        feedback_str = f"Tool {tool_name} returned:\n{json.dumps(result, indent=2)}"
                        feedback.append(feedback_str)
                    else:
                        feedback.append(f"Error: Tool {tool_name} not found.")
                        tool_failures += 1

                if feedback:
                    # Self-Correction Guidance
                    if tool_failures > 0:
                        feedback.append("\n[SYSTEM NOTE] Some tools failed. Re-evaluate your approach, check file paths, or use `read_file` to confirm the current state before retrying.")
                    
                    self.messages.append({
                        "role": "user",
                        "content": "\n\n".join(feedback)
                    })
            except Exception as e:
                self.console.print(f"[bold red]API ERROR:[/bold red] {e}")
                return False
        
        self.console.print("[bold yellow]Max loops reached.[/bold yellow]")
        return False
