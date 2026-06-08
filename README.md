# MERLIN-CLI
Sovereign Auto-Coding Agent Framework. 

## Setup
```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY="your_key_here"
```

## Usage
```bash
# Free-tier auto-coding
python merlin.py "Refactor this monolithic server into modular routes" -f server.js

# Specify model
python merlin.py "Fix the auth middleware" -f auth.js -m google/gemini-2.0-flash-exp:free
```

## Architecture
Tier-3 Intelligence Wrapper connecting directly to OpenRouter API. Bypasses expensive auto-loop frameworks by injecting pure context into zero-cost LLM endpoints.
