import os
import sys
import time
import json
import re
from datetime import datetime
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich.align import Align
from ..tools import ToolRegistry

class MerlinTUI:
    def __init__(self, model, api_key, system_prompt, registry):
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={"HTTP-Referer": "https://github.com/june-arthov/Merlin", "X-Title": "MERLIN-TIER3-TUI"}
        )
        self.system_prompt = system_prompt
        self.registry = registry
        self.console = Console()
        self.layout = Layout()
        self.history = [] # For UI display (role, content)
        self.persistent_messages = [{"role": "system", "content": self.system_prompt}] # For LLM Context
        self.logs = []
        self.status = "SYSTEM_READY"
        self.loops_active = False
        self.current_loop = 0
        self.max_loops = 10
        self.start_time = datetime.now()

    def _init_layout(self):
        # ... (same as before)
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="chat", ratio=2),
            Layout(name="sidebar", ratio=1)
        )
        self.layout["sidebar"].split_column(
            Layout(name="stats", size=8),
            Layout(name="logs"),
            Layout(name="mandate", size=6)
        )

    # ... (other helper methods same as before)

    def _get_chat_panel(self):
        chat_content = ""
        # Show last 15 messages for a better chat feel
        for role, content in self.history[-15:]:
            if role == "user":
                chat_content += f"[bold green]USER > [/bold green]{content}\n"
            elif role == "assistant":
                clean_text = re.sub(r'<[^>]+>.*?</[^>]+>', '', content, flags=re.DOTALL).strip()
                if clean_text:
                    chat_content += f"[bold gold1]MERLIN > [/bold gold1]{clean_text}\n"
            elif role == "system_log":
                chat_content += f"[dim italic magenta]LOG: {content}[/dim italic magenta]\n"
        
        return Panel(chat_content, title="[bold cyan]NEURAL_LINK[/bold cyan]", border_style="cyan", padding=(1, 1))

    def _get_header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        grid.add_row(
            Text("🧙‍♂️ MERLIN_OS", style="bold gold1"),
            Text(f"COGNITIVE_PERSISTENCE: ON", style="bold green"),
            Text(datetime.now().strftime("%H:%M:%S"), style="bold magenta")
        )
        return Panel(grid, style="gold1", border_style="gold1")

    def _get_stats_panel(self):
        table = Table.grid(expand=True)
        uptime = str(datetime.now() - self.start_time).split(".")[0]
        table.add_row("[cyan]MODEL:[/cyan]", f"[white]{self.model}[/white]")
        table.add_row("[cyan]UPTIME:[/cyan]", f"[white]{uptime}[/white]")
        table.add_row("[cyan]CTX_LEN:[/cyan]", f"[white]{len(self.persistent_messages)} TURNS[/white]")
        table.add_row("[cyan]LOOPS:[/cyan]", f"[white]{self.current_loop}/{self.max_loops if self.loops_active else '-'}[/white]")
        return Panel(table, title="[bold cyan]SYSTEM_STATS[/bold cyan]", border_style="cyan")

    # ... (rest of helper methods remain mostly same, just updating run_task)

    def log(self, message):
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_task(self, task, live):
        self.status = "BUSY_THINKING"
        self.loops_active = True
        self.current_loop = 0
        self.history.append(("user", task))
        self.persistent_messages.append({"role": "user", "content": task})
        
        for i in range(self.max_loops):
            self.current_loop = i + 1
            self.status = f"LOOP_{i+1}_PROCESSING"
            self.refresh()
            
            try:
                response = self.client.chat.completions.create(model=self.model, messages=self.persistent_messages)
                content = response.choices[0].message.content or ""
                
                # Keep assistant content in persistent messages
                self.persistent_messages.append({"role": "assistant", "content": content})
                self.history.append(("assistant", content))
                
                # Parse tools
                pattern = r'<(p?)(?P<name>\w+)(?P<attrs>[^/>]*)(?:/>|>(?P<content>.*?)</(?P=name)>)'
                calls = []
                for match in re.finditer(pattern, content, re.DOTALL):
                    tool_name = match.group('name')
                    attrs_str = match.group('attrs')
                    inner = match.group('content').strip() if match.group('content') else ""
                    
                    if tool_name not in self.registry.tools and tool_name != "done":
                        continue
                    
                    params = {}
                    attr_pattern = r'(\w+)="([^"]*)"'
                    for attr_match in re.finditer(attr_pattern, attrs_str):
                        params[attr_match.group(1)] = attr_match.group(2)
                    
                    if inner:
                        if tool_name == "write_file": params["content"] = inner
                        elif tool_name == "run_shell_command" and not params.get("command"): params["command"] = inner
                    
                    calls.append((tool_name, params))

                if not calls:
                    self.status = "SYSTEM_READY"
                    break

                feedback = []
                for t_name, t_params in calls:
                    if t_name == "done":
                        self.status = "TASK_COMPLETED"
                        self.log(f"DONE: {t_params.get('summary', 'Complete')}")
                        self.refresh()
                        time.sleep(1)
                        self.loops_active = False
                        return

                    self.status = f"EXECUTING_{t_name.upper()}"
                    self.log(f"EXEC: {t_name}")
                    self.refresh()
                    
                    tool = self.registry.get_tool(t_name)
                    if tool:
                        res = tool.execute(**t_params)
                        if "error" in res:
                            self.log(f"ERROR: {t_name}")
                        
                        if t_name == "activate_skill" and "instructions" in res:
                            self.persistent_messages.append({"role": "system", "content": f"<activated_skill name=\"{t_params['skill_name']}\">{res['instructions']}</activated_skill>"})
                            self.log(f"SKILL_INJECTED: {t_params['skill_name']}")
                        
                        feedback.append(f"Tool {t_name} returned:\n{json.dumps(res, indent=2)}")
                    else:
                        feedback.append(f"Error: Tool {tool_name} not found.")

                if feedback:
                    self.persistent_messages.append({"role": "user", "content": "\n\n".join(feedback)})

            except Exception as e:
                self.status = "CORE_ERROR"
                self.log(f"FATAL: {str(e)}")
                self.refresh()
                time.sleep(3)
                break
        
        self.status = "SYSTEM_READY"
        self.loops_active = False
        self.refresh()

    def start_shell(self):
        self._init_layout()
        self.console.clear()
        
        with Live(self.layout, refresh_per_second=10, screen=True) as live:
            while True:
                self.refresh()
                live.stop()
                try:
                    # More conversational prompt
                    task = self.console.input("[bold gold1]YOU > [/bold gold1]")
                    if task.lower() in ["exit", "quit", "bye"]:
                        self.console.print("[bold red]Shutting down Merlin-OS...[/bold red]")
                        break
                    if task.lower() == "/clear":
                        self.persistent_messages = [{"role": "system", "content": self.system_prompt}]
                        self.history = []
                        self.log("CONTEXT_CLEARED")
                        live.start()
                        continue
                except KeyboardInterrupt:
                    break
                
                live.start()
                self.run_task(task, live)
