#!/usr/bin/env python3
"""
MERLIN-CLI: Sovereign Auto-Coding Agent
Tier-3 Intelligence Wrapper for OpenRouter Free-Tier Execution.
"""
import os
import sys
import argparse
from openai import OpenAI

SYSTEM_PROMPT = """You are MERLIN, a Tier-3 Sovereign Auto-Coding Agent.
You receive a coding task and the contents of relevant files.
You must output ONLY valid code blocks, file paths, or bash commands to solve the task.
No explanations. Pure execution. Grey Hat & Ihsan alignment.
"""

def main():
    parser = argparse.ArgumentParser(description="MERLIN-CLI: Sovereign Coding Agent")
    parser.add_argument("task", help="The coding task or directive to execute")
    parser.add_argument("-f", "--files", nargs="+", help="Target files to include as context")
    parser.add_argument("-m", "--model", default="deepseek/deepseek-coder-v2-lite:free", 
                        help="OpenRouter model (default: deepseek-coder-v2-lite:free)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("[MERLIN] Error: OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    context = ""
    if args.files:
        for f in args.files:
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    context += f"\n--- FILE: {f} ---\n{file.read()}\n"
            except Exception as e:
                context += f"\n--- FILE: {f} ---\n[Error reading: {e}]\n"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Task: {args.task}\n\nContext:\n{context}"}
    ]  # type: ignore

    print(f"[MERLIN] Executing via {args.model}...")
    try:
        response = client.chat.completions.create(
            model=args.model,
            messages=messages,
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()
    except Exception as e:
        print(f"[MERLIN] API Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
