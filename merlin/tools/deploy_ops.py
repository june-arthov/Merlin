import subprocess
from .base import BaseTool

class DockerManager(BaseTool):
    @property
    def name(self): return "docker_manager"
    @property
    def category(self): return "devops"
    @property
    def description(self): return "Manages Docker containers and images."
    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["build", "up", "down", "ps", "logs", "restart"]},
                "target": {"type": "string"}, "args": {"type": "string"}
            },
            "required": ["action"]
        }
    def execute(self, action, target=None, args=""):
        cmd = f"docker {action} {target if target else ''} {args}"
        if action == "up": cmd = f"docker-compose up -d {target if target else ''} {args}"
        elif action == "down": cmd = f"docker-compose down {args}"
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            return {"command": cmd, "exit_code": res.returncode, "stdout": res.stdout.strip(), "stderr": res.stderr.strip()}
        except Exception as e: return {"error": str(e)}

class SSHExec(BaseTool):
    @property
    def name(self): return "ssh_exec"
    @property
    def category(self): return "devops"
    @property
    def description(self): return "Executes command on remote server via SSH."
    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {"host": {"type": "string"}, "command": {"type": "string"}, "identity_file": {"type": "string"}},
            "required": ["host", "command"]
        }
    def execute(self, host, command, identity_file=None):
        ssh_cmd = f"ssh -o BatchMode=yes -o StrictHostKeyChecking=no"
        if identity_file: ssh_cmd += f" -i {identity_file}"
        full_cmd = f'{ssh_cmd} {host} "{command}"'
        try:
            res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=120)
            return {"host": host, "exit_code": res.returncode, "output": (res.stdout + "\n" + res.stderr).strip()}
        except Exception as e: return {"error": str(e)}
