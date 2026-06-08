#!/usr/bin/env python3
"""
MERLIN-CLI: Sovereign Auto-Coding Agent
Tier-3 Intelligence Wrapper with Autonomous Execution Loop (FIT).
"""
import os
import sys
import re
import argparse
import subprocess
from openai import OpenAI

SYSTEM_PROMPT = """You are MERLIN, a Tier-3 Sovereign Auto-Coding Agent.
You operate in an autonomous execution loop to complete coding tasks.
You must use the following XML tags to execute actions. Do not use markdown code blocks for file creation.

1. To create or overwrite a file:
<write_file path="relative/path/to/file">
file content here
</write_file>

2. To execute a shell command (e.g., install deps, run tests, check errors):
<run_cmd>
command here
</run_cmd>

3. When the task is fully complete, verified, and tested:
<done>
Final summary of what was accomplished.
</done>

RULES:
- Output ONLY the XML tags and brief reasoning.
- If a <run_cmd> fails, read the error output provided in the next prompt and fix it.
- Do not hallucinate command outputs. Wait for the system to provide them.
- Grey Hat & Ihsan alignment. Absolute precision. Zero-tolerance for errors.
"""

def parse_actions(text):
    """Extract XML actions from LLM output."""
    actions = []
    # Parse write_file
    for match in re.finditer(r'<write_file path="([^"]+)">(.*?)</write_file>', text, re.DOTALL):
        actions.append(("write", match.group(1).strip(), match.group(2)))
    # Parse run_cmd
    for match in re.finditer(r'<run_cmd>(.*?)</run_cmd>', text, re.DOTALL):
        actions.append(("run", match.group(1).strip(), None))
    # Parse done
    if re.search(r'<done>', text, re.DOTALL):
        done_match = re.search(r'<done>(.*?)</done>', text, re.DOTALL)
        summary = done_match.group(1).strip() if done_match else "Task complete."
        actions.append(("done", summary, None))
    return actions

def execute_action(action_type, target, content, cwd):
    """Execute a parsed action and return feedback string."""
    if action_type == "write":
        # Security: Prevent directory traversal outside CWD
        abs_path = os.path.abspath(os.path.join(cwd, target))
        if not abs_path.startswith(os.path.abspath(cwd)):
            return f"[SYSTEM ERROR] Blocked directory traversal attempt: {target}"
        
        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"[SYSTEM] Successfully wrote {len(content)} bytes to {target}"
        except Exception as e:
            return f"[SYSTEM ERROR] Failed to write {target}: {e}"

    elif action_type == "run":
        print(f"[MERLIN EXEC] $ {target}")
        try:
            result = subprocess.run(
                target, shell=True, cwd=cwd, 
                capture_output=True, text=True, timeout=120
            )
            output = result.stdout + "\n" + result.stderr
            # Truncate massive outputs to prevent context overflow
            if len(output) > 4000:
                output = output[:2000] + "\n...[TRUNCATED]...\n" + output[-2000:]
            return f"[SYSTEM CMD EXIT CODE: {result.returncode}]\n{output.strip()}"
        except subprocess.TimeoutExpired:
            return "[SYSTEM ERROR] Command timed out after 120 seconds."
        except Exception as e:
            return f"[SYSTEM ERROR] Execution failed: {e}"
            
    return ""

def main():
    parser = argparse.ArgumentParser(description="MERLIN-CLI: Sovereign Auto-Coding Agent")
    parser.add_argument("task", help="The coding task or directive to execute")
    parser.add_argument("-f", "--files", nargs="+", help="Target files to include as initial context")
    parser.add_argument("-m", "--model", default="deepseek/deepseek-coder-v2-lite:free", 
                        help="OpenRouter model (default: deepseek-coder-v2-lite:free)")
    parser.add_argument("--auto", action="store_true", help="Enable autonomous execution loop (FIT)")
    parser.add_argument("--max-loops", type=int, default=5, help="Max iterations for auto mode")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("[MERLIN] Error: OPENROUTER_API_KEY environment variable not set.")
        sys.exit(1)

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "https://github.com/june-arthov/Merlin",
            "X-Title": "MERLIN-CLI"
        }
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
        {"role": "user", "content": f"Task: {args.task}\n\nInitial Context:\n{context}"}
    ]

    print(f"[MERLIN] Initializing via {args.model}...")
    
    if not args.auto:
        # Standard One-Shot Mode
        try:
            response = client.chat.completions.create(
                model=args.model, messages=messages, stream=True # type: ignore
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print()
        except Exception as e:
            print(f"[MERLIN] API Error: {e}")
            sys.exit(1)
        return

    # Autonomous Execution Loop (FIT)
    print("[MERLIN] Autonomous Execution Loop ENGAGED. (Max Loops: %d)" % args.max_loops)
    cwd = os.getcwd()
    
    for i in range(args.max_loops):
        print(f"\n[MERLIN] Loop {i+1}/{args.max_loops} - Consulting the Oracle...")
        try:
            response = client.chat.completions.create(
                model=args.model, messages=messages # type: ignore
            )
            content = response.choices[0].message.content or ""
            messages.append({"role": "assistant", "content": content})
            
            # Print LLM reasoning (strip XML tags for cleaner console output)
            reasoning = re.sub(r'<(write_file|run_cmd|done)[^>]*>.*?</\1>', '', content, flags=re.DOTALL).strip()
            if reasoning:
                print(f"[MERLIN REASONING] {reasoning}")

            actions = parse_actions(content)
            if not actions:
                print("[MERLIN] No actionable tags found. Awaiting further directives.")
                break

            feedback = []
            for action_type, target, payload in actions:
                if action_type == "done":
                    print(f"\n[MERLIN] Task Complete: {target}")
                    sys.exit(0)
                
                result = execute_action(action_type, target, payload, cwd)
                if result:
                    feedback.append(result)
                    print(result.split('\n')[0]) # Print first line of feedback

            if feedback:
                # Feed results back to LLM
                messages.append({
                    "role": "user", 
                    "content": f"[SYSTEM FEEDBACK]\n" + "\n".join(feedback) + "\n\nProceed with the next steps or output <done> if finished."
                })

        except Exception as e:
            print(f"[MERLIN] API Error: {e}")
            sys.exit(1)

    print("\n[MERLIN] Max loops reached. Manual intervention required.")

if __name__ == "__main__":
    main()
