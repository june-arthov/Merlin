import os
import json
import re
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from ..tools import ToolRegistry

class MerlinTUI:
    def __init__(self, model, api_key, system_prompt, registry, loader):
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={"HTTP-Referer": "https://github.com/june-arthov/Merlin", "X-Title": "MERLIN-CLI"}
        )
        self.system_prompt = system_prompt
        self.registry = registry
        self.loader = loader
        self.console = Console()
        self.persistent_messages = [{"role": "system", "content": self.system_prompt}]
        self.max_loops = 10

    def start_shell(self):
        self.console.clear()
        self.console.print("[bold cyan]Merlin-CLI[/bold cyan] [dim]v3.0.0[/dim]")
        self.console.print(f"[dim]Model: {self.model} | Mode: Sovereign Interactive[/dim]\n")
        
        while True:
            try:
                task = self.console.input("[bold green]>[/bold green] ")
                if task.lower() in ["exit", "quit", "bye"]:
                    break
                if task.lower() == "/clear":
                    self.persistent_messages = [{"role": "system", "content": self.system_prompt}]
                    self.console.print("[dim]Conversation history cleared.[/dim]\n")
                    continue
                if not task.strip():
                    continue
                
                self.run_task(task)
                self.console.print() # Empty line for spacing
            except KeyboardInterrupt:
                self.console.print()
                break

    def run_task(self, task):
        self.persistent_messages.append({"role": "user", "content": task})
        
        for i in range(self.max_loops):
            # 1. Show thinking spinner while waiting for LLM
            with self.console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
                try:
                    response = self.client.chat.completions.create(model=self.model, messages=self.persistent_messages)
                    content = response.choices[0].message.content or ""
                except Exception as e:
                    self.console.print(f"[bold red]API Error:[/bold red] {str(e)}")
                    return

            self.persistent_messages.append({"role": "assistant", "content": content})
            
            # 2. Print conversational text (Markdown)
            clean_text = re.sub(r'<[^>]+>.*?</[^>]+>', '', content, flags=re.DOTALL).strip()
            if clean_text:
                self.console.print(Markdown(clean_text))

            # 3. Parse tools
            pattern = r'<(p?)(?P<name>\w+)(?P<attrs>[^/>]*)(?:/>|>(?P<content>.*?)</(?P=name)>)'
            calls = []
            for match in re.finditer(pattern, content, re.DOTALL):
                tool_name = match.group('name')
                if tool_name in self.registry.tools or tool_name == "done":
                    attrs_str = match.group('attrs')
                    params = {}
                    for am in re.finditer(r'(\w+)="([^"]*)"', attrs_str):
                        params[am.group(1)] = am.group(2)
                    inner = match.group('content').strip() if match.group('content') else ""
                    if inner:
                        if tool_name == "write_file": params["content"] = inner
                        elif tool_name == "run_shell_command" and not params.get("command"): params["command"] = inner
                    calls.append((tool_name, params))

            if not calls:
                break

            # 4. Execute tools
            feedback = []
            for t_name, t_params in calls:
                if t_name == "done":
                    summary = t_params.get('summary', 'Task complete.')
                    self.console.print(f"✅ [bold green]Done:[/bold green] {summary}")
                    return
                
                self.console.print(f"⚙️  [dim cyan]Tool Call:[/dim cyan] [bold]{t_name}[/bold]")
                tool = self.registry.get_tool(t_name)
                if tool:
                    # Show spinner while tool executes
                    with self.console.status(f"[dim]Executing {t_name}...[/dim]", spinner="dots"):
                        res = tool.execute(**t_params)
                        
                    if t_name == "activate_skill" and "instructions" in res:
                        self.persistent_messages.append({"role": "system", "content": f"<activated_skill name=\"{t_params['skill_name']}\">{res['instructions']}</activated_skill>"})
                        self.console.print(f"✨ [dim magenta]Skill Activated:[/dim magenta] {t_params['skill_name']}")
                    
                    feedback.append(f"Tool {t_name} returned:\n{json.dumps(res, indent=2)}")
                else:
                    feedback.append(f"Error: Tool {t_name} not found.")
                    self.console.print(f"❌ [bold red]Error:[/bold red] Tool {t_name} not found.")

            if feedback:
                self.persistent_messages.append({"role": "user", "content": "\n\n".join(feedback)})
