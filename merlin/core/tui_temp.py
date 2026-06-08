import os
import json
import re
import asyncio
from openai import AsyncOpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from ..tools import ToolRegistry

class MerlinTUI:
    def __init__(self, model, api_key, system_prompt, registry, loader):
        self.model = model
        self.client = AsyncOpenAI(
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

    async def start_shell(self):
        self.console.clear()
        self.console.print("[bold cyan]Merlin-CLI[/bold cyan] [dim]v3.0.0-Async[/dim]")
        self.console.print(f"[dim]Model: {self.model} | Mode: Radical Singularity (Streaming & Async)[/dim]\n")
        
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
                
                await self.run_task(task)
                self.console.print() # Empty line for spacing
            except KeyboardInterrupt:
                self.console.print()
                break
            except Exception as e:
                self.console.print(f"[bold red]Shell Error:[/bold red] {e}")

    async def run_task(self, task):
        self.persistent_messages.append({"role": "user", "content": task})
        
        for i in range(self.max_loops):
            content = ""
            
            self.console.print("[dim cyan]Oracle thinking...[/dim cyan]", end="\r")
            try:
                response = await self.client.chat.completions.create(
                    model=self.model, 
                    messages=self.persistent_messages,
                    stream=True
                )
                
                # Clear the thinking text
                self.console.print(" " * 20, end="\r")
                
                # Streaming loop
                for chunk in await response:
                    # Depending on library version, might be async for or normal for if it's an async generator
                    # Actually, AsyncOpenAI stream returns an async generator
                    pass
            except Exception as e:
                self.console.print(f"[bold red]API Error:[/bold red] {str(e)}")
                return
