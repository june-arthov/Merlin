# MERLIN-CLI
Sovereign Auto-Coding Agent Framework. 

## Setup
```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY="your_key_here"
```

## Usage

### Standard Mode (One-Shot)
```bash
python merlin.py "Refactor this monolithic server into modular routes" -f server.js
```

### Autonomous Mode (Execution Loop)
Engage the FIT (File-modify, Inspect, Test) loop. MERLIN will write files, run commands, read the errors, and fix them autonomously.
```bash
# Max 5 loops (default) using free tier
python merlin.py --auto "Setup a basic Express server with auth and write tests"

# Limit to 3 loops to save tokens
python merlin.py --auto --max-loops 3 "Fix the failing test in auth.js" -f auth.js

# Use a paid model for complex architecture
python merlin.py --auto -m anthropic/claude-3.5-sonnet "Build a full Next.js dashboard"
```

## Architecture
Tier-3 Intelligence Wrapper connecting directly to OpenRouter API. 
The `--auto` flag activates a sovereign execution loop:
1. **Generate**: LLM outputs structured XML (`<write_file>`, `<run_cmd>`, `<done>`).
2. **Execute**: Python engine parses and safely executes actions in the local directory.
3. **Inspect**: `stdout` and `stderr` from commands are captured.
4. **Adapt**: Errors are fed back to the LLM for self-correction.
5. **Terminate**: Loop ends when LLM outputs `<done>` or max loops are reached.
