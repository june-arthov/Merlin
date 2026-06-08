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
from rich.box import ROUNDED, DOUBLE
from ..tools import ToolRegistry

# ASCII ART Header
MERLIN_LOGO = """
[bold gold1]███╗   ███╗███████╗██████╗ ██╗     ██╗███╗   ██╗[/bold gold1]
[bold gold1]████╗ ████║██╔════╝██╔══██╗██║     ██║████╗  ██║[/bold gold1]
[bold white]██╔████╔██║█████╗  ██████╔╝██║     ██║██╔██╗ ██║[/bold white]
[bold white]██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║██║╚██╗██║[/bold white]
[bold cyan]██║ ╚═╝ ██║███████╗██║  ██║███████╗██║██║ ╚████║[/bold cyan]
[bold cyan]╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝[/bold cyan]
"""

class MerlinTUI:
    def __init__(self, model, api_key, system_prompt, registry, loader):
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={"HTTP-Referer": "https://github.com/june-arthov/Merlin", "X-Title": "MERLIN-OS-TUI"}
        )
        self.system_prompt = system_prompt
        self.registry = registry
        self.loader = loader # SkillLoader
        self.console = Console()
        self.layout = Layout()
        self.history = []
        self.persistent_messages = [{"role": "system", "content": self.system_prompt}]
        self.logs = []
        self.status = "SYSTEM_READY"
        self.loops_active = False
        self.current_loop = 0
        self.max_loops = 10
        self.start_time = datetime.now()
        self.token_usage = 0 # Dummy for now

    def _get_dashboard(self):
        # Build Tools Grid
        tools_table = Table.grid(expand=True)
        tools_table.add_column(ratio=1)
        
        # Group tools by category
        categories = {}
        for name, tool in self.registry.tools.items():
            cat = getattr(tool, 'category', 'general')
            if cat not in categories: categories[cat] = []
            categories[cat].append(name)
        
        for cat, tools in sorted(categories.items()):
            tools_table.add_row(f"[bold cyan]{cat}:[/bold cyan] [white]{', '.join(tools)}[/white]")

        # Build Skills Grid
        skills_table = Table.grid(expand=True)
        skills_table.add_column(ratio=1)
        # Skills are directory names in available_skills
        if self.loader.available_skills:
            # Grouping dummy for now, just list them
            skills_table.add_row(f"[bold magenta]available:[/bold magenta] [white]{', '.join(self.loader.available_skills.keys())}[/white]")
        else:
            skills_table.add_row("[dim]No specialized skills detected.[/dim]")

        # Sidebar Stats
        sidebar = Table.grid(expand=True, padding=(0, 1))
        sidebar.add_row(f"[bold white]{self.model}[/bold white]")
        sidebar.add_row(f"[dim]{os.getcwd()}[/dim]")
        sidebar.add_row(f"Session: [dim]{datetime.now().strftime('%Y%m%d_%H%M%S')}[/dim]")

        # Assemble Main Box
        main_grid = Table.grid(expand=True)
        main_grid.add_column(width=52) # Logo area
        main_grid.add_column(ratio=1) # Info area
        
        # ASCII Image
        logo_area = Text.from_markup(f"\n{MERLIN_LOGO}\n", justify="left")
        
        info_area = Table.grid(expand=True)
        info_area.add_row("[bold white]Available Tools[/bold white]")
        info_area.add_row(tools_table)
        info_area.add_row("")
        info_area.add_row("[bold white]Available Skills[/bold white]")
        info_area.add_row(skills_table)
        info_area.add_row("")
        info_area.add_row(f"[bold gold1]{len(self.registry.tools)} tools · {len(self.loader.available_skills)} skills · /help for commands[/bold gold1]")

        main_grid.add_row(logo_area, info_area)

        return Panel(main_grid, title=f"Merlin OS Agent v3.0.0 ({datetime.now().strftime('%Y.%m.%d')})", border_style="grey50", box=ROUNDED)

    def _get_status_bar(self):
        uptime = int((datetime.now() - self.start_time).total_seconds())
        # ctx_bar = "[████████░░░░]"
        ctx_bar = "[░░░░░░░░░░]" # Progress bar style
        status_line = f" ⚕ {self.model} │ ctx {len(self.persistent_messages)} │ {ctx_bar} -- │ {uptime}s │ ⏲ 0s"
        return Text(status_line, style="bold white on grey11")

    def show_startup(self):
        self.console.print(self._get_dashboard())
        self.console.print("\n[bold white]Welcome to Merlin OS! Type your command to initiate link, or /help for system manual.[/bold white]")
        self.console.print("✦ [dim]System Tip: Sovereign Node is active. Operating under deep-system directives.[/dim]\n")

    def run_task(self, task):
        self.history.append(("user", task))
        self.persistent_messages.append({"role": "user", "content": task})
        
        with Live(self._get_status_bar(), refresh_per_second=4, transient=True) as live:
            for i in range(self.max_loops):
                self.current_loop = i + 1
                try:
                    response = self.client.chat.completions.create(model=self.model, messages=self.persistent_messages)
                    content = response.choices[0].message.content or ""
                    self.persistent_messages.append({"role": "assistant", "content": content})
                    
                    # Print reasoning/content immediately
                    clean_text = re.sub(r'<[^>]+>.*?</[^>]+>', '', content, flags=re.DOTALL).strip()
                    if clean_text:
                        self.console.print(f"\n[bold gold1]MERLIN > [/bold gold1]{clean_text}")
                    elif "<" in content:
                        self.console.print("\n[dim italic]Neural processing... executing tools.[/dim italic]")

                    # Parse and exec tools
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

                    if not calls: break

                    feedback = []
                    for t_name, t_params in calls:
                        if t_name == "done":
                            self.console.print(f"\n[bold green]✔ MISSION ACCOMPLISHED:[/bold green] {t_params.get('summary', 'Task complete.')}")
                            return True
                        
                        self.console.print(f"\n[bold cyan]EXEC:[/bold cyan] [italic]{t_name}[/italic]")
                        tool = self.registry.get_tool(t_name)
                        if tool:
                            res = tool.execute(**t_params)
                            if t_name == "activate_skill" and "instructions" in res:
                                self.persistent_messages.append({"role": "system", "content": f"<activated_skill name=\"{t_params['skill_name']}\">{res['instructions']}</activated_skill>"})
                            feedback.append(f"Tool {t_name} returned:\n{json.dumps(res, indent=2)}")
                        else:
                            feedback.append(f"Error: Tool {t_name} not found.")

                    if feedback:
                        self.persistent_messages.append({"role": "user", "content": "\n\n".join(feedback)})

                except Exception as e:
                    self.console.print(f"[bold red]CRITICAL ERROR:[/bold red] {str(e)}")
                    break

    def start_shell(self):
        self.console.clear()
        self.show_startup()
        
        while True:
            try:
                self.console.print(self._get_status_bar())
                task = self.console.input("[bold cyan]❯ [/bold cyan]")
                
                if task.lower() in ["exit", "quit", "bye"]:
                    self.console.print("[bold red]Deactivating Merlin-OS...[/bold red]")
                    break
                if task.lower() == "/clear":
                    self.persistent_messages = [{"role": "system", "content": self.system_prompt}]
                    self.console.clear()
                    self.show_startup()
                    continue
                if not task.strip(): continue
                
                self.run_task(task)
                self.console.print("-" * self.console.width, style="grey15")
            except KeyboardInterrupt:
                break
