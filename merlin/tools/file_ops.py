import os
import fnmatch
import glob
from .base import BaseTool

class ReadFile(BaseTool):
    # ... (existing ReadFile)
    @property
    def name(self):
        return "read_file"

    @property
    def description(self):
        return "Reads a file and returns its content. Supports line ranges."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file."},
                "start_line": {"type": "integer", "description": "1-based start line."},
                "end_line": {"type": "integer", "description": "1-based end line."}
            },
            "required": ["file_path"]
        }

    def execute(self, file_path, start_line=None, end_line=None):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = (start_line - 1) if start_line else 0
            end = end_line if end_line else len(lines)
            
            content = "".join(lines[start:end])
            return {"content": content, "total_lines": len(lines)}
        except Exception as e:
            return {"error": str(e)}

class ListDirectory(BaseTool):
    # ... (existing ListDirectory)
    @property
    def name(self):
        return "list_directory"

    @property
    def description(self):
        return "Lists files and directories in a given path."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "dir_path": {"type": "string", "description": "Path to list."}
            },
            "required": ["dir_path"]
        }

    def execute(self, dir_path):
        try:
            items = os.listdir(dir_path)
            result = []
            for item in items:
                full_path = os.path.join(dir_path, item)
                is_dir = os.path.isdir(full_path)
                result.append({"name": item, "type": "directory" if is_dir else "file"})
            return {"items": result}
        except Exception as e:
            return {"error": str(e)}

class Replace(BaseTool):
    @property
    def name(self):
        return "replace"

    @property
    def description(self):
        return "Replaces a specific string in a file. Use this for surgical edits."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file."},
                "old_string": {"type": "string", "description": "Exact text to replace."},
                "new_string": {"type": "string", "description": "New text to insert."},
                "allow_multiple": {"type": "boolean", "description": "Allow multiple replacements."}
            },
            "required": ["file_path", "old_string", "new_string"]
        }

    def execute(self, file_path, old_string, new_string, allow_multiple=False):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            count = content.count(old_string)
            if count == 0:
                return {"error": "old_string not found in file."}
            if count > 1 and not allow_multiple:
                return {"error": f"old_string found {count} times. Set allow_multiple=True to replace all."}
            
            new_content = content.replace(old_string, new_string)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {"status": "success", "replacements": count}
        except Exception as e:
            return {"error": str(e)}

class Glob(BaseTool):
    @property
    def name(self):
        return "glob"

    @property
    def description(self):
        return "Finds files matching a pattern (e.g., **/*.py)."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern."}
            },
            "required": ["pattern"]
        }

    def execute(self, pattern):
        try:
            files = glob.glob(pattern, recursive=True)
            return {"files": files}
        except Exception as e:
            return {"error": str(e)}
