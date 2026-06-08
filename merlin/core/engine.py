import re
import json
import time
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.layout import Layout
from rich.table import Table
from rich.spinner import Spinner
from rich.status import Status
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
        self.layout = Layout()
        self.current_task = ""
        self.tool_logs = []

    def register_tool(self, tool):
        self.registry.register(tool)

    def _make_layout(self):
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )
        self.layout["main"].split_row(
            Layout(name="mission", ratio=2),
            Layout(name="sidebar", ratio=1),
        )
        self.layout["sidebar"].split_column(
            Layout(name="stats"),
            Layout(name="mandate"),
        )

    def _update_layout(self, loop, total, status_text="Ready"):
        # Header
        self.layout["header"].update(
            Panel(f"[bold gold1]MERLIN OS v3.0.0[/bold gold1] | Model: [dim]{self.model}[/dim] | Loop: {loop}/{total}", border_style="gold1")
        )
        
        # Mission Panel
        log_content = "\n".join(self.tool_logs[-5:]) if self.tool_logs else "[dim]Waiting for tool calls...[/dim]"
        self.layout["mission"].update(
            Panel(f"[bold green]TASK:[/bold green] {self.current_task}\n\n[bold cyan]RECENT LOGS:[/bold cyan]\n{log_content}", title="MISSION CONTROL", border_style="green")
        )

        # Stats Panel
        stats_table = Table.grid(expand=True)
        stats_table.add_column(style="cyan")
        stats_table.add_column(style="magenta", justify="right")
        stats_table.add_row("Status:", status_text)
        stats_table.add_row("Tools:", str(len(self.registry.tools)))
        stats_table.add_row("Memory:", "Active")
        self.layout["stats"].update(Panel(stats_table, title="SYSTEM STATS", border_style="cyan"))

        # Mandate Panel
        self.layout["mandate"].update(
            Panel("[dim][italic]Grey Hat & Ihsan\nZero Hallucination\nAutonomous Ops[/italic][/dim]", title="MANDATE", border_style="magenta")
        )

        # Footer
        self.layout["footer"].update(
            Panel(f"[bold white]STATUS:[/bold white] {status_text}", border_style="white")
        )

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

    def run(self, task, max_loops=10):
        self.current_task = task
        self.messages = [{"role": "system", "content": self.system_prompt}, {"role": "user", "content": task}]
        self._make_layout()

        with Live(self.layout, refresh_per_second=4, screen=True) as live:
            for i in range(max_loops):
                self._update_layout(i+1, max_loops, "Consulting Oracle...")
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages
                    )
                    content = response.choices[0].message.content or ""
                    self.messages.append({"role": "assistant", "content": content})
                    
                    calls = self._parse_tool_calls(content)
                    if not calls:
                        self.tool_logs.append("[yellow]No tool calls found. Awaiting input.[/yellow]")
                        self._update_layout(i+1, max_loops, "Idle")
                        time.sleep(2)
                        break

                    feedback = []
                    for tool_name, params in calls:
                        if tool_name == "done":
                            self.tool_logs.append(f"[bold green]DONE:[/bold green] {params.get('summary', 'Task complete.')}")
                            self._update_layout(i+1, max_loops, "Mission Accomplished")
                            time.sleep(3)
                            return True
                        
                        self._update_layout(i+1, max_loops, f"Executing {tool_name}...")
                        self.tool_logs.append(f"[bold cyan]EXEC:[/bold cyan] {tool_name}")
                        
                        tool = self.registry.get_tool(tool_name)
                        if tool:
                            result = tool.execute(**params)
                            if tool_name == "activate_skill" and "instructions" in result:
                                self.messages.append({"role": "system", "content": f"<activated_skill name=\"{params['skill_name']}\">{result['instructions']}</activated_skill>"})
                                self.tool_logs.append(f"[magenta]SKILL ACTIVATED:[/magenta] {params['skill_name']}")
                            
                            feedback.append(f"Tool {tool_name} returned:\n{json.dumps(result, indent=2)}")
                        else:
                            feedback.append(f"Error: Tool {tool_name} not found.")

                    if feedback:
                        self.messages.append({"role": "user", "content": "\n\n".join(feedback)})
                        
                except Exception as e:
                    self.tool_logs.append(f"[bold red]API ERROR:[/bold red] {str(e)}")
                    self._update_layout(i+1, max_loops, "Error")
                    time.sleep(5)
                    return False
        
        return False
