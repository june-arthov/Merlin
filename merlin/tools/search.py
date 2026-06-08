import os
import re
from .base import BaseTool

class GrepSearch(BaseTool):
    @property
    def name(self): return "grep_search"
    @property
    def category(self): return "search"
    @property
    def description(self): return "Searches for a pattern in files within a directory."
    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern to search for."},
                "dir_path": {"type": "string", "description": "Directory to search in."},
                "include_pattern": {"type": "string", "description": "Glob pattern for files to include."}
            },
            "required": ["pattern"]
        }
    def execute(self, pattern, dir_path=".", include_pattern="*"):
        results = []
        try:
            regex = re.compile(pattern)
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if not re.search(include_pattern.replace("*", ".*"), file): continue
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for i, line in enumerate(f):
                                if regex.search(line):
                                    results.append({"file": file_path, "line": i + 1, "content": line.strip()})
                                if len(results) > 100: return {"results": results, "status": "truncated"}
                    except Exception: continue
            return {"results": results}
        except Exception as e: return {"error": str(e)}
