import os
import json
import re
import asyncio
from openai import AsyncOpenAI
from rich.console import Console
from rich.markdown import Markdown
from ..tools import ToolRegistry

class MerlinTUI:
    def __init__(self, model, api_key, system_prompt, registry, loader):
        self.model = model
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={"HTTP-Referer": "https://github.com/june-arthov/Merlin", "X-Title": "MERLIN-CLI-ASYNC"}
        )
        self.system_prompt = system_prompt
        self.registry = registry
        self.loader = loader
        self.console = Console()
        self.persistent_messages = [{"role": "system", "content": self.system_prompt}]
        self.max_loops = 10

    async def start_shell(self):
        self.console.clear()
        self.console.print("╭─────────────────────────────────────────────────────────────────────────────╮", style="dim")
        self.console.print("│ 🧙‍♂️ [bold gold1]MERLIN-OS[/bold gold1] v3.0.0-Singularity (Async Streaming Active)               │")
        self.console.print(f"│ [dim]Model: {self.model}[/dim]{' ' * max(0, 56 - len(self.model))}│")
        self.console.print("╰─────────────────────────────────────────────────────────────────────────────╯", style="dim")
        self.console.print("✦ [dim]Welcome to the Singularity. Type your task or /help.[/dim]\n")
        
        while True:
            try:
                task = self.console.input("[bold green]❯ [/bold green]")
                if task.lower() in ["exit", "quit", "bye"]:
                    self.console.print("[dim]Terminating connection...[/dim]")
                    break
                if task.lower() == "/clear":
                    self.persistent_messages = [{"role": "system", "content": self.system_prompt}]
                    self.console.print("[dim]Neural link reset.[/dim]\n")
                    continue
                if not task.strip():
                    continue
                
                await self.run_task(task)
                self.console.print()
            except KeyboardInterrupt:
                self.console.print("\n[dim]Task interrupted.[/dim]\n")
            except Exception as e:
                self.console.print(f"\n[bold red]System Error:[/bold red] {e}\n")

    async def run_task(self, task):
        self.persistent_messages.append({"role": "user", "content": task})
        
        for i in range(self.max_loops):
            content = ""
            
            # Show a thinking status
            with self.console.status(f"[dim cyan]Consulting Oracle (Loop {i+1})...[/dim cyan]", spinner="dots"):
                try:
                    response = await self.client.chat.completions.create(
                        model=self.model, 
                        messages=self.persistent_messages,
                        stream=True
                    )
                except Exception as e:
                    self.console.print(f"[bold red]API Error:[/bold red] {str(e)}")
                    return

            # Stream the response
            self.console.print("[bold gold1]MERLIN > [/bold gold1]", end="")
            in_tag = False
            tag_buffer = ""
            
            import sys
            async for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    # OpenRouter async stream handling
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content is not None:
                        text = delta.content
                        content += text
                        
                        # Very simple logic to hide XML tags from being streamed to the console
                        for char in text:
                            if char == '<':
                                in_tag = True
                                tag_buffer += char
                            elif char == '>':
                                in_tag = False
                                tag_buffer += char
                                # We don't print the tag buffer
                                tag_buffer = ""
                            elif in_tag:
                                tag_buffer += char
                            else:
                                sys.stdout.write(char)
                                sys.stdout.flush()
            
            print() # Newline after streaming
            self.persistent_messages.append({"role": "assistant", "content": content})
            
            # Parse tools
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

            # Execute tools
            feedback = []
            for t_name, t_params in calls:
                if t_name == "done":
                    summary = t_params.get('summary', 'Task complete.')
                    self.console.print(f"✅ [bold green]DONE:[/bold green] {summary}")
                    return
                
                self.console.print(f"⚡ [bold cyan]EXEC:[/bold cyan] [dim]{t_name}[/dim]")
                tool = self.registry.get_tool(t_name)
                if tool:
                    with self.console.status(f"[dim]Executing {t_name}...[/dim]", spinner="bouncingBar"):
                        # Tools are currently synchronous
                        res = tool.execute(**t_params)
                        
                    if t_name == "activate_skill" and "instructions" in res:
                        self.persistent_messages.append({"role": "system", "content": f"<activated_skill name=\"{t_params['skill_name']}\">{res['instructions']}</activated_skill>"})
                        self.console.print(f"✨ [bold magenta]SKILL_ACTIVATED:[/bold magenta] {t_params['skill_name']}")
                    
                    feedback.append(f"Tool {t_name} returned:\n{json.dumps(res, indent=2)}")
                else:
                    feedback.append(f"Error: Tool {t_name} not found.")
                    self.console.print(f"❌ [bold red]ERROR:[/bold red] Tool {t_name} not found.")

            if feedback:
                self.persistent_messages.append({"role": "user", "content": "\n\n".join(feedback)})
