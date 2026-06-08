import os

def load_project_instructions():
    """Loads MERLIN.md from current or parent directories."""
    cwd = os.getcwd()
    while True:
        path = os.path.join(cwd, "MERLIN.md")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    return None

def load_memory():
    """Loads MEMORY.md (private)."""
    # For now, just look in current dir or a specific home dir
    path = os.path.expanduser("~/.merlin/MEMORY.md")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def load_manifesto():
    """Loads MERLIN_MANIFESTO.md from the root."""
    path = "MERLIN_MANIFESTO.md"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None
