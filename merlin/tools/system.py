import os
import subprocess
from .base import BaseTool

class RunShellCommand(BaseTool):
    @property
    def name(self): return "run_shell_command"
    
    @property
    def category(self): return "system"
    
    @property
    def description(self): return "Executes a shell command and returns stdout/stderr."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command to execute."},
                "cwd": {"type": "string", "description": "Working directory."},
                "is_background": {"type": "boolean", "description": "Run in background."}
            },
            "required": ["command"]
        }

    def execute(self, command, cwd=None, is_background=False):
        try:
            if is_background:
                # Run in background without waiting
                process = subprocess.Popen(
                    command, shell=True, cwd=cwd or os.getcwd(),
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                return {
                    "status": "background process started",
                    "pid": process.pid,
                    "command": command
                }
            else:
                result = subprocess.run(
                    command, shell=True, cwd=cwd or os.getcwd(),
                    capture_output=True, text=True, timeout=300
                )
                output = result.stdout + "\n" + result.stderr
                return {
                    "exit_code": result.returncode,
                    "output": output.strip()
                }
        except Exception as e:
            return {"error": str(e)}

class WriteFile(BaseTool):
    @property
    def name(self): return "write_file"
    
    @property
    def category(self): return "system"
    
    @property
    def description(self): return "Writes content to a file, creating directories if needed."

    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file."},
                "content": {"type": "string", "description": "Content to write."}
            },
            "required": ["file_path", "content"]
        }

    def execute(self, file_path, content):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"status": "success", "bytes": len(content)}
        except Exception as e:
            return {"error": str(e)}
