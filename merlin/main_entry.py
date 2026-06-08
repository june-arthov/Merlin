#!/usr/bin/env python3
import os
import sys
import argparse
from merlin.core.engine import MerlinEngine
from merlin.core.prompts import build_system_prompt
from merlin.core.skills import SkillLoader
from merlin.tools import (
    ToolRegistry, RunShellCommand, WriteFile, ReadFile, ListDirectory, GrepSearch,
    Replace, Glob, UpdateMemory, UpdateProjectInstructions, Plan
)
from merlin.tools.skills_tool import ActivateSkill
from merlin.tools.orchestration import InvokeAgent
from merlin.utils.context import load_project_instructions, load_memory, load_manifesto

def main_cli():
    parser = argparse.ArgumentParser(description="MERLIN-CLI Tier-3 Sovereign Agent")
    parser.add_argument("task", nargs="?", help="Task to execute")
    parser.add_argument("-m", "--model", default="deepseek/deepseek-coder-v2-lite:free", help="LLM Model")
    parser.add_argument("--loops", type=int, default=10, help="Max execution loops")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set.")
        sys.exit(1)

    # Initialize Registry and Tools
    registry = ToolRegistry()
    registry.register(RunShellCommand())
    registry.register(WriteFile())
    registry.register(ReadFile())
    registry.register(ListDirectory())
    registry.register(GrepSearch())
    registry.register(Replace())
    registry.register(Glob())
    registry.register(UpdateMemory())
    registry.register(UpdateProjectInstructions())
    registry.register(Plan())
    registry.register(GoogleSearch())
    registry.register(WebFetch())
    registry.register(DockerManager())
    registry.register(SSHExec())

    # Load Skills
    loader = SkillLoader(registry)
    loader.load_skills(".merlin/skills")
    # Also load from global location if exists
    loader.load_skills(os.path.expanduser("~/.merlin/skills"))

    # Register Special Tools
    registry.register(ActivateSkill(loader))
    registry.register(InvokeAgent(args.model, api_key))


    # Load Context
    instructions = load_project_instructions()
    memory = load_memory()
    manifesto = load_manifesto()
    
    system_prompt = build_system_prompt(registry)
    if instructions:
        system_prompt += f"\n\n## Project Instructions (MERLIN.md)\n{instructions}"
    if memory:
        system_prompt += f"\n\n## Private Memory (MEMORY.md)\n{memory}"
    if manifesto:
        system_prompt += f"\n\n## Ethical Guardrails (MERLIN_MANIFESTO.md)\n{manifesto}"

    engine = MerlinEngine(args.model, api_key, system_prompt)
    # Re-register tools in engine (it uses its own registry internally, but let's sync)
    engine.registry = registry 

    task = args.task
    if not task:
        print("Merlin-CLI Tier-3 Active. Enter your task:")
        task = input("> ")

    print(f"[MERLIN] Model: {args.model}")
    engine.run(task, max_loops=args.loops)
