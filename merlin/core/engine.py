import re
import json
import asyncio
from openai import AsyncOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from ..tools import ToolRegistry

class MerlinEngine:
    def __init__(self, model, api_key, system_prompt):
        self.model = model
        self.client = AsyncOpenAI(
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
        pattern = r'<(p?)(?P<name>\w+)(?P<attrs>[^/>]*)(?:/>|>(?P<content>.*?)</(?P=name)>)'
        
        for match in re.finditer(pattern, text, re.DOTALL):
            tool_name = match.group('name')
            attrs_str = match.group('attrs')
            content = match.group('content').strip() if match.group('content') else ""
            
            if tool_name not in self.registry.tools and tool_name != "done":
                continue

            params = {}
            attr_pattern = r'(\w+)="([^"]*)"'
            for attr_match in re.finditer(attr_pattern, attrs_str):
                params[attr_match.group(1)] = attr_match.group(2)
            
            if content:
                if tool_name == "write_file": params["content"] = content
                elif tool_name == "run_shell_command" and not params.get("command"): params["command"] = content
            
            calls.append((tool_name, params))
            
        return calls

    async def run(self, task, max_loops=10):
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        self.console.print(f"[bold cyan]MERLIN-OS Autonomous Mode[/bold cyan] | [dim]Model: {self.model}[/dim]")
        self.console.print(f"[bold green]>[/bold green] {task}\n")

        for i in range(max_loops):
            content = ""
            with self.console.status(f"[dim cyan]Consulting Oracle (Loop {i+1})...[/dim cyan]", spinner="dots"):
                try:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages,
                        stream=True
                    )
                except Exception as e:
                    self.console.print(f"[bold red]API ERROR:[/bold red] {e}")
                    return False
            
            self.console.print("[bold gold1]MERLIN > [/bold gold1]", end="")
            in_tag = False
            tag_buffer = ""
            
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    content += text
                    
                    for char in text:
                        if char == '<':
                            in_tag = True
                            tag_buffer += char
                        elif char == '>':
                            in_tag = False
                            tag_buffer += char
                            tag_buffer = ""
                        elif in_tag:
                            tag_buffer += char
                        else:
                            self.console.print(char, end="")
                            
            self.console.print()
            self.messages.append({"role": "assistant", "content": content})

            calls = self._parse_tool_calls(content)
            if not calls:
                break

            feedback = []
            tool_failures = 0
            for tool_name, params in calls:
                if tool_name == "done":
                    self.console.print(f"✅ [bold green]DONE:[/bold green] {params.get('summary', 'Task complete.')}")
                    return True
                
                self.console.print(f"⚡ [bold cyan]EXEC:[/bold cyan] [dim]{tool_name}[/dim]")
                tool = self.registry.get_tool(tool_name)
                if tool:
                    with self.console.status(f"[dim]Executing {tool_name}...[/dim]", spinner="bouncingBar"):
                        result = tool.execute(**params)
                    
                    if "error" in result:
                        tool_failures += 1
                        self.console.print(f"❌ [bold red]ERROR:[/bold red] Tool failed.")
                    
                    if tool_name == "activate_skill" and "instructions" in result:
                        instr = result["instructions"]
                        self.messages.append({"role": "system", "content": f"<activated_skill name=\"{params['skill_name']}\">\n{instr}\n</activated_skill>"})
                        self.console.print(f"✨ [bold magenta]SKILL ACTIVATED:[/bold magenta] {params['skill_name']}")

                    feedback.append(f"Tool {tool_name} returned:\n{json.dumps(result, indent=2)}")
                else:
                    feedback.append(f"Error: Tool {tool_name} not found.")
                    tool_failures += 1

            if feedback:
                if tool_failures > 0:
                    feedback.append("\n[SYSTEM NOTE] Some tools failed. Re-evaluate your approach, check file paths, or use `read_file` to confirm the current state before retrying.")
                self.messages.append({"role": "user", "content": "\n\n".join(feedback)})
        
        self.console.print("[bold yellow]Max loops reached.[/bold yellow]")
        return False
